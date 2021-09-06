from django.urls import path
from new_app.view import views


urlpatterns = [
    path("login", views.LoginUser.as_view(), name="login"),
    path("logout", views.LogoutUser.as_view(), name="logout"),
    path("signup", views.Signup.as_view(), name="signup"),
    path("change_password", views.ChangePasswordUser.as_view(), name="change_password"),
    path("user_profile", views.UserProfile.as_view(), name="user_profile"),
]
