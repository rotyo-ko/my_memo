from django.urls import path

from .views import CustomSignupView, CustomLoginView, CustomLogoutView

app_name = "accounts"
urlpatterns = [
    path("signup/", CustomSignupView.as_view(),
        name="signup"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    
]