from django import forms

from .models import FitnessGoal, FitnessProfile, PhysicalAssessment


INPUT_CLASS = "form-control"
SELECT_CLASS = "form-select"
TEXTAREA_CLASS = "form-control"
DATE_CLASS = "form-control"

class FitnessProfileForm(forms.ModelForm):
    class Meta:
        model = FitnessProfile
        fields = [
            "data_nascimento",
            "sexo",
            "objetivo",
            "nivel_atividade",
            "observacoes",
        ]
        widgets = {
            "data_nascimento": forms.DateInput(attrs={"type": "date", "class": DATE_CLASS}),
            "sexo": forms.Select(attrs={"class": SELECT_CLASS}),
            "objetivo": forms.Select(attrs={"class": SELECT_CLASS}),
            "nivel_atividade": forms.Select(attrs={"class": SELECT_CLASS}),
            "observacoes": forms.Textarea(attrs={"class": TEXTAREA_CLASS, "rows": 3}),
        }


class PhysicalAssessmentForm(forms.ModelForm):
    class Meta:
        model = PhysicalAssessment
        exclude = [
            "user",
            "idade_no_momento",
            "massa_magra",
            "massa_gorda",
            "imc",
            "classificacao_imc",
            "created_at",
        ]
        widgets = {
            "data_avaliacao": forms.DateInput(attrs={"type": "date", "class": DATE_CLASS}),
            "peso": forms.NumberInput(attrs={"class": INPUT_CLASS, "step": "0.01", "placeholder": "Ex: 82.50"}),
            "altura": forms.NumberInput(attrs={"class": INPUT_CLASS, "step": "0.01", "placeholder": "Ex: 1.78"}),
            "percentual_gordura": forms.NumberInput(attrs={"class": INPUT_CLASS, "step": "0.01"}),
            "pescoco": forms.NumberInput(attrs={"class": INPUT_CLASS, "step": "0.01"}),
            "ombro": forms.NumberInput(attrs={"class": INPUT_CLASS, "step": "0.01"}),
            "torax": forms.NumberInput(attrs={"class": INPUT_CLASS, "step": "0.01"}),
            "cintura": forms.NumberInput(attrs={"class": INPUT_CLASS, "step": "0.01"}),
            "abdomen": forms.NumberInput(attrs={"class": INPUT_CLASS, "step": "0.01"}),
            "quadril": forms.NumberInput(attrs={"class": INPUT_CLASS, "step": "0.01"}),
            "braco_direito": forms.NumberInput(attrs={"class": INPUT_CLASS, "step": "0.01"}),
            "braco_esquerdo": forms.NumberInput(attrs={"class": INPUT_CLASS, "step": "0.01"}),
            "antebraco_direito": forms.NumberInput(attrs={"class": INPUT_CLASS, "step": "0.01"}),
            "antebraco_esquerdo": forms.NumberInput(attrs={"class": INPUT_CLASS, "step": "0.01"}),
            "coxa_direita": forms.NumberInput(attrs={"class": INPUT_CLASS, "step": "0.01"}),
            "coxa_esquerda": forms.NumberInput(attrs={"class": INPUT_CLASS, "step": "0.01"}),
            "panturrilha_direita": forms.NumberInput(attrs={"class": INPUT_CLASS, "step": "0.01"}),
            "panturrilha_esquerda": forms.NumberInput(attrs={"class": INPUT_CLASS, "step": "0.01"}),
            "pressao_arterial": forms.TextInput(attrs={"class": INPUT_CLASS, "placeholder": "Ex: 12x8"}),
            "frequencia_cardiaca": forms.NumberInput(attrs={"class": INPUT_CLASS}),
            "horas_sono": forms.NumberInput(attrs={"class": INPUT_CLASS, "step": "0.01"}),
            "consumo_agua_litros": forms.NumberInput(attrs={"class": INPUT_CLASS, "step": "0.01"}),
            "observacoes": forms.Textarea(attrs={"class": TEXTAREA_CLASS, "rows": 4}),
        }

class FitnessGoalForm(forms.ModelForm):
    class Meta:
        model = FitnessGoal
        exclude = ["user", "created_at"]
        widgets = {
            "tipo_meta": forms.Select(attrs={"class": SELECT_CLASS}),
            "valor_inicial": forms.NumberInput(attrs={"class": INPUT_CLASS, "step": "0.01"}),
            "valor_alvo": forms.NumberInput(attrs={"class": INPUT_CLASS, "step": "0.01"}),
            "data_inicio": forms.DateInput(attrs={"type": "date", "class": DATE_CLASS}),
            "data_limite": forms.DateInput(attrs={"type": "date", "class": DATE_CLASS}),
            "status": forms.Select(attrs={"class": SELECT_CLASS}),
            "observacoes": forms.Textarea(attrs={"class": TEXTAREA_CLASS, "rows": 3}),
        }