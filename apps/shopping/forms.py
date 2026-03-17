from django import forms
from .models import ShoppingList, ShoppingItem


class ShoppingListForm(forms.ModelForm):
    class Meta:
        model = ShoppingList
        fields = ["name", "description"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex: Wishlist Tech, Livros, Compras da Casa"
            }),
            "description": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Descrição opcional"
            }),
        }


class ShoppingItemForm(forms.ModelForm):
    class Meta:
        model = ShoppingItem
        fields = [
            "name",
            "category",
            "store_name",
            "product_url",
            "quantity",
            "desired_price",
            "current_price",
            "priority",
            "status",
            "notes",
        ]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nome do item"
            }),
            "category": forms.Select(attrs={"class": "form-select"}),
            "store_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex: Amazon, Kabum, Mercado Livre"
            }),
            "product_url": forms.URLInput(attrs={
                "class": "form-control",
                "placeholder": "https://..."
            }),
            "quantity": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "1"
            }),
            "desired_price": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "placeholder": "0.00"
            }),
            "current_price": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "placeholder": "0.00"
            }),
            "priority": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "notes": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Observações"
            }),
        }