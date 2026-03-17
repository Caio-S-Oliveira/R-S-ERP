from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum, Value, DecimalField
from django.db.models.deletion import ProtectedError
from decimal import Decimal
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect, render
from collections import defaultdict
from .forms import TransactionForm
from .models import Account, Category, Tag, Transaction


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "type", "color", "icon"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nome da categoria"
            }),
            "type": forms.Select(attrs={"class": "form-select"}),
            "color": forms.TextInput(attrs={
                "class": "form-control form-control-color",
                "type": "color"
            }),
            "icon": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex: fa-wallet"
            }),
        }

class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ["name", "initial_balance"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nome da conta"
            }),
            "initial_balance": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "placeholder": "0.00"
            }),
        }

class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nome da tag"
            }),
        }

@login_required
@login_required
def finance_home(request):
    transactions = (
        Transaction.objects
        .filter(user=request.user)
        .select_related("category", "account")
        .prefetch_related("tags")
        .order_by("-date", "-created_at")[:10]
    )

    income_total = (
        Transaction.objects
        .filter(user=request.user, type=Transaction.INCOME)
        .aggregate(
            total=Coalesce(
                Sum("amount"),
                Value(Decimal("0.00")),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            )
        )["total"]
    )

    expense_total = (
        Transaction.objects
        .filter(user=request.user, type=Transaction.EXPENSE)
        .aggregate(
            total=Coalesce(
                Sum("amount"),
                Value(Decimal("0.00")),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            )
        )["total"]
    )

    initial_balance = (
        Account.objects
        .filter(user=request.user)
        .aggregate(
            total=Coalesce(
                Sum("initial_balance"),
                Value(Decimal("0.00")),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            )
        )["total"]
    )

    balance = initial_balance + income_total - expense_total

    # =========================
    # GRÁFICO 1: EVOLUÇÃO MENSAL
    # =========================
    monthly_transactions = (
        Transaction.objects
        .filter(user=request.user)
        .order_by("date")
        .values("date", "type", "amount")
    )

    month_map_income = defaultdict(Decimal)
    month_map_expense = defaultdict(Decimal)

    for item in monthly_transactions:
        month_label = item["date"].strftime("%m/%Y")
        if item["type"] == Transaction.INCOME:
            month_map_income[month_label] += item["amount"]
        else:
            month_map_expense[month_label] += item["amount"]

    monthly_labels = sorted(set(list(month_map_income.keys()) + list(month_map_expense.keys())), key=lambda x: (x[3:], x[:2]))
    monthly_income_data = [float(month_map_income[label]) for label in monthly_labels]
    monthly_expense_data = [float(month_map_expense[label]) for label in monthly_labels]

    # =========================
    # GRÁFICO 2: DESPESAS POR CATEGORIA
    # =========================
    expense_by_category = (
        Transaction.objects
        .filter(user=request.user, type=Transaction.EXPENSE)
        .values("category__name")
        .annotate(total=Coalesce(
            Sum("amount"),
            Value(Decimal("0.00")),
            output_field=DecimalField(max_digits=12, decimal_places=2),
        ))
        .order_by("category__name")
    )

    expense_category_labels = [item["category__name"] for item in expense_by_category]
    expense_category_data = [float(item["total"]) for item in expense_by_category]

    # =========================
    # GRÁFICO 3: SALDO POR CONTA
    # saldo = initial_balance + receitas - despesas
    # =========================
    accounts = Account.objects.filter(user=request.user).order_by("name")

    account_balance_labels = []
    account_balance_data = []

    for account in accounts:
        account_income = (
            Transaction.objects
            .filter(user=request.user, account=account, type=Transaction.INCOME)
            .aggregate(
                total=Coalesce(
                    Sum("amount"),
                    Value(Decimal("0.00")),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                )
            )["total"]
        )

        account_expense = (
            Transaction.objects
            .filter(user=request.user, account=account, type=Transaction.EXPENSE)
            .aggregate(
                total=Coalesce(
                    Sum("amount"),
                    Value(Decimal("0.00")),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                )
            )["total"]
        )

        account_total = account.initial_balance + account_income - account_expense

        account_balance_labels.append(account.name)
        account_balance_data.append(float(account_total))

    context = {
        "transactions": transactions,
        "income_total": income_total,
        "expense_total": expense_total,
        "balance": balance,

        "monthly_labels": monthly_labels,
        "monthly_income_data": monthly_income_data,
        "monthly_expense_data": monthly_expense_data,

        "expense_category_labels": expense_category_labels,
        "expense_category_data": expense_category_data,

        "account_balance_labels": account_balance_labels,
        "account_balance_data": account_balance_data,
    }
    return render(request, "finance/home.html", context)

# TRANSAÇÕES
@login_required
def transaction_create(request):
    if request.method == "POST":
        form = TransactionForm(request.POST, user=request.user)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            form.save_m2m()

            messages.success(request, "Transação cadastrada com sucesso.")
            return redirect("finance_home")
    else:
        form = TransactionForm(user=request.user)

    context = {
        "form": form,
        "page_title": "Nova transação",
    }
    return render(request, "finance/transaction_form.html", context)

@login_required
def transaction_update(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)

    if request.method == "POST":
        form = TransactionForm(request.POST, instance=transaction, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Transação atualizada com sucesso.")
            return redirect("finance_home")
    else:
        form = TransactionForm(instance=transaction, user=request.user)

    context = {
        "form": form,
        "page_title": "Editar transação",
    }
    print("USER:", request.user)
    print("CATEGORIES:", list(form.fields["category"].queryset))
    print("ACCOUNTS:", list(form.fields["account"].queryset))
    print("TAGS:", list(form.fields["tags"].queryset))
    return render(request, "finance/transaction_form.html", context)

@login_required
def transaction_delete(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)

    if request.method == "POST":
        transaction.delete()
        messages.success(request, "Transação removida com sucesso.")
        return redirect("finance_home")

    return render(request, "finance/transaction_confirm_delete.html", {
        "object": transaction
    })


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

    context = {
        "transactions": qs,
        "search": search or "",
        "selected_type": transaction_type or "",
        "selected_category": category_id or "",
        "selected_account": account_id or "",
        "categories": Category.objects.filter(user=request.user).order_by("name"),
        "accounts": Account.objects.filter(user=request.user).order_by("name"),
    }
    return render(request, "finance/transaction_list.html", context)


# CATEGORY CRUD
@login_required
def category_list(request):
    categories = Category.objects.filter(user=request.user).order_by("type", "name")
    return render(request, "finance/category_list.html", {"categories": categories})


@login_required
def category_create(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, "Categoria cadastrada com sucesso.")
            return redirect("category_list")
    else:
        form = CategoryForm()

    return render(request, "finance/category_form.html", {
        "form": form,
        "title": "Nova categoria",
        "submit_label": "Salvar categoria",
    })


@login_required
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)

    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Categoria atualizada com sucesso.")
            return redirect("category_list")
    else:
        form = CategoryForm(instance=category)

    return render(request, "finance/category_form.html", {
        "form": form,
        "title": "Editar categoria",
        "submit_label": "Salvar alterações",
    })


@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)

    if request.method == "POST":
        try:
            category.delete()
            messages.success(request, "Categoria removida com sucesso.")
        except ProtectedError:
            messages.error(
                request,
                "Não é possível excluir esta categoria porque ela está vinculada a transações."
            )
        return redirect("category_list")

    return render(request, "finance/category_confirm_delete.html", {"object": category})


# =========================
# ACCOUNT CRUD
# =========================

@login_required
def account_list(request):
    accounts = Account.objects.filter(user=request.user).order_by("name")
    return render(request, "finance/account_list.html", {"accounts": accounts})


@login_required
def account_create(request):
    if request.method == "POST":
        form = AccountForm(request.POST)
        if form.is_valid():
            account = form.save(commit=False)
            account.user = request.user
            account.save()
            messages.success(request, "Conta cadastrada com sucesso.")
            return redirect("account_list")
    else:
        form = AccountForm()

    return render(request, "finance/account_form.html", {
        "form": form,
        "title": "Nova conta",
        "submit_label": "Salvar conta",
    })


@login_required
def account_update(request, pk):
    account = get_object_or_404(Account, pk=pk, user=request.user)

    if request.method == "POST":
        form = AccountForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            messages.success(request, "Conta atualizada com sucesso.")
            return redirect("account_list")
    else:
        form = AccountForm(instance=account)

    return render(request, "finance/account_form.html", {
        "form": form,
        "title": "Editar conta",
        "submit_label": "Salvar alterações",
    })


@login_required
def account_delete(request, pk):
    account = get_object_or_404(Account, pk=pk, user=request.user)

    if request.method == "POST":
        try:
            account.delete()
            messages.success(request, "Conta removida com sucesso.")
        except ProtectedError:
            messages.error(
                request,
                "Não é possível excluir esta conta porque ela está vinculada a transações."
            )
        return redirect("account_list")

    return render(request, "finance/account_confirm_delete.html", {"object": account})


# =========================
# TAG CRUD
# =========================

@login_required
def tag_list(request):
    tags = Tag.objects.filter(user=request.user).order_by("name")
    return render(request, "finance/tag_list.html", {"tags": tags})


@login_required
def tag_create(request):
    if request.method == "POST":
        form = TagForm(request.POST)
        if form.is_valid():
            tag = form.save(commit=False)
            tag.user = request.user
            tag.save()
            messages.success(request, "Tag cadastrada com sucesso.")
            return redirect("tag_list")
    else:
        form = TagForm()

    return render(request, "finance/tag_form.html", {
        "form": form,
        "title": "Nova tag",
        "submit_label": "Salvar tag",
    })


@login_required
def tag_update(request, pk):
    tag = get_object_or_404(Tag, pk=pk, user=request.user)

    if request.method == "POST":
        form = TagForm(request.POST, instance=tag)
        if form.is_valid():
            form.save()
            messages.success(request, "Tag atualizada com sucesso.")
            return redirect("tag_list")
    else:
        form = TagForm(instance=tag)

    return render(request, "finance/tag_form.html", {
        "form": form,
        "title": "Editar tag",
        "submit_label": "Salvar alterações",
    })


@login_required
def tag_delete(request, pk):
    tag = get_object_or_404(Tag, pk=pk, user=request.user)

    if request.method == "POST":
        tag.delete()
        messages.success(request, "Tag removida com sucesso.")
        return redirect("tag_list")

    return render(request, "finance/tag_confirm_delete.html", {"object": tag})