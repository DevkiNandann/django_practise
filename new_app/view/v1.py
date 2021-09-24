import os
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.serializers import Serializer
from new_app.models.user import User, Otp
from rest_framework.views import APIView
from new_app.serializers import (
    UserSerializerV1,
    LoginUserSerializer,
    ForgotPasswordEmailSerializer,
    ForgotPasswordOtpSerializer,
    ChangePasswordUserSerializer,
    SignupSerializer,
    ValidateOtpSerializer,
    ResetPasswordSerializer,
)
from django.utils import timezone
from django.utils.translation import gettext as _
from new_app.helpers import generate_otp, MessageClient, save_model
from django.shortcuts import render
from django.core.mail import send_mail
from new_project.settings import BASE_URL


class Signup(APIView):
    """
    API for new user to sign up
    """

    def post(self, request):

        serializer = SignupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"]
        phone_number = serializer.validated_data["phone_number"]
        password = serializer.validated_data["password"]

        # make password hash and create the user
        password_hash = make_password(password)
        user = User(
            email=email,
            phone_number=phone_number,
            password=password_hash,
            date_created=timezone.now(),
        )
        save_model(user)

        return Response(
            data={
                _("message"): _("user created successfully"),
                _("user"): UserSerializerV1(request.data).data,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginUser(APIView):
    """
    API for the user to login
    """

    def post(self, request):
        serializer = LoginUserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        # check for email existence in db
        user_qs = User.objects.using("default").filter(email=email)
        if not user_qs.exists():
            return Response(
                data={_("error"): _("The user with this email does not exist")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = user_qs.first()

        # check if password entered is correct
        if not check_password(password, user.password):
            return Response(
                data={_("error"): _("Incorrect Password")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # creating a new token or getting it if already exists for a user
        new_token, created = Token.objects.get_or_create(user=user)
        if new_token:
            user.last_login = timezone.now()
            user.save()
            response = {
                _("token"): str(new_token),
                _("user"): UserSerializerV1(user).data,
            }
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
            serializer = ChangePasswordUserSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    data=serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )

            new_password = serializer.validated_data["new_password"]
            old_password = serializer.validated_data["old_password"]

            # check if old passwor entered is correct
            if not check_password(old_password, user.password):
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={_("error"): _("Old password entered is incorrect")},
                )

            # make new password hash and save it
            user.password = make_password(new_password)
            save_model(user)
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
        if user:
            serializer = UserSerializerV1(user).data
            return Response(data=serializer, status=status.HTTP_200_OK)

        return Response(
            data={_("error"): _("User not found")}, status=status.HTTP_400_BAD_REQUEST
        )


class ForgotPasswordEmail(APIView):
    """
    API to send reset link on forgot password through email using sendgrid
    """

    def post(self, request):

        serializer = ForgotPasswordEmailSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"]

        # check for existence of user
        user_qs = User.objects.filter(email=email)
        if user_qs.exists():
            user = user_qs.first().user_id

            # creating a local url for now
            url = f"{BASE_URL}/redirect_email/{user}"
            sender = os.environ.get("SEND_FROM")

            # send the mail to user
            send_mail(
                "Change your password",
                f"Please click on {url} to change your password",
                sender,
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
    """
    API to send the otp on forogt password using twilio
    """

    def post(self, request):

        serializer = ForgotPasswordOtpSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        phone_number = serializer.validated_data["phone_number"]
        country_code = serializer.validated_data["country_code"]
        otp = generate_otp()

        # creating a client
        client = MessageClient()
        send_to = "+" + country_code + phone_number

        # if otp is already present with the number then update the otp
        existing_otp_qs = Otp.objects.filter(phone_number=send_to)
        if existing_otp_qs.exists():
            existing_otp = existing_otp_qs.first()

            # send the otp with a gap of 1 minute
            if (timezone.now() - existing_otp.date_created).seconds < 60:
                return Response(
                    data={_("error"): _("Please try after one minute")},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                existing_otp.otp = otp
                existing_otp.date_created = timezone.now()
                save_model(existing_otp)
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

        serializer = ValidateOtpSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        otp = serializer.validated_data["otp"]
        phone_number = serializer.validated_data["phone_number"]
        country_code = serializer.validated_data["country_code"]

        # checking if the otp is present and is of required length 4
        if not otp or len(otp) != 4:
            return Response(
                data={_("error"): _("Please enter a valid 4 digit otp")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        send_to = "+" + country_code + phone_number

        # if the otp entered exists for the entered phone number render it to
        # the change password page else throw an error
        otp = Otp.objects.filter(otp=otp, phone_number=send_to)
        if otp.exists():
            user_qs = User.objects.filter(phone_number=phone_number)
            if user_qs.exists():
                user_id = user_qs.first().user_id
                return render(request, "change_password.html", {"user_id": user_id})

            else:
                return Response(
                    data={_("error"): _("No user assosciated with the phone number")},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        else:
            return Response(
                data={_("error"): _("The otp entered is incorrect")},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ResetPassword(APIView):
    """
    API to change the user password in db
    """

    def post(self, request):

        # fetching the details from html form
        serializer = ResetPasswordSerializer(data=request.POST)
        if not serializer.is_valid():
            errors = []

            for key, value in serializer.errors.items():
                errors.append({key: value})

            return render(request, "change_password.html", {"errors": errors})

        new_password = serializer.validated_data["new_password"]
        user_id = serializer.validated_data["user_id"]

        user = User.objects.get(user_id=user_id)

        user.password = make_password(new_password)
        save_model(user)
        return Response(
            data={_("message"): _("Password changed successfully")},
            status=status.HTTP_200_OK,
        )


class RedirectEmail(APIView):
    """
    API to render the link sent on email to chnage password page
    """

    def get(self, request, user_id: int):
        return render(request, "change_password.html", {"user_id": user_id})
