from django.urls import path
from members import views

urlpatterns = [
    path('login_user', views.login_user, name="login"),
	path('register_user', views.register_user, name="register"),
]
