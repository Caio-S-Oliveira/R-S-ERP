from django.contrib import admin
from django.urls import path, include
from apps.dashboard.views import home

urlpatterns = [
    path("admin/", admin.site.urls),
    path("users/", include("apps.users.urls")),
    path("accounts/", include("allauth.urls")),
    path("finance/", include("apps.finance.urls")),
    path("health/", include("apps.health.urls")),
    path("shopping/", include("apps.shopping.urls")),
    path("dashboard/", include("apps.dashboard.urls")),
    path("core/", include("apps.core.urls")),
    path("", home, name="home"),
]