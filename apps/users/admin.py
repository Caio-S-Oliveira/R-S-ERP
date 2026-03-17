from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User

    list_display = ("email", "username", "first_name", "last_name", "is_staff")
    search_fields = ("email", "username", "first_name", "last_name")
    ordering = ("email",)

    fieldsets = UserAdmin.fieldsets + (
        ("Informações extras", {
            "fields": ("avatar", "bio"),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Informações extras", {
            "fields": ("email", "avatar", "bio"),
        }),
    )