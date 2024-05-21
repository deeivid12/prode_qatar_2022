from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy


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

class PasswordChangeView(PasswordChangeView):
    form_class = PasswordChangeForm
    success_url = reverse_lazy('welcome')

    def form_valid(self, form):
        messages.success(self.request, 'Ha cambiado su password correctamente')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Error al cambiar password')
        return super().form_invalid(form)
