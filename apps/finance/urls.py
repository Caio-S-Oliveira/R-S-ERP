from django.urls import path
from . import views

urlpatterns = [
    path("finance_home/", views.finance_home, name="finance_home"),
    path("transactions/", views.transaction_list, name="transaction_list"),
    path("transactions/new/", views.transaction_create, name="transaction_create"),
    path("categories/", views.category_list, name="category_list"),
    path("categories/new/", views.category_create, name="category_create"),
    path("categories/<int:pk>/edit/", views.category_update, name="category_update"),
    path("categories/<int:pk>/delete/", views.category_delete, name="category_delete"),

    path("accounts/", views.account_list, name="account_list"),
    path("accounts/new/", views.account_create, name="account_create"),
    path("accounts/<int:pk>/edit/", views.account_update, name="account_update"),
    path("accounts/<int:pk>/delete/", views.account_delete, name="account_delete"),

    path("tags/", views.tag_list, name="tag_list"),
    path("tags/new/", views.tag_create, name="tag_create"),
    path("tags/<int:pk>/edit/", views.tag_update, name="tag_update"),
    path("tags/<int:pk>/delete/", views.tag_delete, name="tag_delete"),
]