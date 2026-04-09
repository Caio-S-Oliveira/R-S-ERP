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
            "bought_price",
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
            "bought_price": forms.NumberInput(attrs={
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

    def clean_quantity(self):
        quantity = self.cleaned_data.get("quantity")
        if quantity is not None and quantity < 1:
            raise forms.ValidationError("A quantidade deve ser no mínimo 1.")
        return quantity

    def clean(self):
        cleaned_data = super().clean()

        desired_price = cleaned_data.get("desired_price")
        current_price = cleaned_data.get("current_price")
        bought_price = cleaned_data.get("bought_price")
        status = cleaned_data.get("status")

        for field_name, value in {
            "desired_price": desired_price,
            "current_price": current_price,
            "bought_price": bought_price,
        }.items():
            if value is not None and value < 0:
                self.add_error(field_name, "O valor não pode ser negativo.")

        if status == "bought" and not bought_price and not current_price and not desired_price:
            raise forms.ValidationError(
                "Para marcar como comprado, informe pelo menos um valor "
                "(comprado, atual ou desejado)."
            )

        return cleaned_data