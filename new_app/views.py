from django.contrib.auth.hashers import make_password, check_password
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from new_app.models.user import User
from rest_framework.views import APIView
from new_app.serializers import Userserializer
from django.utils import timezone


class UserDetail(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        users = User.objects.all()
        resp = Userserializer(users, many=True)
        return Response(resp.data)

    def post(self, request):
        data = request.data
        data["date_created"] = timezone.now()
        serializer = Userserializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


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

        print(request.data)
        print(email, phone_number, user_id, password, confirm_password)
        if (
            not email
            or not phone_number
            or not user_id
            or not password
            or not confirm_password
        ):
            return Response(
                data={"error": "Please enter all required fields"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if password != confirm_password:
            return Response(
                data={"error": "Password and confirm password does not match"},
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
                "message": "user created successfully",
                "user": Userserializer(request.data).data,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginUser(APIView):
    """
    API for the user to login
    """

    def post(self, request):
        user = User.objects.get(email=request.data["email"])

        new_token, created = Token.objects.get_or_create(user=user)
        print(new_token)
        if new_token:
            response = {"token": str(new_token), "user": Userserializer(user).data}
            return Response(response, status=status.HTTP_201_CREATED)

        return Response(request.data, status=status.HTTP_400_BAD_REQUEST)


class LogoutUser(APIView):
    """
    API for the user to logout
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)


class ChangePaswordUser(APIView):
    """
    API for user to change password
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = User.objects.get(phone_number=request.user)
        if user:
            password = request.data.get("old_password")
            new_password = request.data.get("new_password")
            confirm_new_password = request.data.get("confirm_new_password")

            if not password or not new_password or not confirm_new_password:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={"error": "All the parameters are not given"},
                )

            if not check_password(password, user.password):
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={"error": "Old password entered is incorrect"},
                )

            if new_password != confirm_new_password:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={
                        "error": "New password and confirm new password does not match"
                    },
                )

            user.password = make_password(new_password)
            user.save()
            return Response(
                data={"message": "Password changed successfully"},
                status=status.HTTP_200_OK,
            )
