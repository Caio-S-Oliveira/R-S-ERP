from decimal import Decimal, ROUND_HALF_UP
from datetime import date

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class FitnessProfile(models.Model):
    SEXO_CHOICES = (
        ("M", "Masculino"),
        ("F", "Feminino"),
    )

    OBJETIVO_CHOICES = (
        ("perder_gordura", "Perder gordura"),
        ("manter", "Manter peso"),
        ("ganhar_massa", "Ganhar massa"),
        ("recomposicao", "Recomposição corporal"),
    )

    NIVEL_ATIVIDADE_CHOICES = (
        ("sedentario", "Sedentário"),
        ("leve", "Levemente ativo"),
        ("moderado", "Moderadamente ativo"),
        ("alto", "Muito ativo"),
        ("atleta", "Atleta"),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="fitness_profile",
    )
    data_nascimento = models.DateField(null=True, blank=True)
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES, blank=True)
    objetivo = models.CharField(
        max_length=20,
        choices=OBJETIVO_CHOICES,
        default="manter",
    )
    nivel_atividade = models.CharField(
        max_length=20,
        choices=NIVEL_ATIVIDADE_CHOICES,
        default="moderado",
    )
    observacoes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Perfil fitness"
        verbose_name_plural = "Perfis fitness"

    def __str__(self):
        return f"Perfil fitness de {self.user}"

    @property
    def idade_atual(self):
        if not self.data_nascimento:
            return None
        hoje = date.today()
        return hoje.year - self.data_nascimento.year - (
            (hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day)
        )


class PhysicalAssessment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="physical_assessments",
    )
    data_avaliacao = models.DateField(db_index=True)

    peso = models.DecimalField(max_digits=5, decimal_places=2)
    altura = models.DecimalField(max_digits=4, decimal_places=2)
    idade_no_momento = models.PositiveIntegerField(null=True, blank=True)

    percentual_gordura = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    massa_magra = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    massa_gorda = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    pescoco = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    ombro = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    torax = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    cintura = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    abdomen = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    quadril = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    braco_direito = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    braco_esquerdo = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    antebraco_direito = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    antebraco_esquerdo = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    coxa_direita = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    coxa_esquerda = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    panturrilha_direita = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    panturrilha_esquerda = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    pressao_arterial = models.CharField(max_length=20, blank=True)
    frequencia_cardiaca = models.PositiveIntegerField(null=True, blank=True)
    horas_sono = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    consumo_agua_litros = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)

    imc = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    classificacao_imc = models.CharField(max_length=50, blank=True)

    observacoes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-data_avaliacao", "-id"]
        verbose_name = "Avaliação física"
        verbose_name_plural = "Avaliações físicas"

    def __str__(self):
        return f"{self.user} - {self.data_avaliacao:%d/%m/%Y}"

    def clean(self):
        if self.altura and self.altura <= 0:
            raise ValidationError({"altura": "A altura deve ser maior que zero."})
        if self.peso and self.peso <= 0:
            raise ValidationError({"peso": "O peso deve ser maior que zero."})

    @property
    def resumo_medidas(self):
        return {
            "cintura": self.cintura,
            "quadril": self.quadril,
            "pescoco": self.pescoco,
            "torax": self.torax,
            "abdomen": self.abdomen,
        }

    @property
    def rcq(self):
        if self.cintura and self.quadril and self.quadril > 0:
            return (self.cintura / self.quadril).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return None

    @property
    def hidracao_status(self):
        if self.consumo_agua_litros is None:
            return "sem_dados"
        if self.consumo_agua_litros < Decimal("2.00"):
            return "baixo"
        if self.consumo_agua_litros < Decimal("3.00"):
            return "ok"
        return "bom"

    @property
    def sono_status(self):
        if self.horas_sono is None:
            return "sem_dados"
        if self.horas_sono < Decimal("6.00"):
            return "baixo"
        if self.horas_sono < Decimal("8.00"):
            return "ok"
        return "bom"


class FitnessGoal(models.Model):
    TIPO_META_CHOICES = (
        ("peso", "Peso"),
        ("gordura", "% de gordura"),
        ("massa_magra", "Massa magra"),
        ("cintura", "Cintura"),
        ("agua", "Consumo de água"),
        ("sono", "Horas de sono"),
    )

    STATUS_CHOICES = (
        ("ativa", "Ativa"),
        ("concluida", "Concluída"),
        ("cancelada", "Cancelada"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="fitness_goals",
    )
    tipo_meta = models.CharField(max_length=20, choices=TIPO_META_CHOICES)
    valor_inicial = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    valor_alvo = models.DecimalField(max_digits=6, decimal_places=2)
    data_inicio = models.DateField()
    data_limite = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="ativa")
    observacoes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["status", "data_limite", "-created_at"]
        verbose_name = "Meta fitness"
        verbose_name_plural = "Metas fitness"

    def __str__(self):
        return f"{self.user} - {self.get_tipo_meta_display()}"

    def clean(self):
        if self.data_limite and self.data_limite < self.data_inicio:
            raise ValidationError({"data_limite": "A data limite não pode ser menor que a data de início."})


class MetabolicPlan(models.Model):
    OBJETIVO_CALORICO_CHOICES = (
        ("deficit", "Déficit calórico"),
        ("manutencao", "Manutenção"),
        ("superavit", "Superávit calórico"),
    )

    assessment = models.OneToOneField(
        PhysicalAssessment,
        on_delete=models.CASCADE,
        related_name="metabolic_plan",
    )

    tmb = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    get = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    estrategia_calorica = models.CharField(
        max_length=20,
        choices=OBJETIVO_CALORICO_CHOICES,
        default="manutencao",
    )
    calorias_meta = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    calorias_gasto_meta = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    proteina_g = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    carboidrato_g = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    gordura_g = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    proteina_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    carboidrato_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    gordura_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Plano metabólico"
        verbose_name_plural = "Planos metabólicos"

    def __str__(self):
        return f"Plano metabólico - {self.assessment.user} - {self.assessment.data_avaliacao:%d/%m/%Y}"


def calcular_delta(atual, anterior):
    if atual is None or anterior is None:
        return None
    return atual - anterior


def calcular_lifestyle_score(assessment):
    if not assessment:
        return None

    score = 0

    if assessment.horas_sono is not None:
        if assessment.horas_sono >= Decimal("8.00"):
            score += 35
        elif assessment.horas_sono >= Decimal("6.00"):
            score += 25
        else:
            score += 10

    if assessment.consumo_agua_litros is not None:
        if assessment.consumo_agua_litros >= Decimal("3.00"):
            score += 35
        elif assessment.consumo_agua_litros >= Decimal("2.00"):
            score += 25
        else:
            score += 10

    if assessment.frequencia_cardiaca is not None:
        if assessment.frequencia_cardiaca <= 60:
            score += 30
        elif assessment.frequencia_cardiaca <= 80:
            score += 20
        else:
            score += 10

    return score

class DailyCheckin(models.Model):
    HUMOR_CHOICES = (
        ("terrivel", "Terrível"),
        ("ruim", "Ruim"),
        ("ok", "Ok"),
        ("bom", "Bom"),
        ("excelente", "Excelente"),
    )

    ENERGIA_CHOICES = (
        ("muito_baixa", "Muito baixa"),
        ("baixa", "Baixa"),
        ("media", "Média"),
        ("alta", "Alta"),
        ("muito_alta", "Muito alta"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="daily_checkins",
    )
    data = models.DateField(db_index=True)

    peso = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    horas_sono = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    consumo_agua_litros = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)

    treinou = models.BooleanField(default=False)
    minutos_treino = models.PositiveIntegerField(null=True, blank=True)
    passos = models.PositiveIntegerField(null=True, blank=True)

    aderencia_dieta = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Percentual de aderência da dieta no dia (0 a 100)."
    )

    humor = models.CharField(max_length=20, choices=HUMOR_CHOICES, blank=True)
    energia = models.CharField(max_length=20, choices=ENERGIA_CHOICES, blank=True)

    observacoes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-data", "-id"]
        unique_together = ("user", "data")
        verbose_name = "Check-in diário"
        verbose_name_plural = "Check-ins diários"

    def __str__(self):
        return f"{self.user} - {self.data:%d/%m/%Y}"

    def clean(self):
        errors = {}

        if self.horas_sono is not None and self.horas_sono < 0:
            errors["horas_sono"] = "As horas de sono não podem ser negativas."

        if self.consumo_agua_litros is not None and self.consumo_agua_litros < 0:
            errors["consumo_agua_litros"] = "O consumo de água não pode ser negativo."

        if self.minutos_treino is not None and not self.treinou:
            errors["minutos_treino"] = "Informe minutos de treino apenas quando marcar que treinou."

        if self.aderencia_dieta is not None and not (0 <= self.aderencia_dieta <= 100):
            errors["aderencia_dieta"] = "A aderência da dieta deve estar entre 0 e 100."

        if errors:
            raise ValidationError(errors)

    @property
    def lifestyle_score(self):
        score = 0

        if self.horas_sono is not None:
            if self.horas_sono >= Decimal("8.00"):
                score += 25
            elif self.horas_sono >= Decimal("6.00"):
                score += 18
            else:
                score += 8

        if self.consumo_agua_litros is not None:
            if self.consumo_agua_litros >= Decimal("3.00"):
                score += 20
            elif self.consumo_agua_litros >= Decimal("2.00"):
                score += 14
            else:
                score += 6

        if self.treinou:
            if self.minutos_treino and self.minutos_treino >= 60:
                score += 20
            else:
                score += 14

        if self.passos is not None:
            if self.passos >= 10000:
                score += 15
            elif self.passos >= 7000:
                score += 10
            else:
                score += 4

        if self.aderencia_dieta is not None:
            if self.aderencia_dieta >= 90:
                score += 20
            elif self.aderencia_dieta >= 70:
                score += 14
            else:
                score += 6

        return score