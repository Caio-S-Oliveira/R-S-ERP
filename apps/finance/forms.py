from django import forms
from .models import Transaction, Category, Account, Tag


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = [
            "type",
            "description",
            "amount",
            "category",
            "account",
            "tags",
            "date",
            "notes",
        ]
        widgets = {
            "type": forms.Select(attrs={"class": "form-select"}),
            "description": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex: Salário, Mercado, Gasolina..."
            }),
            "amount": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "0.00",
                "step": "0.01"
            }),
            "category": forms.Select(attrs={"class": "form-select"}),
            "account": forms.Select(attrs={"class": "form-select"}),
            "tags": forms.SelectMultiple(attrs={"class": "form-select"}),
            "date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date"
            }),
            "notes": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Observações opcionais"
            }),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["category"].queryset = Category.objects.none()
        self.fields["account"].queryset = Account.objects.none()
        self.fields["tags"].queryset = Tag.objects.none()

        if user and user.is_authenticated:
            self.fields["category"].queryset = Category.objects.filter(user=user).order_by("name")
            self.fields["account"].queryset = Account.objects.filter(user=user).order_by("name")
            self.fields["tags"].queryset = Tag.objects.filter(user=user).order_by("name")

            self.fields["category"].empty_label = "Selecione uma categoria"
            self.fields["account"].empty_label = "Selecione uma conta"

    def clean(self):
        cleaned_data = super().clean()
        transaction_type = cleaned_data.get("type")
        category = cleaned_data.get("category")

        if category and transaction_type and category.type != transaction_type:
            self.add_error("category", "A categoria precisa ter o mesmo tipo da transação.")

        return cleaned_data