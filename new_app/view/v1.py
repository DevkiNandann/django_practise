from django.contrib.auth.hashers import make_password, check_password
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from new_app.models.user import User, Otp
from rest_framework.views import APIView
from new_app.serializers import Userserializer_v1
from django.utils import timezone
from django.utils.translation import gettext as _
from new_app import helpers
from django.shortcuts import render
from django.core.mail import send_mail
from new_project.settings import SENDING_EMAIL


class Signup(APIView):
    """
    API for new user to sign up
    """

    def post(self, request):
        email = request.data.get("email")
        phone_number = request.data.get("phone_number")
        user_id = request.data.get("user_id")
        password = request.data.get("password")
        confirm_password = request.data.get("confirm_password")

        if (
            not email
            or not phone_number
            or not user_id
            or not password
            or not confirm_password
        ):
            return Response(
                data={_("error"): _("Please enter all required fields")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(email=email).count() > 0:
            return Response(
                data={_("error"): _("This email already exist")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(phone_number=phone_number).count() > 0:
            return Response(
                data={_("error"): _("This phone number already exist")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if password != confirm_password:
            return Response(
                data={_("error"): _("Password and confirm password does not match")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        password_to_set = make_password(password)
        User.objects.create(
            user_id=user_id,
            email=email,
            phone_number=phone_number,
            password=password_to_set,
            date_created=timezone.now(),
        )
        return Response(
            data={
                _("message"): _("user created successfully"),
                _("user"): Userserializer_v1(request.data).data,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginUser(APIView):
    """
    API for the user to login
    """

    def post(self, request):
        if not request.data.get("email") or not request.data.get("password"):
            return Response(
                data={_("error"): _("Please enter all required fields")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(email=request.data["email"])
        if not user.count() > 0:
            return Response(
                data={_("error"): _("The user with this email does not exist")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = user.first()
        if not check_password(request.data["password"], user.password):
            return Response(
                data={_("error"): _("Either the email or password is incorrect")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        new_token, created = Token.objects.get_or_create(user=user)
        if new_token:
            response = {
                _("token"): str(new_token),
                _("user"): Userserializer_v1(user).data,
            }
            user.last_login = timezone.now()
            user.save()
            return Response(response, status=status.HTTP_201_CREATED)

        return Response(request.data, status=status.HTTP_400_BAD_REQUEST)


class LogoutUser(APIView):
    """
    API for the user to logout
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response(
            data={_("message"): _("User log out successfully")},
            status=status.HTTP_200_OK,
        )


class ChangePasswordUser(APIView):
    """
    API for user to change password
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = User.objects.get(phone_number=request.user)
        if user:
            new_password = request.data.get("new_password")
            confirm_new_password = request.data.get("confirm_new_password")
            password = request.data.get("old_password")

            if not password or not new_password or not confirm_new_password:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={_("error"): _("All the parameters are not given")},
                )

            if not check_password(password, user.password):
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={_("error"): _("Old password entered is incorrect")},
                )

            if new_password != confirm_new_password:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={
                        _("error"): _(
                            "New password and confirm new password does not match"
                        )
                    },
                )

            user.password = make_password(new_password)
            user.save()
            return Response(
                data={_("message"): _("Password changed successfully")},
                status=status.HTTP_200_OK,
            )


class UserProfile(APIView):
    """
    API to get user profile
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = User.objects.get(phone_number=request.user)
        serializer = Userserializer_v1(user).data
        return Response(data=serializer, status=status.HTTP_200_OK)


class ForgotPasswordEmail(APIView):
    def post(self, request):
        data = request.data
        email = data.get("email")

        if not email:
            return Response(
                data={_("error"): _("Please enter all required fields")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(email=email)
        if user.count() > 0:
            user = user.first().user_id

            url = f"localhost:8000/reset_password/{user}"

            send_mail(
                "Change your password",
                f"Please click on {url} to change your password",
                SENDING_EMAIL,
                [email],
            )
            return Response(
                data={_("message"): _("Mail to change password sent successfully")},
                status=status.HTTP_201_CREATED,
            )

        else:
            return Response(
                data={_("error"): _("No user assosciated with the email")},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ForgotPasswordOtp(APIView):
    def post(self, request):
        data = request.data
        phone_number = data.get("phone_number")
        country_code = data.get("country_code")
        otp = helpers.generate_otp()

        if not phone_number and not country_code:
            return Response(
                data={_("error"): _("Please enter all required fields")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        client = helpers.MessageClient()
        send_to = "+" + country_code + phone_number

        existing_otp = Otp.objects.filter(phone_number=send_to)
        if existing_otp.count() > 0:
            existing_otp = existing_otp.first()
            if (timezone.now() - existing_otp.date_created).seconds < 60:
                return Response(
                    data={_("error"): _("Please try after one minute")},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                existing_otp.otp = otp
                existing_otp.date_created = timezone.now()
                existing_otp.save()
                client.send_message(otp, send_to)

                return Response(
                    data={_("message"): _("Otp generated successfully")},
                    status=status.HTTP_201_CREATED,
                )

        client.send_message(otp, send_to)
        Otp.objects.create(phone_number=send_to, otp=otp, date_created=timezone.now())

        return Response(
            data={_("message"): _("Otp generated and sent successfully")},
            status=status.HTTP_201_CREATED,
        )


class ValidateOtp(APIView):
    """
    API to validate otp for forgot password
    """

    def post(self, request):
        otp = request.data.get("otp")
        phone_number = request.data.get("phone_number")
        country_code = request.data.get("country_code")
        if not otp or len(otp) != 4:
            return Response(
                data={_("error"): _("Please enter a valid 4 digit otp")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not phone_number or not country_code:
            return Response(
                data={_("error"): _("Please enter phone numberand country_code")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        send_to = "+" + country_code + phone_number
        otp = Otp.objects.filter(otp=otp, phone_number=send_to)
        if otp.count() == 1:
            user = User.objects.filter(phone_number=phone_number)
            if user.count() > 0:
                user_id = user.first().user_id
                return render(request, "change_password.html", {"user_id": user_id})

        else:
            return Response(
                data={_("error"): _("The otp entered is incorrect")},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ChangePasswordonForgot(APIView):
    def post(self, request):

        new_password = request.POST.get("new_password")
        confirm_new_password = request.POST.get("confirm_new_password")
        user_id = request.POST.get("user_id")

        user = User.objects.get(user_id=user_id)
        errors = []
        if not new_password or not confirm_new_password:
            errors.append("All the parameters are not given")

        if new_password != confirm_new_password:
            errors.append("New password and confirm new password does not match")

        if errors:
            return render(request, "change_password.html", {"errors": errors})

        user.password = make_password(new_password)
        user.save()
        return Response(
            data={_("message"): _("Password changed successfully")},
            status=status.HTTP_200_OK,
        )


class ResetPassword(APIView):
    def get(self, request, user_id):
        return render(request, "change_password.html", {"user_id": user_id})
