from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class Category(models.Model):
    INCOME = "income"
    EXPENSE = "expense"

    TYPE_CHOICES = (
        (INCOME, "Receita"),
        (EXPENSE, "Despesa"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="finance_categories")
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    color = models.CharField(max_length=7, blank=True)
    icon = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        unique_together = ("user", "name", "type")

    def __str__(self):
        return self.name


class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="finance_accounts")
    name = models.CharField(max_length=100)
    initial_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        unique_together = ("user", "name")

    def __str__(self):
        return self.name


class Tag(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="finance_tags")
    name = models.CharField(max_length=50)

    class Meta:
        ordering = ["name"]
        unique_together = ("user", "name")

    def __str__(self):
        return self.name


class Transaction(models.Model):
    INCOME = "income"
    EXPENSE = "expense"

    TYPE_CHOICES = (
        (INCOME, "Receita"),
        (EXPENSE, "Despesa"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="finance_transactions")
    description = models.CharField(max_length=255)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="transactions")
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name="transactions")
    tags = models.ManyToManyField(Tag, blank=True, related_name="transactions")
    date = models.DateField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def clean(self):
        if self.category_id and self.category.type != self.type:
            raise ValidationError({
                "category": "A categoria deve ter o mesmo tipo da transação."
            })

    def __str__(self):
        return f"{self.description} - {self.amount}"