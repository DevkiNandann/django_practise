from django.urls import path
from . import views


urlpatterns = [
    path("login", views.LoginUser.as_view(), name="login"),
    path("logout", views.LogoutUser.as_view(), name="logout"),
    path("signup", views.Signup.as_view(), name="signup"),
    path("change_password", views.ChangePaswordUser.as_view(), name="change_password"),
    path("user_detail", views.UserDetail.as_view(), name="user_detail"),
]
