from django.utils import timezone
from apps.finance.models import Account, Category, Tag, Transaction


def get_or_create_default_shopping_category(user):
    category, _ = Category.objects.get_or_create(
        user=user,
        name="Compras",
        type="expense",
        defaults={
            "color": "#6f42c1",
            "icon": "cart",
        }
    )
    return category


def get_or_create_default_account(user):
    account = Account.objects.filter(user=user).order_by("id").first()

    if account:
        return account

    account = Account.objects.create(
        user=user,
        name="Carteira",
        initial_balance=0,
    )
    return account


def get_or_create_shopping_tag(user):
    tag, _ = Tag.objects.get_or_create(
        user=user,
        name="shopping",
    )
    return tag


def create_financial_transaction_for_shopping_item(item):
    if item.financial_transaction_created:
        return False, "A transação financeira já foi criada para este item."

    unit_price = item.bought_price or item.current_price or item.desired_price
    if unit_price is None:
        return False, "O item não possui valor para gerar transação financeira."

    total_value = unit_price * item.quantity
    user = item.shopping_list.user

    category = get_or_create_default_shopping_category(user)
    account = get_or_create_default_account(user)
    tag = get_or_create_shopping_tag(user)

    transaction = Transaction.objects.create(
        user=user,
        type="expense",
        description=f"Compra: {item.name}",
        amount=total_value,
        category=category,
        account=account,
        date=(item.bought_at.date() if item.bought_at else timezone.localdate()),
        notes=(
            f"Origem: Lista de compras\n"
            f"Lista: {item.shopping_list.name}\n"
            f"Loja: {item.store_name or '-'}\n"
            f"Quantidade: {item.quantity}\n"
            f"Preço unitário: {unit_price}\n"
            f"Link: {item.product_url or '-'}"
        ),
        is_paid=True,
        schedule_type="single",
        recurrence_frequency="",
        series_position=1,
        series_total=1,
    )
    transaction.tags.add(tag)

    item.financial_transaction_created = True
    item.financial_transaction = transaction
    item.save(update_fields=["financial_transaction_created", "financial_transaction"])

    return True, "Transação financeira criada com sucesso."