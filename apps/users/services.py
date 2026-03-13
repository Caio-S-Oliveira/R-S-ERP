from django.contrib.auth.hashers import make_password
from .models import User

def create_user(email: str, password: str):
    user = User.objects.create(
        email=email,
        password=make_password(password)
    )
    return user