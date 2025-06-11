from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser
from .forms import RegisterForm


# Custom Admin interface for CustomUser model.
class CustomUserAdmin(BaseUserAdmin):

    # Form to use for adding new users in the admin.
    add_form = RegisterForm

    # The form to use for changing existing users in the admin
    # TODO: Look at this more in detail, be aware of the Password Change confimation
    form = RegisterForm

    # List view of users in the admin panel and the search fields
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'is_superuser', 'date_joined',)
    list_filter = ('is_active', 'is_superuser', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

    # Fieldsets for editing an existing user
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'address', 'city', 'zip_code')}),
        ('Permissions', {'fields': ('is_active', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    # Fieldsets for adding a new user via Admin Panel
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'address', 'city', 'zip_code', 'password',),
        }),
    )
    filter_horizontal = ('groups', 'user_permissions',)


admin.site.register(CustomUser, CustomUserAdmin)