from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from .forms import FitnessGoalForm, FitnessProfileForm, PhysicalAssessmentForm
from .models import FitnessGoal, FitnessProfile, PhysicalAssessment
from .services import gerar_plano_metabolico, preencher_dados_avaliacao


@login_required
def home(request):
    profile, _ = FitnessProfile.objects.get_or_create(user=request.user)

    latest_assessment = (
        PhysicalAssessment.objects.filter(user=request.user)
        .select_related("metabolic_plan")
        .first()
    )
    previous_assessment = (
        PhysicalAssessment.objects.filter(user=request.user)
        .exclude(id=getattr(latest_assessment, "id", None))
        .first()
    )

    active_goals = FitnessGoal.objects.filter(user=request.user, status="ativa").order_by("data_limite", "created_at")
    recent_assessments = PhysicalAssessment.objects.filter(user=request.user)[:5]

    peso_delta = None
    gordura_delta = None
    cintura_delta = None

    if latest_assessment and previous_assessment:
        if latest_assessment.peso is not None and previous_assessment.peso is not None:
            peso_delta = latest_assessment.peso - previous_assessment.peso
        if latest_assessment.percentual_gordura is not None and previous_assessment.percentual_gordura is not None:
            gordura_delta = latest_assessment.percentual_gordura - previous_assessment.percentual_gordura
        if latest_assessment.cintura is not None and previous_assessment.cintura is not None:
            cintura_delta = latest_assessment.cintura - previous_assessment.cintura

    context = {
        "profile": profile,
        "latest_assessment": latest_assessment,
        "previous_assessment": previous_assessment,
        "active_goals": active_goals,
        "recent_assessments": recent_assessments,
        "total_assessments": PhysicalAssessment.objects.filter(user=request.user).count(),
        "peso_delta": peso_delta,
        "gordura_delta": gordura_delta,
        "cintura_delta": cintura_delta,
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
            return redirect("apps.apps.health:home")
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
            return redirect("app.shealth:assessment_detail", pk=assessment.pk)
    else:
        form = PhysicalAssessmentForm(instance=assessment)

    return render(request, "health/assessment_form.html", {"form": form, "page_title": "Editar avaliação", "assessment": assessment})


@login_required
def assessment_list(request):
    assessments = PhysicalAssessment.objects.filter(user=request.user).select_related("metabolic_plan")
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
            return redirect("apps.apps.health:home")
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

    return render(request, "health/goal_form.html", {"form": form, "page_title": "Editar meta", "goal": goal})