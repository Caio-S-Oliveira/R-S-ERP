from django.urls import path

from . import views

app_name = "apps.health"

urlpatterns = [
    path("", views.home, name="home"),
    path("perfil/", views.profile_update, name="profile_update"),
    path("avaliacoes/", views.assessment_list, name="assessment_list"),
    path("avaliacoes/nova/", views.assessment_create, name="assessment_create"),
    path("avaliacoes/<int:pk>/", views.assessment_detail, name="assessment_detail"),
    path("avaliacoes/<int:pk>/editar/", views.assessment_update, name="assessment_update"),
    path("metas/nova/", views.goal_create, name="goal_create"),
    path("metas/<int:pk>/editar/", views.goal_update, name="goal_update"),
]