from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm


def login_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("welcome")
        else:
            messages.warning(
                request,
                "Usuario y/o password incorrecto. Por favor intente nuevamente.",
            )
            return redirect("login")
    return render(request, "auth/login.html", {})


def register_user(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Usuario creado correctamente.",
            )
            return redirect("login")
        else:
            messages.error(
                request,
                "Error al crear usuario.",
            )
            return redirect("register")
        data = {"form": form}
    else:
        form = UserCreationForm()
        data = {"form": form}
    return render(request, "auth/register.html", data)


def logout_user(request):
    logout(request)
    messages.success(request, ("Sesión cerrada correctamente"))
    return redirect("login")
