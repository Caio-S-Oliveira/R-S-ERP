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
    path("checkins/", views.daily_checkin_list, name="daily_checkin_list"),
    path("checkins/novo/", views.daily_checkin_create, name="daily_checkin_create"),
    path("checkins/<int:pk>/editar/", views.daily_checkin_update, name="daily_checkin_update"),
]