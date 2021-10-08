from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import UserViewSet

user_router = DefaultRouter()
user_router.register('users', UserViewSet, basename='Users')


urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(user_router.urls)),
]
