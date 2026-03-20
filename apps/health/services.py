from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from .models import FitnessProfile, MetabolicPlan, PhysicalAssessment


def to_decimal(value, default="0"):
    if value is None or value == "":
        return Decimal(default)
    return Decimal(str(value))


def round2(value):
    return Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def calcular_idade(data_nascimento, data_avaliacao=None):
    if not data_nascimento:
        return None

    ref = data_avaliacao or date.today()
    idade = ref.year - data_nascimento.year
    if (ref.month, ref.day) < (data_nascimento.month, data_nascimento.day):
        idade -= 1
    return idade


def calcular_imc(peso, altura):
    peso = to_decimal(peso, default=None)
    altura = to_decimal(altura, default=None)

    if peso is None or altura is None or altura == 0:
        return None

    return round2(peso / (altura * altura))


def classificar_imc(imc):
    if imc is None:
        return ""
    if imc < Decimal("18.5"):
        return "Abaixo do peso"
    if imc < Decimal("25"):
        return "Peso normal"
    if imc < Decimal("30"):
        return "Sobrepeso"
    if imc < Decimal("35"):
        return "Obesidade grau I"
    if imc < Decimal("40"):
        return "Obesidade grau II"
    return "Obesidade grau III"

def calcular_massa_gorda(peso, percentual_gordura):
    if percentual_gordura in (None, ""):
        return None
    peso = to_decimal(peso)
    percentual_gordura = to_decimal(percentual_gordura)
    return round2(peso * (percentual_gordura / Decimal("100")))


def calcular_massa_magra(peso, massa_gorda):
    if massa_gorda is None:
        return None
    peso = to_decimal(peso)
    return round2(peso - to_decimal(massa_gorda))


def fator_atividade(nivel_atividade):
    fatores = {
        "sedentario": Decimal("1.20"),
        "leve": Decimal("1.375"),
        "moderado": Decimal("1.55"),
        "alto": Decimal("1.725"),
        "atleta": Decimal("1.90"),
    }
    return fatores.get(nivel_atividade, Decimal("1.55"))


def estrategia_por_objetivo(objetivo):
    mapa = {
        "perder_gordura": "deficit",
        "manter": "manutencao",
        "ganhar_massa": "superavit",
        "recomposicao": "manutencao",
    }
    return mapa.get(objetivo, "manutencao")

def ajustar_calorias_por_objetivo(get, objetivo):
    get = to_decimal(get)
    if objetivo == "perder_gordura":
        return round2(get - Decimal("400"))
    if objetivo == "ganhar_massa":
        return round2(get + Decimal("300"))
    if objetivo == "recomposicao":
        return round2(get - Decimal("150"))
    return round2(get)


def calcular_tmb(sexo, peso, altura, idade):
    if not sexo or peso is None or altura is None or idade is None:
        return None

    peso = to_decimal(peso)
    altura_cm = to_decimal(altura) * Decimal("100")
    idade = Decimal(str(idade))

    base = (Decimal("10") * peso) + (Decimal("6.25") * altura_cm) - (Decimal("5") * idade)

    if sexo == "M":
        return round2(base + Decimal("5"))
    if sexo == "F":
        return round2(base - Decimal("161"))
    return None


def calcular_get(tmb, nivel_atividade):
    if tmb is None:
        return None
    return round2(to_decimal(tmb) * fator_atividade(nivel_atividade))

def calcular_macros(calorias_meta, peso, objetivo):
    calorias_meta = to_decimal(calorias_meta)
    peso = to_decimal(peso)

    if objetivo == "ganhar_massa":
        proteina_g = round2(peso * Decimal("2.00"))
        gordura_g = round2(peso * Decimal("0.90"))
    elif objetivo == "perder_gordura":
        proteina_g = round2(peso * Decimal("2.20"))
        gordura_g = round2(peso * Decimal("0.80"))
    else:
        proteina_g = round2(peso * Decimal("2.00"))
        gordura_g = round2(peso * Decimal("0.80"))

    calorias_proteina = proteina_g * Decimal("4")
    calorias_gordura = gordura_g * Decimal("9")
    calorias_restantes = calorias_meta - calorias_proteina - calorias_gordura
    carboidrato_g = round2(max(calorias_restantes, Decimal("0")) / Decimal("4"))

    total_calculado = (proteina_g * Decimal("4")) + (carboidrato_g * Decimal("4")) + (gordura_g * Decimal("9"))
    if total_calculado > 0:
        proteina_pct = round2((proteina_g * Decimal("4") / total_calculado) * Decimal("100"))
        carboidrato_pct = round2((carboidrato_g * Decimal("4") / total_calculado) * Decimal("100"))
        gordura_pct = round2((gordura_g * Decimal("9") / total_calculado) * Decimal("100"))
    else:
        proteina_pct = carboidrato_pct = gordura_pct = Decimal("0.00")

    return {
        "proteina_g": proteina_g,
        "carboidrato_g": carboidrato_g,
        "gordura_g": gordura_g,
        "proteina_pct": proteina_pct,
        "carboidrato_pct": carboidrato_pct,
        "gordura_pct": gordura_pct,
    }


def preencher_dados_avaliacao(assessment: PhysicalAssessment, profile: FitnessProfile | None = None):
    profile = profile or getattr(assessment.user, "fitness_profile", None)

    assessment.imc = calcular_imc(assessment.peso, assessment.altura)
    assessment.classificacao_imc = classificar_imc(assessment.imc)
    assessment.massa_gorda = calcular_massa_gorda(assessment.peso, assessment.percentual_gordura)
    assessment.massa_magra = calcular_massa_magra(assessment.peso, assessment.massa_gorda)

    if profile:
        assessment.idade_no_momento = calcular_idade(profile.data_nascimento, assessment.data_avaliacao)

    return assessment


def gerar_plano_metabolico(assessment: PhysicalAssessment, profile: FitnessProfile | None = None):
    profile = profile or getattr(assessment.user, "fitness_profile", None)
    if not profile:
        return None

    tmb = calcular_tmb(
        sexo=profile.sexo,
        peso=assessment.peso,
        altura=assessment.altura,
        idade=assessment.idade_no_momento,
    )
    get = calcular_get(tmb, profile.nivel_atividade)
    calorias_meta = ajustar_calorias_por_objetivo(get, profile.objetivo) if get is not None else None
    macros = calcular_macros(calorias_meta, assessment.peso, profile.objetivo) if calorias_meta is not None else {}

    plan, _ = MetabolicPlan.objects.update_or_create(
        assessment=assessment,
        defaults={
            "tmb": tmb,
            "get": get,
            "estrategia_calorica": estrategia_por_objetivo(profile.objetivo),
            "calorias_meta": calorias_meta,
            "calorias_gasto_meta": get,
            "proteina_g": macros.get("proteina_g"),
            "carboidrato_g": macros.get("carboidrato_g"),
            "gordura_g": macros.get("gordura_g"),
            "proteina_pct": macros.get("proteina_pct"),
            "carboidrato_pct": macros.get("carboidrato_pct"),
            "gordura_pct": macros.get("gordura_pct"),
        },
    )
    return plan