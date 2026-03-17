from django.contrib import admin
from .models import Category, Account, Tag, Transaction


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "user", "color", "created_at")
    list_filter = ("type", "created_at")
    search_fields = ("name", "user__email", "user__username", "user__first_name", "user__last_name")
    ordering = ("name",)


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "initial_balance", "created_at")
    list_filter = ("created_at",)
    search_fields = ("name", "user__email", "user__username", "user__first_name", "user__last_name")
    ordering = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "user")
    search_fields = ("name", "user__email", "user__username", "user__first_name", "user__last_name")
    ordering = ("name",)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "description",
        "type",
        "amount",
        "user",
        "category",
        "account",
        "date",
        "tag_list",
        "created_at",
    )
    list_filter = (
        "type",
        "category",
        "account",
        "date",
        "created_at",
    )
    search_fields = (
        "description",
        "notes",
        "user__email",
        "user__username",
        "user__first_name",
        "user__last_name",
        "category__name",
        "account__name",
        "tags__name",
    )
    autocomplete_fields = ("user", "category", "account", "tags")
    date_hierarchy = "date"
    ordering = ("-date", "-created_at")

    def tag_list(self, obj):
        return ", ".join(tag.name for tag in obj.tags.all())

    tag_list.short_description = "Tags"