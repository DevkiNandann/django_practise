from django.urls import path
from new_app.view.views import LoginUser, LogoutUser, Signup, LiveStream, ChangePasswordUser, UserProfile, ForgotPasswordEmail, ForgotPasswordOtp, ValidateOtp, ResetPassword, RedirectEmail


urlpatterns = [
    path("", LoginUser.as_view(), name=""),
    path("login", LoginUser.as_view(), name="login"),
    path("logout", LogoutUser.as_view(), name="logout"),
    path("signup", Signup.as_view(), name="signup"),
    path("live_stream", LiveStream.as_view(), name="live_stream"),
    path("change_password", ChangePasswordUser.as_view(), name="change_password"),
    path("user_profile", UserProfile.as_view(), name="user_profile"),
    path(
        "forgot_password_email",
        ForgotPasswordEmail.as_view(),
        name="forgot_password_email",
    ),
    path(
        "forgot_password_otp",
        ForgotPasswordOtp.as_view(),
        name="forgot_password_otp",
    ),
    path("validate_otp", ValidateOtp.as_view(), name="validate_otp"),
    path("reset_password", ResetPassword.as_view(), name="reset_password"),
    path(
        "redirect_email/<int:user_id>",
        RedirectEmail.as_view(),
        name="redirect_email",
    ),
]
