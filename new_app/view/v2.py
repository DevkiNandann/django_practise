from django.contrib.auth.hashers import make_password, check_password
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from new_app.models.user import User
from rest_framework.views import APIView
from new_app.serializers import Userserializer_v2
from django.utils import timezone
from django.utils.translation import gettext as _


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
        address = request.data.get("address")

        # check for required fields
        if (
            not email
            or not phone_number
            or not user_id
            or not password
            or not confirm_password
            or not address
        ):
            return Response(
                data={_("error"): _("Please enter all required fields")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # check for uniqueness of email
        if User.objects.filter(email=email).count() > 0:
            return Response(
                data={_("error"): _("This email already exist")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # check for uniqueness of phone_number
        if User.objects.filter(phone_number=phone_number).count() > 0:
            return Response(
                data={_("error"): _("This phone number already exist")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # check for password and confirm password do match
        if password != confirm_password:
            return Response(
                data={_("error"): _("Password and confirm password does not match")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # make password hash and create the user
        password_to_set = make_password(password)
        User.objects.create(
            user_id=user_id,
            email=email,
            phone_number=phone_number,
            password=password_to_set,
            date_created=timezone.now(),
            address=address,
        )
        return Response(
            data={
                _("message"): _("user created successfully"),
                _("user"): Userserializer_v2(request.data).data,
            },
            status=status.HTTP_201_CREATED,
        )


class UserProfile(APIView):
    """
    API to get user profile
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = User.objects.get(phone_number=request.user)
        serializer = Userserializer_v2(user).data
        return Response(data=serializer, status=status.HTTP_200_OK)
