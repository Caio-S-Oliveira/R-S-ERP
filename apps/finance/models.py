import uuid

from django.conf import settings
from django.db import models


class BaseOwnedModel(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="%(class)ss"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(BaseOwnedModel):
    TYPE_CHOICES = (
        ("income", "Receita"),
        ("expense", "Despesa"),
    )

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    color = models.CharField(max_length=20, blank=True, default="#0d6efd")
    icon = models.CharField(max_length=50, blank=True, default="")

    class Meta:
        ordering = ["name"]
        unique_together = ("user", "name", "type")

    def __str__(self):
        return self.name


class Account(BaseOwnedModel):
    name = models.CharField(max_length=100)
    initial_balance = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        ordering = ["name"]
        unique_together = ("user", "name")

    def __str__(self):
        return self.name


class Tag(BaseOwnedModel):
    name = models.CharField(max_length=60)

    class Meta:
        ordering = ["name"]
        unique_together = ("user", "name")

    def __str__(self):
        return self.name


class Transaction(BaseOwnedModel):
    TYPE_CHOICES = (
        ("income", "Receita"),
        ("expense", "Despesa"),
    )

    SCHEDULE_TYPE_CHOICES = (
        ("single", "Lançamento único"),
        ("installment", "Parcelado"),
        ("recurring", "Recorrente"),
    )

    RECURRENCE_FREQUENCY_CHOICES = (
        ("monthly", "Mensal"),
        ("yearly", "Anual"),
    )

    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="transactions"
    )
    account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name="transactions"
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="transactions")
    date = models.DateField()
    notes = models.TextField(blank=True, default="")

    is_paid = models.BooleanField(default=True)

    schedule_type = models.CharField(
        max_length=20,
        choices=SCHEDULE_TYPE_CHOICES,
        default="single"
    )
    recurrence_frequency = models.CharField(
        max_length=20,
        choices=RECURRENCE_FREQUENCY_CHOICES,
        blank=True,
        default=""
    )

    series_group = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
        editable=False
    )
    series_position = models.PositiveIntegerField(default=1)
    series_total = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return self.description

    @property
    def is_series(self):
        return bool(self.series_group)

    @property
    def series_label(self):
        if self.series_total and self.series_total > 1:
            return f"{self.series_position}/{self.series_total}"
        return ""

    @property
    def schedule_label(self):
        return dict(self.SCHEDULE_TYPE_CHOICES).get(self.schedule_type, self.schedule_type)