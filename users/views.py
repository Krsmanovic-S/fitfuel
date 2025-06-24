from django.shortcuts import render
from .forms import RegisterForm, LoginForm


def register(request):
    register_form = RegisterForm()
    return render(request, 'users/register.html', {'register_form': register_form})


def login(request):
    login_form = LoginForm()
    return render(request, 'users/login.html', {'login_form': login_form})