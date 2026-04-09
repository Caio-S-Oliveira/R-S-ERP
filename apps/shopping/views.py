from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import (
    Count,
    Sum,
    Value,
    DecimalField,
    F,
    ExpressionWrapper,
    Case,
    When,
    IntegerField,
    Q,
)
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import ShoppingListForm, ShoppingItemForm
from .models import ShoppingList, ShoppingItem
from .services import create_financial_transaction_for_shopping_item


@login_required
def shopping_list_list(request):
    lists = (
        ShoppingList.objects
        .filter(user=request.user)
        .annotate(
            items_count=Count("items"),
            bought_items_count=Count("items", filter=Q(items__status="bought")),
            waiting_items_count=Count("items", filter=Q(items__status="waiting")),
        )
        .order_by("-created_at")
    )

    return render(request, "shopping/list_list.html", {
        "lists": lists
    })


@login_required
def shopping_list_create(request):
    if request.method == "POST":
        form = ShoppingListForm(request.POST)
        if form.is_valid():
            shopping_list = form.save(commit=False)
            shopping_list.user = request.user
            shopping_list.save()
            messages.success(request, "Lista criada com sucesso.")
            return redirect("shopping_list_detail", pk=shopping_list.pk)
    else:
        form = ShoppingListForm()

    return render(request, "shopping/list_form.html", {
        "form": form,
        "title": "Nova lista",
        "submit_label": "Salvar lista",
    })


@login_required
def shopping_list_update(request, pk):
    shopping_list = get_object_or_404(ShoppingList, pk=pk, user=request.user)

    if request.method == "POST":
        form = ShoppingListForm(request.POST, instance=shopping_list)
        if form.is_valid():
            form.save()
            messages.success(request, "Lista atualizada com sucesso.")
            return redirect("shopping_list_detail", pk=shopping_list.pk)
    else:
        form = ShoppingListForm(instance=shopping_list)

    return render(request, "shopping/list_form.html", {
        "form": form,
        "title": "Editar lista",
        "submit_label": "Salvar alterações",
    })


@login_required
def shopping_list_delete(request, pk):
    shopping_list = get_object_or_404(ShoppingList, pk=pk, user=request.user)

    if request.method == "POST":
        shopping_list.delete()
        messages.success(request, "Lista removida com sucesso.")
        return redirect("shopping_list_list")

    return render(request, "shopping/list_confirm_delete.html", {
        "object": shopping_list
    })


@login_required
def shopping_list_detail(request, pk):
    shopping_list = get_object_or_404(ShoppingList, pk=pk, user=request.user)

    status_filter = request.GET.get("status", "").strip()
    priority_filter = request.GET.get("priority", "").strip()
    category_filter = request.GET.get("category", "").strip()
    search = request.GET.get("search", "").strip()

    items = shopping_list.items.all()

    if status_filter:
        items = items.filter(status=status_filter)

    if priority_filter:
        items = items.filter(priority=priority_filter)

    if category_filter:
        items = items.filter(category=category_filter)

    if search:
        items = items.filter(
            Q(name__icontains=search) |
            Q(store_name__icontains=search) |
            Q(notes__icontains=search)
        )

    status_order = Case(
        When(status="wanted", then=Value(1)),
        When(status="researching", then=Value(2)),
        When(status="waiting", then=Value(3)),
        When(status="bought", then=Value(4)),
        When(status="cancelled", then=Value(5)),
        default=Value(99),
        output_field=IntegerField(),
    )

    priority_order = Case(
        When(priority="high", then=Value(1)),
        When(priority="medium", then=Value(2)),
        When(priority="low", then=Value(3)),
        default=Value(99),
        output_field=IntegerField(),
    )

    items = items.annotate(
        desired_total_calc=ExpressionWrapper(
            F("desired_price") * F("quantity"),
            output_field=DecimalField(max_digits=14, decimal_places=2),
        ),
        current_total_calc=ExpressionWrapper(
            F("current_price") * F("quantity"),
            output_field=DecimalField(max_digits=14, decimal_places=2),
        ),
        bought_total_calc=ExpressionWrapper(
            F("bought_price") * F("quantity"),
            output_field=DecimalField(max_digits=14, decimal_places=2),
        ),
        status_order=status_order,
        priority_order=priority_order,
    ).order_by("status_order", "priority_order", "-created_at", "name")

    all_items = shopping_list.items.all()

    desired_total_expr = ExpressionWrapper(
        F("desired_price") * F("quantity"),
        output_field=DecimalField(max_digits=14, decimal_places=2),
    )

    current_total_expr = ExpressionWrapper(
        F("current_price") * F("quantity"),
        output_field=DecimalField(max_digits=14, decimal_places=2),
    )

    bought_total_expr = ExpressionWrapper(
        F("bought_price") * F("quantity"),
        output_field=DecimalField(max_digits=14, decimal_places=2),
    )

    total_items = all_items.count()
    bought_items = all_items.filter(status="bought").count()
    waiting_items = all_items.filter(status="waiting").count()

    desired_total = all_items.aggregate(
        total=Coalesce(
            Sum(desired_total_expr),
            Value(Decimal("0.00")),
            output_field=DecimalField(max_digits=14, decimal_places=2),
        )
    )["total"]

    current_total = all_items.aggregate(
        total=Coalesce(
            Sum(current_total_expr),
            Value(Decimal("0.00")),
            output_field=DecimalField(max_digits=14, decimal_places=2),
        )
    )["total"]

    bought_total = all_items.filter(status="bought").aggregate(
        total=Coalesce(
            Sum(bought_total_expr),
            Value(Decimal("0.00")),
            output_field=DecimalField(max_digits=14, decimal_places=2),
        )
    )["total"]

    categories = ShoppingItem.CATEGORY_CHOICES
    priorities = ShoppingItem.PRIORITY_CHOICES
    statuses = ShoppingItem.STATUS_CHOICES

    return render(request, "shopping/list_detail.html", {
        "shopping_list": shopping_list,
        "items": items,
        "total_items": total_items,
        "bought_items": bought_items,
        "waiting_items": waiting_items,
        "desired_total": desired_total,
        "current_total": current_total,
        "bought_total": bought_total,
        "categories": categories,
        "priorities": priorities,
        "statuses": statuses,
        "selected_status": status_filter,
        "selected_priority": priority_filter,
        "selected_category": category_filter,
        "search": search,
    })


@login_required
def shopping_item_create(request, list_pk):
    shopping_list = get_object_or_404(ShoppingList, pk=list_pk, user=request.user)

    if request.method == "POST":
        form = ShoppingItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.shopping_list = shopping_list

            if item.status == "bought" and not item.bought_at:
                item.bought_at = timezone.now()

            if item.status == "bought" and item.bought_price is None:
                item.bought_price = item.current_price or item.desired_price

            item.save()

            if item.status == "bought":
                created, msg = create_financial_transaction_for_shopping_item(item)
                if created:
                    messages.success(request, f"Item adicionado e compra registrada no financeiro. {msg}")
                else:
                    messages.warning(request, f"Item adicionado, mas a transação financeira não foi criada. {msg}")
            else:
                messages.success(request, "Item adicionado com sucesso.")

            return redirect("shopping_list_detail", pk=shopping_list.pk)
    else:
        form = ShoppingItemForm()

    return render(request, "shopping/item_form.html", {
        "form": form,
        "shopping_list": shopping_list,
        "title": "Novo item",
        "submit_label": "Salvar item",
    })


@login_required
def shopping_item_update(request, pk):
    item = get_object_or_404(
        ShoppingItem.objects.select_related("shopping_list"),
        pk=pk,
        shopping_list__user=request.user
    )

    old_status = item.status

    if request.method == "POST":
        form = ShoppingItemForm(request.POST, instance=item)
        if form.is_valid():
            item = form.save(commit=False)

            if item.status == "bought" and not item.bought_at:
                item.bought_at = timezone.now()

            if item.status == "bought" and item.bought_price is None:
                item.bought_price = item.current_price or item.desired_price

            item.save()

            if old_status != "bought" and item.status == "bought":
                created, msg = create_financial_transaction_for_shopping_item(item)
                if created:
                    messages.success(request, f"Item atualizado e transação financeira criada. {msg}")
                else:
                    messages.warning(request, f"Item atualizado, mas a transação financeira não foi criada. {msg}")
            else:
                messages.success(request, "Item atualizado com sucesso.")

            return redirect("shopping_list_detail", pk=item.shopping_list.pk)
    else:
        form = ShoppingItemForm(instance=item)

    return render(request, "shopping/item_form.html", {
        "form": form,
        "shopping_list": item.shopping_list,
        "title": "Editar item",
        "submit_label": "Salvar alterações",
    })


@login_required
def shopping_item_delete(request, pk):
    item = get_object_or_404(
        ShoppingItem.objects.select_related("shopping_list"),
        pk=pk,
        shopping_list__user=request.user
    )

    if request.method == "POST":
        list_pk = item.shopping_list.pk
        item.delete()
        messages.success(request, "Item removido com sucesso.")
        return redirect("shopping_list_detail", pk=list_pk)

    return render(request, "shopping/item_confirm_delete.html", {
        "object": item
    })

@login_required
@require_POST
def shopping_item_change_status(request, pk, status):
    item = get_object_or_404(
        ShoppingItem.objects.select_related("shopping_list"),
        pk=pk,
        shopping_list__user=request.user
    )

    valid_status = dict(ShoppingItem.STATUS_CHOICES).keys()
    if status not in valid_status:
        messages.error(request, "Status inválido.")
        return redirect("shopping_list_detail", pk=item.shopping_list.pk)

    old_status = item.status
    item.status = status

    update_fields = ["status"]

    if status == "bought" and not item.bought_at:
        item.bought_at = timezone.now()
        update_fields.append("bought_at")

    if status == "bought" and item.bought_price is None:
        item.bought_price = item.current_price or item.desired_price
        update_fields.append("bought_price")

    item.save(update_fields=update_fields)

    if old_status != "bought" and status == "bought":
        created, msg = create_financial_transaction_for_shopping_item(item)
        if created:
            messages.success(request, f"Status atualizado para comprado. {msg}")
        else:
            messages.warning(
                request,
                f"Status atualizado para comprado, mas a transação financeira não foi criada. {msg}"
            )
    else:
        messages.success(request, "Status do item atualizado.")

    return redirect("shopping_list_detail", pk=item.shopping_list.pk)