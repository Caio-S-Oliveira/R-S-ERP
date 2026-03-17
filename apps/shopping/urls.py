from django.urls import path
from . import views

urlpatterns = [
    path("", views.shopping_list_list, name="shopping_list_list"),
    path("new/", views.shopping_list_create, name="shopping_list_create"),
    path("<int:pk>/", views.shopping_list_detail, name="shopping_list_detail"),
    path("<int:pk>/edit/", views.shopping_list_update, name="shopping_list_update"),
    path("<int:pk>/delete/", views.shopping_list_delete, name="shopping_list_delete"),

    path("<int:list_pk>/items/new/", views.shopping_item_create, name="shopping_item_create"),
    path("items/<int:pk>/edit/", views.shopping_item_update, name="shopping_item_update"),
    path("items/<int:pk>/delete/", views.shopping_item_delete, name="shopping_item_delete"),
    path("items/<int:pk>/status/<str:status>/", views.shopping_item_change_status, name="shopping_item_change_status"),
]