from datetime import datetime
from decimal import Decimal
import calendar
import uuid

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction as db_transaction
from django.db.models import (
    Sum,
    Case,
    When,
    Value,
    DecimalField,
    F,
    ExpressionWrapper,
    Q,
)
from django.db.models.deletion import ProtectedError
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import TransactionForm
from .models import Account, Category, Tag, Transaction


# =========================
# HELPERS
# =========================
def add_months(source_date, months):
    month = source_date.month - 1 + months
    year = source_date.year + month // 12
    month = month % 12 + 1
    day = min(source_date.day, calendar.monthrange(year, month)[1])
    return source_date.replace(year=year, month=month, day=day)


def add_years(source_date, years):
    year = source_date.year + years
    day = min(source_date.day, calendar.monthrange(year, source_date.month)[1])
    return source_date.replace(year=year, day=day)


def apply_recurrence(source_date, step, frequency):
    if frequency == "yearly":
        return add_years(source_date, step)
    return add_months(source_date, step)


def get_period_label(selected_month):
    if not selected_month:
        return "Geral"

    try:
        selected_date = datetime.strptime(selected_month, "%Y-%m")
        month_names = {
            1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
            5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
            9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
        }
        return f"{month_names[selected_date.month]} de {selected_date.year}"
    except ValueError:
        return "Geral"


def calculate_net_total(queryset):
    return queryset.aggregate(
        total=Coalesce(
            Sum(
                Case(
                    When(type="income", then=F("amount")),
                    When(
                        type="expense",
                        then=ExpressionWrapper(
                            F("amount") * Value(-1),
                            output_field=DecimalField(max_digits=14, decimal_places=2),
                        ),
                    ),
                    default=Value(0),
                    output_field=DecimalField(max_digits=14, decimal_places=2),
                )
            ),
            Decimal("0.00")
        )
    )["total"]


# =========================
# FORMS
# =========================
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "type", "color", "icon"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nome da categoria"}),
            "type": forms.Select(attrs={"class": "form-select"}),
            "color": forms.TextInput(attrs={"class": "form-control form-control-color", "type": "color"}),
            "icon": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: fa-wallet"}),
        }


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ["name", "initial_balance"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nome da conta"}),
            "initial_balance": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
        }


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nome da tag"}),
        }


# =========================
# DASHBOARD
# =========================
@login_required
def finance_home(request):
    user = request.user
    selected_month = (request.GET.get("month") or "").strip()
    has_month_filter = bool(selected_month)

    transactions_qs = (
        Transaction.objects
        .filter(user=user)
        .select_related("category", "account")
        .prefetch_related("tags")
        .order_by("-date", "-id")
    )

    filtered_transactions = transactions_qs

    if has_month_filter:
        try:
            selected_date = datetime.strptime(selected_month, "%Y-%m")
            filtered_transactions = filtered_transactions.filter(
                date__year=selected_date.year,
                date__month=selected_date.month
            )
        except ValueError:
            selected_month = ""
            has_month_filter = False
            filtered_transactions = transactions_qs

    income_total = filtered_transactions.filter(type="income").aggregate(
        total=Coalesce(Sum("amount"), Decimal("0.00"))
    )["total"]

    expense_total = filtered_transactions.filter(type="expense").aggregate(
        total=Coalesce(Sum("amount"), Decimal("0.00"))
    )["total"]

    balance = income_total - expense_total
    transactions = filtered_transactions[:30]

    # Evolução mensal sempre mostra os últimos 12 meses
    current_date = timezone.localdate()
    monthly_labels = []
    monthly_income_data = []
    monthly_expense_data = []

    month_names = {
        1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr",
        5: "Mai", 6: "Jun", 7: "Jul", 8: "Ago",
        9: "Set", 10: "Out", 11: "Nov", 12: "Dez"
    }

    year_month_pairs = []
    for offset in range(11, -1, -1):
        ref_month = current_date.month - offset
        ref_year = current_date.year

        while ref_month <= 0:
            ref_month += 12
            ref_year -= 1

        while ref_month > 12:
            ref_month -= 12
            ref_year += 1

        year_month_pairs.append((ref_year, ref_month))

    for year, month in year_month_pairs:
        monthly_labels.append(f"{month_names[month]}/{str(year)[-2:]}")
        month_qs = transactions_qs.filter(date__year=year, date__month=month)

        month_income = month_qs.filter(type="income").aggregate(
            total=Coalesce(Sum("amount"), Decimal("0.00"))
        )["total"]

        month_expense = month_qs.filter(type="expense").aggregate(
            total=Coalesce(Sum("amount"), Decimal("0.00"))
        )["total"]

        monthly_income_data.append(float(month_income))
        monthly_expense_data.append(float(month_expense))

    expense_by_category = (
        filtered_transactions
        .filter(type="expense", category__isnull=False)
        .values("category__id", "category__name")
        .annotate(total=Coalesce(Sum("amount"), Decimal("0.00")))
        .order_by("-total", "category__name")
    )

    expense_category_labels = [item["category__name"] for item in expense_by_category]
    expense_category_data = [float(item["total"]) for item in expense_by_category]
    expense_category_ids = [item["category__id"] for item in expense_by_category]

    accounts = Account.objects.filter(user=user).order_by("name")
    account_balance_labels = []
    account_balance_data = []

    for account in accounts:
        movements_qs = filtered_transactions.filter(account=account)
        movement_total = calculate_net_total(movements_qs)

        if has_month_filter:
            account_total = movement_total
        else:
            all_account_movements = transactions_qs.filter(account=account)
            account_total = (account.initial_balance or Decimal("0.00")) + calculate_net_total(all_account_movements)

        account_balance_labels.append(account.name)
        account_balance_data.append(float(account_total))

    future_transactions = transactions_qs.filter(
        date__gt=current_date,
        is_paid=False
    )

    future_expense_total = future_transactions.filter(type="expense").aggregate(
        total=Coalesce(Sum("amount"), Decimal("0.00"))
    )["total"]

    future_income_total = future_transactions.filter(type="income").aggregate(
        total=Coalesce(Sum("amount"), Decimal("0.00"))
    )["total"]

    context = {
        "selected_month": selected_month,
        "has_month_filter": has_month_filter,
        "period_label": get_period_label(selected_month),
        "balance": balance,
        "income_total": income_total,
        "expense_total": expense_total,
        "transactions": transactions,
        "monthly_labels": monthly_labels,
        "monthly_income_data": monthly_income_data,
        "monthly_expense_data": monthly_expense_data,
        "expense_category_labels": expense_category_labels,
        "expense_category_data": expense_category_data,
        "expense_category_ids": expense_category_ids,
        "account_balance_labels": account_balance_labels,
        "account_balance_data": account_balance_data,
        "future_expense_total": future_expense_total,
        "future_income_total": future_income_total,
    }

    return render(request, "finance/home.html", context)


# =========================
# TRANSAÇÕES
# =========================
@login_required
def transaction_create(request):
    if request.method == "POST":
        form = TransactionForm(request.POST, user=request.user)

        if form.is_valid():
            transaction_mode = form.cleaned_data.get("transaction_mode") or "single"
            installments = form.cleaned_data.get("installments") or 1
            recurrence_count = form.cleaned_data.get("recurrence_count") or 1
            recurrence_frequency = form.cleaned_data.get("recurrence_frequency") or "monthly"
            tags = list(form.cleaned_data.get("tags"))
            base_transaction = form.save(commit=False)
            base_transaction.user = request.user

            original_description = (base_transaction.description or "").strip()
            today = timezone.localdate()

            with db_transaction.atomic():
                if transaction_mode == "single":
                    transaction = Transaction.objects.create(
                        user=request.user,
                        type=base_transaction.type,
                        description=original_description,
                        amount=base_transaction.amount,
                        category=base_transaction.category,
                        account=base_transaction.account,
                        date=base_transaction.date,
                        notes=base_transaction.notes,
                        is_paid=base_transaction.is_paid,
                        schedule_type="single",
                        recurrence_frequency="",
                        series_group=None,
                        series_position=1,
                        series_total=1,
                    )

                    if tags:
                        transaction.tags.set(tags)

                    messages.success(request, "Transação cadastrada com sucesso.")

                elif transaction_mode == "installment":
                    series_group = uuid.uuid4()

                    for number in range(1, installments + 1):
                        installment_date = add_months(base_transaction.date, number - 1)
                        is_paid = base_transaction.is_paid if number == 1 else False

                        transaction = Transaction.objects.create(
                            user=request.user,
                            type=base_transaction.type,
                            description=f"{original_description} ({number}/{installments})",
                            amount=base_transaction.amount,
                            category=base_transaction.category,
                            account=base_transaction.account,
                            date=installment_date,
                            notes=base_transaction.notes,
                            is_paid=is_paid,
                            schedule_type="installment",
                            recurrence_frequency="",
                            series_group=series_group,
                            series_position=number,
                            series_total=installments,
                        )

                        if tags:
                            transaction.tags.set(tags)

                    messages.success(
                        request,
                        f"Transação parcelada criada com sucesso. {installments} parcelas foram geradas."
                    )

                elif transaction_mode == "recurring":
                    series_group = uuid.uuid4()

                    for number in range(1, recurrence_count + 1):
                        recurrence_date = apply_recurrence(
                            base_transaction.date,
                            number - 1,
                            recurrence_frequency
                        )
                        is_paid = base_transaction.is_paid if number == 1 else False

                        transaction = Transaction.objects.create(
                            user=request.user,
                            type=base_transaction.type,
                            description=f"{original_description} [{number}/{recurrence_count}]",
                            amount=base_transaction.amount,
                            category=base_transaction.category,
                            account=base_transaction.account,
                            date=recurrence_date,
                            notes=base_transaction.notes,
                            is_paid=is_paid,
                            schedule_type="recurring",
                            recurrence_frequency=recurrence_frequency,
                            series_group=series_group,
                            series_position=number,
                            series_total=recurrence_count,
                        )

                        if tags:
                            transaction.tags.set(tags)

                    messages.success(
                        request,
                        f"Lançamento recorrente criado com sucesso. {recurrence_count} ocorrências foram geradas."
                    )

            return redirect("finance_home")
    else:
        form = TransactionForm(user=request.user)

    return render(
        request,
        "finance/transaction_form.html",
        {
            "form": form,
            "page_title": "Nova transação",
            "is_edit_mode": False,
        }
    )


@login_required
def transaction_update(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)

    if request.method == "POST":
        form = TransactionForm(request.POST, instance=transaction, user=request.user)

        form.fields.pop("transaction_mode", None)
        form.fields.pop("installments", None)
        form.fields.pop("recurrence_count", None)
        form.fields.pop("recurrence_frequency", None)

        if form.is_valid():
            form.save()
            messages.success(request, "Transação atualizada com sucesso.")
            return redirect("finance_home")
    else:
        form = TransactionForm(instance=transaction, user=request.user)
        form.fields.pop("transaction_mode", None)
        form.fields.pop("installments", None)
        form.fields.pop("recurrence_count", None)
        form.fields.pop("recurrence_frequency", None)

    return render(
        request,
        "finance/transaction_form.html",
        {
            "form": form,
            "page_title": "Editar transação",
            "is_edit_mode": True,
            "transaction_object": transaction,
        }
    )


@login_required
def transaction_delete(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)

    if request.method == "POST":
        delete_scope = request.POST.get("delete_scope", "single")

        if delete_scope == "series" and transaction.series_group:
            qs = Transaction.objects.filter(
                user=request.user,
                series_group=transaction.series_group
            )
            deleted_count = qs.count()
            qs.delete()
            messages.success(request, f"Série removida com sucesso. {deleted_count} lançamentos excluídos.")
        else:
            transaction.delete()
            messages.success(request, "Transação removida com sucesso.")

        return redirect("finance_home")

    return render(request, "finance/transaction_confirm_delete.html", {"object": transaction})


@login_required
def transaction_list(request):
    qs = (
        Transaction.objects
        .filter(user=request.user)
        .select_related("category", "account")
        .prefetch_related("tags")
        .order_by("-date", "-created_at")
    )

    search = request.GET.get("q")
    transaction_type = request.GET.get("type")
    category_id = request.GET.get("category")
    account_id = request.GET.get("account")
    paid_status = request.GET.get("paid_status")
    schedule_type = request.GET.get("schedule_type")

    if search:
        qs = qs.filter(
            Q(description__icontains=search) |
            Q(notes__icontains=search) |
            Q(category__name__icontains=search) |
            Q(account__name__icontains=search)
        )

    if transaction_type:
        qs = qs.filter(type=transaction_type)

    if category_id:
        qs = qs.filter(category_id=category_id)

    if account_id:
        qs = qs.filter(account_id=account_id)

    if paid_status == "paid":
        qs = qs.filter(is_paid=True)
    elif paid_status == "unpaid":
        qs = qs.filter(is_paid=False)

    if schedule_type:
        qs = qs.filter(schedule_type=schedule_type)

    return render(request, "finance/transaction_list.html", {
        "transactions": qs,
        "search": search or "",
        "selected_type": transaction_type or "",
        "selected_category": category_id or "",
        "selected_account": account_id or "",
        "selected_paid_status": paid_status or "",
        "selected_schedule_type": schedule_type or "",
        "categories": Category.objects.filter(user=request.user).order_by("name"),
        "accounts": Account.objects.filter(user=request.user).order_by("name"),
    })


# =========================
# CATEGORY CRUD
# =========================
@login_required
def category_list(request):
    categories = Category.objects.filter(user=request.user).order_by("type", "name")
    return render(request, "finance/category_list.html", {"categories": categories})


@login_required
def category_create(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            messages.success(request, "Categoria cadastrada com sucesso.")
            return redirect("category_list")
    else:
        form = CategoryForm()

    return render(request, "finance/category_form.html", {"form": form})


@login_required
def category_update(request, pk):
    obj = get_object_or_404(Category, pk=pk, user=request.user)

    if request.method == "POST":
        form = CategoryForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Categoria atualizada com sucesso.")
            return redirect("category_list")
    else:
        form = CategoryForm(instance=obj)

    return render(request, "finance/category_form.html", {"form": form})


@login_required
def category_delete(request, pk):
    obj = get_object_or_404(Category, pk=pk, user=request.user)

    if request.method == "POST":
        try:
            obj.delete()
            messages.success(request, "Categoria removida com sucesso.")
        except ProtectedError:
            messages.error(request, "Categoria vinculada a transações.")
        return redirect("category_list")

    return render(request, "finance/category_confirm_delete.html", {"object": obj})


# =========================
# ACCOUNT CRUD
# =========================
@login_required
def account_list(request):
    accounts = Account.objects.filter(user=request.user)
    return render(request, "finance/account_list.html", {"accounts": accounts})


@login_required
def account_create(request):
    if request.method == "POST":
        form = AccountForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            messages.success(request, "Conta criada.")
            return redirect("account_list")
    else:
        form = AccountForm()

    return render(request, "finance/account_form.html", {"form": form})


@login_required
def account_update(request, pk):
    obj = get_object_or_404(Account, pk=pk, user=request.user)

    if request.method == "POST":
        form = AccountForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Conta atualizada.")
            return redirect("account_list")
    else:
        form = AccountForm(instance=obj)

    return render(request, "finance/account_form.html", {"form": form})


@login_required
def account_delete(request, pk):
    obj = get_object_or_404(Account, pk=pk, user=request.user)

    if request.method == "POST":
        try:
            obj.delete()
            messages.success(request, "Conta removida.")
        except ProtectedError:
            messages.error(request, "Conta vinculada a transações.")
        return redirect("account_list")

    return render(request, "finance/account_confirm_delete.html", {"object": obj})


# =========================
# TAG CRUD
# =========================
@login_required
def tag_list(request):
    tags = Tag.objects.filter(user=request.user)
    return render(request, "finance/tag_list.html", {"tags": tags})


@login_required
def tag_create(request):
    if request.method == "POST":
        form = TagForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            messages.success(request, "Tag criada.")
            return redirect("tag_list")
    else:
        form = TagForm()

    return render(request, "finance/tag_form.html", {"form": form})


@login_required
def tag_update(request, pk):
    obj = get_object_or_404(Tag, pk=pk, user=request.user)

    if request.method == "POST":
        form = TagForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Tag atualizada.")
            return redirect("tag_list")
    else:
        form = TagForm(instance=obj)

    return render(request, "finance/tag_form.html", {"form": form})


@login_required
def tag_delete(request, pk):
    obj = get_object_or_404(Tag, pk=pk, user=request.user)

    if request.method == "POST":
        obj.delete()
        messages.success(request, "Tag removida.")
        return redirect("tag_list")

    return render(request, "finance/tag_confirm_delete.html", {"object": obj})