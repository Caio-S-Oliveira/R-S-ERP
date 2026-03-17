from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.finance.models import Account, Category, Tag


class Command(BaseCommand):
    help = "Cria contas, categorias e tags padrão para um usuário"

    def add_arguments(self, parser):
        parser.add_argument("username", type=str, help="Username do usuário que vai receber os dados iniciais")

    def handle(self, *args, **options):
        username = options["username"]
        User = get_user_model()

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"Usuário '{username}' não encontrado.")
            )
            return

        accounts = [
            {"name": "Carteira", "initial_balance": Decimal("0.00")},
            {"name": "Mercado Pago", "initial_balance": Decimal("0.00")},
            {"name": "Nubank", "initial_balance": Decimal("0.00")},
            {"name": "PicPay", "initial_balance": Decimal("0.00")},
        ]

        categories = [
            {"name": "Salário", "type": Category.INCOME, "color": "#198754", "icon": "fa-wallet"},
            {"name": "Freelance", "type": Category.INCOME, "color": "#20c997", "icon": "fa-laptop-code"},
            {"name": "Investimentos", "type": Category.INCOME, "color": "#0d6efd", "icon": "fa-chart-line"},
            {"name": "Presente", "type": Category.INCOME, "color": "#6f42c1", "icon": "fa-gift"},
            {"name": "Outras Receitas", "type": Category.INCOME, "color": "#198754", "icon": "fa-plus-circle"},

            {"name": "Mercado", "type": Category.EXPENSE, "color": "#dc3545", "icon": "fa-cart-shopping"},
            {"name": "Transporte", "type": Category.EXPENSE, "color": "#fd7e14", "icon": "fa-bus"},
            {"name": "Gasolina", "type": Category.EXPENSE, "color": "#ffc107", "icon": "fa-gas-pump"},
            {"name": "Lazer", "type": Category.EXPENSE, "color": "#0dcaf0", "icon": "fa-gamepad"},
            {"name": "Academia", "type": Category.EXPENSE, "color": "#6610f2", "icon": "fa-dumbbell"},
            {"name": "Saúde", "type": Category.EXPENSE, "color": "#d63384", "icon": "fa-heart-pulse"},
            {"name": "Moradia", "type": Category.EXPENSE, "color": "#6c757d", "icon": "fa-house"},
            {"name": "Restaurante", "type": Category.EXPENSE, "color": "#fd7e14", "icon": "fa-utensils"},
            {"name": "Assinaturas", "type": Category.EXPENSE, "color": "#343a40", "icon": "fa-repeat"},
            {"name": "Outras Despesas", "type": Category.EXPENSE, "color": "#dc3545", "icon": "fa-minus-circle"},
        ]

        tags = [
            "Fixo",
            "Essencial",
            "Supérfluo",
            "Mensal",
            "Trabalho",
            "Pessoal",
            "Urgente",
            "Parcelado",
        ]

        created_accounts = 0
        created_categories = 0
        created_tags = 0

        for account_data in accounts:
            _, created = Account.objects.get_or_create(
                user=user,
                name=account_data["name"],
                defaults={
                    "initial_balance": account_data["initial_balance"],
                },
            )
            if created:
                created_accounts += 1

        for category_data in categories:
            _, created = Category.objects.get_or_create(
                user=user,
                name=category_data["name"],
                type=category_data["type"],
                defaults={
                    "color": category_data["color"],
                    "icon": category_data["icon"],
                },
            )
            if created:
                created_categories += 1

        for tag_name in tags:
            _, created = Tag.objects.get_or_create(
                user=user,
                name=tag_name,
            )
            if created:
                created_tags += 1

        self.stdout.write(self.style.SUCCESS(
            f"Seed concluído para '{username}'. "
            f"Contas criadas: {created_accounts}, "
            f"Categorias criadas: {created_categories}, "
            f"Tags criadas: {created_tags}."
        ))