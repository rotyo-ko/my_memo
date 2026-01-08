from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView

from .forms import CustomUserCreationForm

class CustomSignupView(CreateView):
    template_name = "accounts/signup.html"
    form_class = CustomUserCreationForm
    success_url=reverse_lazy("accounts:login")


class CustomLoginView(LoginView):
    template_name = "accounts/login.html"

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("memo:memo")
    

