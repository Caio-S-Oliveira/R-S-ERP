from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ShoppingList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="shopping_lists")
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ShoppingItem(models.Model):
    CATEGORY_CHOICES = (
        ("electronics", "Eletrônicos"),
        ("books", "Livros"),
        ("home", "Casa"),
        ("fashion", "Roupas"),
        ("games", "Games"),
        ("office", "Escritório"),
        ("online", "Compras online"),
        ("other", "Outros"),
    )

    STATUS_CHOICES = (
        ("wanted", "Quero comprar"),
        ("researching", "Pesquisando"),
        ("waiting", "Aguardando promoção"),
        ("bought", "Comprado"),
        ("cancelled", "Cancelado"),
    )

    PRIORITY_CHOICES = (
        ("low", "Baixa"),
        ("medium", "Média"),
        ("high", "Alta"),
    )

    shopping_list = models.ForeignKey(
        ShoppingList,
        on_delete=models.CASCADE,
        related_name="items"
    )
    name = models.CharField(max_length=150)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default="other")
    store_name = models.CharField(max_length=100, blank=True)
    product_url = models.URLField(blank=True)
    quantity = models.PositiveIntegerField(default=1)
    desired_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    current_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="medium")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="wanted")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name