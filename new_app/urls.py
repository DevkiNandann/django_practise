from django.urls import path
from new_app.view import views


urlpatterns = [
    path("login", views.LoginUser.as_view(), name="login"),
    path("logout", views.LogoutUser.as_view(), name="logout"),
    path("signup", views.Signup.as_view(), name="signup"),
    path("change_password", views.ChangePasswordUser.as_view(), name="change_password"),
    path("user_profile", views.UserProfile.as_view(), name="user_profile"),
    path(
        "forgot_password_email",
        views.ForgotPasswordEmail.as_view(),
        name="forgot_password_email",
    ),
    path(
        "forgot_password_otp",
        views.ForgotPasswordOtp.as_view(),
        name="forgot_password_otp",
    ),
    path("validate_otp", views.ValidateOtp.as_view(), name="validate_otp"),
    path("reset_password", views.ResetPassword.as_view(), name="reset_password"),
    path(
        "redirect_email/<int:user_id>",
        views.RedirectEmail.as_view(),
        name="redirect_email",
    ),
    path(
        "edit_profile",
        views.EditUserProfile.as_view(),
        name="edit_profile",
    ),
]
