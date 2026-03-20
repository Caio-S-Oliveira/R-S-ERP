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

class PhysicalAssessment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="physical_assessments",
    )
    data_avaliacao = models.DateField()

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
    @property
    def resumo_medidas(self):
        return {
            "cintura": self.cintura,
            "quadril": self.quadril,
            "pescoco": self.pescoco,
            "torax": self.torax,
            "abdomen": self.abdomen,
        }


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