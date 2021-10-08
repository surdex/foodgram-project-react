from django.contrib import admin
from django.contrib.auth import get_user_model

from users.models import Follow

User = get_user_model()


class UserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'username', 'email', 'first_name',
                    'last_name', 'is_staff')
    search_fields = ('username', 'email')
    list_filter = ('is_staff', )
    empty_value_display = '-empty-'


class FollowAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author')
    search_fields = ('user', 'author')
    list_filter = ('author', )
    empty_value_display = '-empty-'


admin.site.register(User, UserAdmin)
admin.site.register(Follow, FollowAdmin)
