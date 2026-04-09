from django import forms
from .models import FitnessGoal, FitnessProfile, PhysicalAssessment, DailyCheckin

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

class DailyCheckinForm(forms.ModelForm):
    class Meta:
        model = DailyCheckin
        fields = [
            "data",
            "peso",
            "horas_sono",
            "consumo_agua_litros",
            "treinou",
            "minutos_treino",
            "passos",
            "aderencia_dieta",
            "humor",
            "energia",
            "observacoes",
        ]
        widgets = {
            "data": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "peso": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "0.00"}),
            "horas_sono": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "0.00"}),
            "consumo_agua_litros": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "0.00"}),
            "treinou": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "minutos_treino": forms.NumberInput(attrs={"class": "form-control", "placeholder": "0"}),
            "passos": forms.NumberInput(attrs={"class": "form-control", "placeholder": "0"}),
            "aderencia_dieta": forms.NumberInput(attrs={"class": "form-control", "min": "0", "max": "100", "placeholder": "0 a 100"}),
            "humor": forms.Select(attrs={"class": "form-select"}),
            "energia": forms.Select(attrs={"class": "form-select"}),
            "observacoes": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Observações do dia"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        treinou = cleaned_data.get("treinou")
        minutos_treino = cleaned_data.get("minutos_treino")

        if not treinou:
            cleaned_data["minutos_treino"] = None
        elif treinou and not minutos_treino:
            self.add_error("minutos_treino", "Informe os minutos de treino.")

        return cleaned_data