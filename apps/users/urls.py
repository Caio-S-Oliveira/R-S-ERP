from django.contrib import admin
from django.urls import path, include
from apps.users.views import profile_view, edit_profile_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("profile/", profile_view, name="user_profile"),
    path("profile/edit/", edit_profile_view, name="edit_profile"),
]