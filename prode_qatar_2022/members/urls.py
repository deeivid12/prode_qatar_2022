from django.contrib.auth import views as auth_views
from django.urls import path
from members import views

urlpatterns = [
    path("login", views.login_user, name="login"),
    path("logout_user", views.logout_user, name="logout"),
    path("register", views.register_user, name="register"),
    path("password", views.PasswordChangeView.as_view(template_name='auth/change-password.html'), name="change_password"),
]
