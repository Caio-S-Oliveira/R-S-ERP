from django import forms
from .models import Transaction, Category, Account, Tag


class TransactionForm(forms.ModelForm):
    TRANSACTION_MODE_CHOICES = (
        ("single", "Lançamento único"),
        ("installment", "Compra parcelada"),
        ("recurring", "Lançamento recorrente"),
    )

    transaction_mode = forms.ChoiceField(
        label="Modo de lançamento",
        choices=TRANSACTION_MODE_CHOICES,
        initial="single",
        required=False,
        widget=forms.Select(attrs={"class": "form-select"})
    )

    installments = forms.IntegerField(
        label="Parcelas",
        min_value=1,
        initial=1,
        required=False,
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "1",
            "min": "1",
        })
    )

    recurrence_count = forms.IntegerField(
        label="Quantidade de repetições",
        min_value=1,
        initial=1,
        required=False,
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "1",
            "min": "1",
        })
    )

    recurrence_frequency = forms.ChoiceField(
        label="Frequência",
        choices=Transaction.RECURRENCE_FREQUENCY_CHOICES,
        initial="monthly",
        required=False,
        widget=forms.Select(attrs={"class": "form-select"})
    )

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
            "is_paid",
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
            "is_paid": forms.CheckboxInput(attrs={
                "class": "form-check-input"
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

        if self.instance and self.instance.pk:
            self.fields["transaction_mode"].initial = self.instance.schedule_type or "single"
            self.fields["installments"].initial = self.instance.series_total or 1
            self.fields["recurrence_count"].initial = self.instance.series_total or 1
            self.fields["recurrence_frequency"].initial = self.instance.recurrence_frequency or "monthly"

    def clean_installments(self):
        installments = self.cleaned_data.get("installments") or 1
        if installments < 1:
            raise forms.ValidationError("A quantidade de parcelas deve ser no mínimo 1.")
        return installments

    def clean_recurrence_count(self):
        recurrence_count = self.cleaned_data.get("recurrence_count") or 1
        if recurrence_count < 1:
            raise forms.ValidationError("A quantidade de repetições deve ser no mínimo 1.")
        return recurrence_count

    def clean(self):
        cleaned_data = super().clean()

        transaction_type = cleaned_data.get("type")
        category = cleaned_data.get("category")
        transaction_mode = cleaned_data.get("transaction_mode") or "single"
        installments = cleaned_data.get("installments") or 1
        recurrence_count = cleaned_data.get("recurrence_count") or 1
        recurrence_frequency = cleaned_data.get("recurrence_frequency") or "monthly"

        if category and transaction_type and category.type != transaction_type:
            self.add_error("category", "A categoria precisa ter o mesmo tipo da transação.")

        if transaction_mode == "installment" and installments < 2:
            self.add_error("installments", "Para parcelamento, informe no mínimo 2 parcelas.")

        if transaction_mode == "recurring":
            if recurrence_count < 2:
                self.add_error("recurrence_count", "Para recorrência, informe no mínimo 2 repetições.")
            if recurrence_frequency not in dict(Transaction.RECURRENCE_FREQUENCY_CHOICES):
                self.add_error("recurrence_frequency", "Selecione uma frequência válida.")

        return cleaned_data