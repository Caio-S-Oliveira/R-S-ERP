from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Value, DecimalField
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ShoppingListForm, ShoppingItemForm
from .models import ShoppingList, ShoppingItem


@login_required
def shopping_list_list(request):
    lists = (
        ShoppingList.objects
        .filter(user=request.user)
        .annotate(items_count=Count("items"))
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

    items = shopping_list.items.all().order_by("status", "-created_at", "name")

    total_items = items.count()
    bought_items = items.filter(status="bought").count()
    waiting_items = items.filter(status="waiting").count()

    desired_total = (
        items.aggregate(
            total=Coalesce(
                Sum("desired_price"),
                Value(Decimal("0.00")),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            )
        )["total"]
    )

    current_total = (
        items.aggregate(
            total=Coalesce(
                Sum("current_price"),
                Value(Decimal("0.00")),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            )
        )["total"]
    )

    return render(request, "shopping/list_detail.html", {
        "shopping_list": shopping_list,
        "items": items,
        "total_items": total_items,
        "bought_items": bought_items,
        "waiting_items": waiting_items,
        "desired_total": desired_total,
        "current_total": current_total,
    })


@login_required
def shopping_item_create(request, list_pk):
    shopping_list = get_object_or_404(ShoppingList, pk=list_pk, user=request.user)

    if request.method == "POST":
        form = ShoppingItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.shopping_list = shopping_list
            item.save()
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

    if request.method == "POST":
        form = ShoppingItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
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
def shopping_item_change_status(request, pk, status):
    item = get_object_or_404(
        ShoppingItem.objects.select_related("shopping_list"),
        pk=pk,
        shopping_list__user=request.user
    )

    valid_status = dict(ShoppingItem.STATUS_CHOICES).keys()
    if status in valid_status:
        item.status = status
        item.save(update_fields=["status"])
        messages.success(request, "Status do item atualizado.")

    return redirect("shopping_list_detail", pk=item.shopping_list.pk)