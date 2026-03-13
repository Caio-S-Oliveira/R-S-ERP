from .models import User

def get_user_by_email(email: str):
    return User.objects.filter(email=email).first()

def list_users():
    return User.objects.all()