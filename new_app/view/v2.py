from django.contrib.auth.hashers import make_password
from rest_framework import permissions, status
from rest_framework.response import Response
from new_app.models.user import User
from rest_framework.views import APIView
from new_app.serializers import (
    SignupSerializer,
    UserSerializerV2,
    EditProfileSerializer,
)
from django.utils import timezone
from django.utils.translation import gettext as _
from new_app.helpers import save_model


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
        address = serializer.validated_data["address"]

        # make password hash and create the user
        password_hash = make_password(password)
        user = User(
            email=email,
            phone_number=phone_number,
            password=password_hash,
            date_created=timezone.now(),
            address=address,
        )
        save_model(user)

        return Response(
            data={
                _("message"): _("user created successfully"),
                _("user"): UserSerializerV2(request.data).data,
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
        if user:
            serializer = UserSerializerV2(user).data
            return Response(data=serializer, status=status.HTTP_200_OK)

        return Response(
            data={_("error"): _("User not found")}, status=status.HTTP_400_BAD_REQUEST
        )


class EditUserProfile(APIView):
    """
    Edit the User details
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = EditProfileSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(phone_number=request.user).first()
        if not user:
            return Response(
                data={_("error"): _("User not found")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        address = serializer.validated_data["address"]
        password = serializer.validated_data["password"]
        password_hash = make_password(password)

        user.email = user.email
        user.address = address
        user.password = password_hash
        save_model(user)

        return Response(
            data={
                _("message"): _("user edited successfully"),
                _("user"): UserSerializerV2(user).data,
            },
            status=status.HTTP_201_CREATED,
        )
