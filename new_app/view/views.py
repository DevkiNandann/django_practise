from . import v1
from . import v2
from rest_framework import generics


class UserProfile(generics.GenericAPIView):
    def dispatch(self, request, *args, **kwargs):

        if request.META.get("HTTP_X_API_VERSION") == "v2":
            view = v2.UserProfile.as_view()
        else:
            view = v1.UserProfile.as_view()

        return view(request, *args, **kwargs)


class Signup(generics.GenericAPIView):
    def dispatch(self, request, *args, **kwargs):

        if request.META.get("HTTP_X_API_VERSION") == "v2":
            view = v2.Signup.as_view()
        else:
            view = v1.Signup.as_view()

        return view(request, *args, **kwargs)


class LoginUser(generics.GenericAPIView):
    def dispatch(self, request, *args, **kwargs):

        view = v1.LoginUser.as_view()
        return view(request, *args, **kwargs)


class LogoutUser(generics.GenericAPIView):
    def dispatch(self, request, *args, **kwargs):

        view = v1.LogoutUser.as_view()
        return view(request, *args, **kwargs)


class ChangePasswordUser(generics.GenericAPIView):
    def dispatch(self, request, *args, **kwargs):

        view = v1.ChangePasswordUser.as_view()
        return view(request, *args, **kwargs)
