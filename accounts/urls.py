from django.urls import path

from .views import (activate, forgot_password, login, logout, profile,
                    registerUser, reset_password, reset_password_validate)

app_name = "accounts"

urlpatterns = [
    path("registerUser/", registerUser, name="registerUser"),
    path("login/", login, name="login"),
    path("logout/", logout, name="logout"),
    path("activate/<uidb64>/<token>", activate, name="activate"),
    path("forgot_password/", forgot_password, name="forgot_password"),
    path(
        "reset_password_validate/<uidb64>/<token>/",
        reset_password_validate,
        name="reset_password_validate",
    ),
    path("reset_password/", reset_password, name="reset_password"),
    path("profile/", profile, name="profile"),
]
