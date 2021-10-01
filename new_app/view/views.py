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


class ForgotPasswordEmail(generics.GenericAPIView):
    def dispatch(self, request, *args, **kwargs):

        view = v1.ForgotPasswordEmail.as_view()
        return view(request, *args, **kwargs)


class ForgotPasswordOtp(generics.GenericAPIView):
    def dispatch(self, request, *args, **kwargs):

        view = v1.ForgotPasswordOtp.as_view()
        return view(request, *args, **kwargs)


class ValidateOtp(generics.GenericAPIView):
    def dispatch(self, request, *args, **kwargs):

        view = v1.ValidateOtp.as_view()
        return view(request, *args, **kwargs)


class ResetPassword(generics.GenericAPIView):
    def dispatch(self, request, *args, **kwargs):

        view = v1.ResetPassword.as_view()
        return view(request, *args, **kwargs)


class RedirectEmail(generics.GenericAPIView):
    def dispatch(self, request, *args, **kwargs):

        view = v1.RedirectEmail.as_view()
        return view(request, *args, **kwargs)

class CreateCheckoutSession(generics.GenericAPIView):
    def dispatch(self, request, *args, **kwargs):

        view = v2.CreateCheckoutSession.as_view()
        return view(request, *args, **kwargs)


class CheckoutSuccess(generics.GenericAPIView):
    def dispatch(self, request, *args, **kwargs):

        view = v2.SuccessView.as_view()
        return view(request, *args, **kwargs)


class CheckoutCancel(generics.GenericAPIView):
    def dispatch(self, request, *args, **kwargs):

        view = v2.CancelView.as_view()
        return view(request, *args, **kwargs)


class CreateProduct(generics.GenericAPIView):
    def dispatch(self, request, *args, **kwargs):

        view = v2.CreateProduct.as_view()
        return view(request, *args, **kwargs)


class GetProduct(generics.GenericAPIView):
    def dispatch(self, request, *args, **kwargs):

        view = v2.GetProduct.as_view()
        return view(request, *args, **kwargs)


class SellProduct(generics.GenericAPIView):
    def dispatch(self, request, *args, **kwargs):

        view = v2.SellProduct.as_view()
        return view(request, *args, **kwargs)
