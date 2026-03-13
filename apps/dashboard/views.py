from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def home(request):
    context = {
        "finance": {
            "saldo_atual": "5.320,00",
            "despesas_mes": "2.150,00",
            "grafico": [30, 55, 40, 70, 60, 85, 75],
        },
        "health": {
            "passos_hoje": "8.450",
            "peso_atual": "75 kg",
            "treinos_feitos": 4,
            "treinos_meta": 5,
            "progresso": 80,
        },
        "shopping_items": [
            {"nome": "Leite", "checked": True},
            {"nome": "Pão integral", "checked": True},
            {"nome": "Ovos", "checked": True},
            {"nome": "Frutas", "checked": False},
        ],
        "tasks": [
            {"titulo": "Reunião às 15:00"},
            {"titulo": "Atualizar relatório financeiro"},
            {"titulo": "Treino de musculação"},
        ],
    }

    return render(request, "dashboard/home.html", context)