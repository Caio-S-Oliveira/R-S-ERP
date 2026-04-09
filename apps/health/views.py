from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from datetime import timedelta

from django.db.models import Avg, Count
from django.utils import timezone
from .forms import FitnessGoalForm, FitnessProfileForm, PhysicalAssessmentForm, DailyCheckinForm
from .models import (
    FitnessGoal,
    DailyCheckin,
    FitnessProfile,
    PhysicalAssessment,
    calcular_delta,
    calcular_lifestyle_score,
)
from .services import gerar_plano_metabolico, preencher_dados_avaliacao

def map_feeling_score(value):
    if value is None:
        return None

    value = str(value).strip().lower()

    mapping = {
        "péssimo": 1,
        "pessimo": 1,
        "ruim": 2,
        "mal": 2,
        "ok": 3,
        "normal": 3,
        "bem": 4,
        "bom": 4,
        "ótimo": 5,
        "otimo": 5,
        "excelente": 5,
    }

    return mapping.get(value)

@login_required
def home(request):
    profile, _ = FitnessProfile.objects.get_or_create(user=request.user)

    assessments_qs = (
        PhysicalAssessment.objects
        .filter(user=request.user)
        .select_related("metabolic_plan")
        .order_by("-data_avaliacao", "-id")
    )

    checkins_qs = (
        DailyCheckin.objects
        .filter(user=request.user)
        .order_by("-data", "-id")
    )

    latest_assessment = assessments_qs.first()
    previous_assessment = assessments_qs[1] if assessments_qs.count() > 1 else None

    active_goals = FitnessGoal.objects.filter(
        user=request.user,
        status="ativa"
    ).order_by("data_limite", "created_at")

    recent_assessments = assessments_qs[:5]
    recent_checkins = checkins_qs[:7]

    chart_assessments = list(
        assessments_qs.order_by("data_avaliacao", "id")[:12]
    )

    # Últimos 7 dias
    today = timezone.localdate()
    start_7d = today - timedelta(days=6)

    last_7d_checkins = (
        DailyCheckin.objects
        .filter(user=request.user, data__range=[start_7d, today])
        .order_by("data", "id")
    )

    latest_checkin = checkins_qs.first()

    peso_delta = calcular_delta(
        getattr(latest_assessment, "peso", None),
        getattr(previous_assessment, "peso", None),
    )
    gordura_delta = calcular_delta(
        getattr(latest_assessment, "percentual_gordura", None),
        getattr(previous_assessment, "percentual_gordura", None),
    )
    cintura_delta = calcular_delta(
        getattr(latest_assessment, "cintura", None),
        getattr(previous_assessment, "cintura", None),
    )

    lifestyle_score = calcular_lifestyle_score(latest_assessment)

    # Métricas 7 dias baseadas nos check-ins
    avg_sleep_7d = last_7d_checkins.aggregate(avg=Avg("horas_sono"))["avg"]
    avg_water_7d = last_7d_checkins.aggregate(avg=Avg("consumo_agua_litros"))["avg"]
    humor_scores = [map_feeling_score(c.humor) for c in last_7d_checkins]
    energia_scores = [map_feeling_score(c.energia) for c in last_7d_checkins]

    humor_scores_valid = [v for v in humor_scores if v is not None]
    energia_scores_valid = [v for v in energia_scores if v is not None]

    avg_humor_7d = (
        sum(humor_scores_valid) / len(humor_scores_valid)
        if humor_scores_valid else None
    )

    avg_energia_7d = (
        sum(energia_scores_valid) / len(energia_scores_valid)
        if energia_scores_valid else None
    )
    total_checkins_7d = last_7d_checkins.count()

    # Se teu cálculo de lifestyle score for por avaliação apenas, usa a última avaliação.
    # Se quiser uma média dos últimos check-ins, depois a gente refatora isso direito.
    lifestyle_score_7d = lifestyle_score

    chart_labels = [a.data_avaliacao.strftime("%d/%m/%Y") for a in chart_assessments]
    chart_peso = [float(a.peso) if a.peso is not None else None for a in chart_assessments]
    chart_gordura = [float(a.percentual_gordura) if a.percentual_gordura is not None else None for a in chart_assessments]
    chart_cintura = [float(a.cintura) if a.cintura is not None else None for a in chart_assessments]
    chart_sono = [float(a.horas_sono) if a.horas_sono is not None else None for a in chart_assessments]
    chart_agua = [float(a.consumo_agua_litros) if a.consumo_agua_litros is not None else None for a in chart_assessments]

    # Gráficos dos check-ins dos últimos 7 dias
    checkin_chart_labels = [c.data.strftime("%d/%m") for c in last_7d_checkins]
    checkin_chart_sleep = [
        float(c.horas_sono) if c.horas_sono is not None else None
        for c in last_7d_checkins
    ]
    checkin_chart_water = [
        float(c.consumo_agua_litros) if c.consumo_agua_litros is not None else None
        for c in last_7d_checkins
    ]
    checkin_chart_humor = [map_feeling_score(c.humor) for c in last_7d_checkins]
    checkin_chart_energia = [map_feeling_score(c.energia) for c in last_7d_checkins]

    context = {
        "profile": profile,
        "latest_assessment": latest_assessment,
        "previous_assessment": previous_assessment,
        "latest_checkin": latest_checkin,
        "active_goals": active_goals,
        "recent_assessments": recent_assessments,
        "recent_checkins": recent_checkins,
        "total_assessments": assessments_qs.count(),
        "total_checkins": checkins_qs.count(),

        "peso_delta": peso_delta,
        "gordura_delta": gordura_delta,
        "cintura_delta": cintura_delta,
        "lifestyle_score": lifestyle_score,

        "lifestyle_score_7d": lifestyle_score_7d,
        "avg_sleep_7d": avg_sleep_7d,
        "avg_water_7d": avg_water_7d,
        "avg_humor_7d": avg_humor_7d,
        "avg_energia_7d": avg_energia_7d,
        "total_checkins_7d": total_checkins_7d,

        "chart_labels": chart_labels,
        "chart_peso": chart_peso,
        "chart_gordura": chart_gordura,
        "chart_cintura": chart_cintura,
        "chart_sono": chart_sono,
        "chart_agua": chart_agua,

        "checkin_chart_labels": checkin_chart_labels,
        "checkin_chart_sleep": checkin_chart_sleep,
        "checkin_chart_water": checkin_chart_water,
        "checkin_chart_humor": checkin_chart_humor,
        "checkin_chart_energia": checkin_chart_energia,
    }
    return render(request, "health/home.html", context)


@login_required
def profile_update(request):
    profile, _ = FitnessProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = FitnessProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil fitness atualizado com sucesso.")
            return redirect("apps.health:home")
    else:
        form = FitnessProfileForm(instance=profile)

    return render(request, "health/profile_form.html", {"form": form, "profile": profile})


@login_required
def assessment_create(request):
    if request.method == "POST":
        form = PhysicalAssessmentForm(request.POST)
        if form.is_valid():
            assessment = form.save(commit=False)
            assessment.user = request.user
            preencher_dados_avaliacao(assessment)
            assessment.full_clean()
            assessment.save()
            gerar_plano_metabolico(assessment)
            messages.success(request, "Avaliação registrada com sucesso.")
            return redirect("apps.health:assessment_detail", pk=assessment.pk)
    else:
        form = PhysicalAssessmentForm()

    return render(request, "health/assessment_form.html", {"form": form, "page_title": "Nova avaliação"})


@login_required
def assessment_update(request, pk):
    assessment = get_object_or_404(PhysicalAssessment, pk=pk, user=request.user)

    if request.method == "POST":
        form = PhysicalAssessmentForm(request.POST, instance=assessment)
        if form.is_valid():
            assessment = form.save(commit=False)
            preencher_dados_avaliacao(assessment)
            assessment.full_clean()
            assessment.save()
            gerar_plano_metabolico(assessment)
            messages.success(request, "Avaliação atualizada com sucesso.")
            return redirect("apps.health:assessment_detail", pk=assessment.pk)
    else:
        form = PhysicalAssessmentForm(instance=assessment)

    return render(request, "health/assessment_form.html", {
        "form": form,
        "page_title": "Editar avaliação",
        "assessment": assessment
    })


@login_required
def assessment_list(request):
    assessments = (
        PhysicalAssessment.objects
        .filter(user=request.user)
        .select_related("metabolic_plan")
        .order_by("-data_avaliacao", "-id")
    )
    return render(request, "health/assessment_list.html", {"assessments": assessments})


@login_required
def assessment_detail(request, pk):
    assessment = get_object_or_404(
        PhysicalAssessment.objects.select_related("metabolic_plan"),
        pk=pk,
        user=request.user,
    )
    return render(request, "health/assessment_detail.html", {"assessment": assessment})


@login_required
def goal_create(request):
    if request.method == "POST":
        form = FitnessGoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.full_clean()
            goal.save()
            messages.success(request, "Meta criada com sucesso.")
            return redirect("apps.health:home")
    else:
        form = FitnessGoalForm()

    return render(request, "health/goal_form.html", {"form": form, "page_title": "Nova meta"})


@login_required
def goal_update(request, pk):
    goal = get_object_or_404(FitnessGoal, pk=pk, user=request.user)

    if request.method == "POST":
        form = FitnessGoalForm(request.POST, instance=goal)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.full_clean()
            goal.save()
            messages.success(request, "Meta atualizada com sucesso.")
            return redirect("apps.health:home")
    else:
        form = FitnessGoalForm(instance=goal)

    return render(request, "health/goal_form.html", {
        "form": form,
        "page_title": "Editar meta",
        "goal": goal
    })
    
@login_required
def daily_checkin_list(request):
    checkins = DailyCheckin.objects.filter(user=request.user).order_by("-data", "-id")
    return render(request, "health/daily_checkin_list.html", {"checkins": checkins})


@login_required
def daily_checkin_create(request):
    initial = {"data": timezone.localdate()}

    if request.method == "POST":
        form = DailyCheckinForm(request.POST)
        if form.is_valid():
            checkin = form.save(commit=False)
            checkin.user = request.user
            checkin.full_clean()
            checkin.save()
            messages.success(request, "Check-in diário registrado com sucesso.")
            return redirect("apps.health:daily_checkin_list")
    else:
        form = DailyCheckinForm(initial=initial)

    return render(request, "health/daily_checkin_form.html", {
        "form": form,
        "page_title": "Novo check-in diário",
    })


@login_required
def daily_checkin_update(request, pk):
    checkin = get_object_or_404(DailyCheckin, pk=pk, user=request.user)

    if request.method == "POST":
        form = DailyCheckinForm(request.POST, instance=checkin)
        if form.is_valid():
            checkin = form.save(commit=False)
            checkin.user = request.user
            checkin.full_clean()
            checkin.save()
            messages.success(request, "Check-in diário atualizado com sucesso.")
            return redirect("apps.health:daily_checkin_list")
    else:
        form = DailyCheckinForm(instance=checkin)

    return render(request, "health/daily_checkin_form.html", {
        "form": form,
        "page_title": "Editar check-in diário",
        "checkin": checkin,
    })