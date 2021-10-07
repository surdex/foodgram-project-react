from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Count, Exists, OuterRef
from django.utils.translation import gettext_lazy as _

from djoser import signals
from djoser.conf import settings
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .mixins import CreateListRetrieveModelViewSet
from .models import Follow
from .serializers import SubscribeUserSerializer

User = get_user_model()


class UserViewSet(CreateListRetrieveModelViewSet):
    serializer_class = settings.SERIALIZERS.user
    permission_classes = settings.PERMISSIONS.user
    token_generator = default_token_generator
    lookup_field = settings.USER_ID_FIELD
    pagination_class = PageNumberPagination

    def get_queryset(self):
        if self.action in ('subscriptions', 'subscribe'):
            queryset = User.objects.filter(
                following__user=self.request.user
            ).annotate(recipes_count=Count('recipes'))
        else:
            queryset = User.objects.annotate(
                is_subscribed=Exists(
                    Follow.objects.filter(
                        user=self.request.user.pk, author=OuterRef('pk')
                    )
                )
            ).order_by('pk')
        return queryset

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = settings.PERMISSIONS.user_create
        elif self.action == 'list':
            self.permission_classes = settings.PERMISSIONS.user_list
        elif self.action == 'set_password':
            self.permission_classes = settings.PERMISSIONS.set_password
        elif self.action in ('subscriptions', 'subscribe'):
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return settings.SERIALIZERS.user_create
        elif self.action == 'set_password':
            return settings.SERIALIZERS.set_password
        elif self.action == 'me':
            return settings.SERIALIZERS.current_user
        elif self.action in ('subscriptions', 'subscribe'):
            return SubscribeUserSerializer
        return self.serializer_class

    def get_instance(self):
        return self.request.user

    def perform_create(self, serializer):
        user = serializer.save()
        signals.user_registered.send(
            sender=self.__class__, user=user, request=self.request
        )

    @action(methods=['get'], detail=False)
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)

    @action(methods=['post'], detail=False)
    def set_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.request.user.set_password(
            serializer.validated_data['new_password']
        )
        self.request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get', 'delete'], detail=True)
    def subscribe(self, request, id):
        author = get_object_or_404(User, pk=id)
        if self.request.method == 'GET':
            if request.user == author:
                return Response(
                    {'errors': _('You can\'t subscribe to yourself')},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if Follow.objects.filter(
                user=request.user, author=author
            ).exists():
                return Response(
                    {'errors': _('You are already subscribed to this author')},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Follow.objects.create(
                user=request.user, author=author
            )
            serializer = self.get_serializer(self.get_object())
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif self.request.method == 'DELETE':
            if not Follow.objects.filter(
                user=request.user, author=author
            ).exists():
                return Response(
                    {'errors': _('You aren\'t subscribed to this author')},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Follow.objects.get(user=request.user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': _('Unknown error')},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=False)
    def subscriptions(self, request):
        return self.list(request)
