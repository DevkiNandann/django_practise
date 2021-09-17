import cv2
from django.shortcuts import render
import numpy as np
from django.contrib.auth.hashers import make_password
from rest_framework import permissions, status
from rest_framework.response import Response
from new_app.models.user import User
from rest_framework.views import APIView
from new_app.serializers import SignupSerializer, UserSerializerV2
from django.utils import timezone
from django.utils.translation import gettext as _
from new_app.helpers import filter_helper, resize_frame


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
        User.objects.create(
            email=email,
            phone_number=phone_number,
            password=password_hash,
            date_created=timezone.now(),
            address=address,
        )
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


class LiveStream(APIView):
    """
    API for user to change filter in live video
    """

    def post(self, request):
        filter_type = request.POST.get("filter_type")
        # use a hardcode video
        # cap = cv2.VideoCapture("data/video.mp4")

        # for webcam
        cap = cv2.VideoCapture(0)

        # set width height brightness for the webcam window
        cap.set(3, 1920)  # id 3 is width
        cap.set(4, 1080)  # id 4 is height
        cap.set(10, 100)  # id 10 is brightness

        while cap.isOpened():
            try:
                success, img = cap.read()
                if not success:
                    return render(request, "index.html", {"errors": "Failure in reading video"})
                img = resize_frame(img, scale=80)
                # apply filter
                img = filter_helper(img, filter_type)
                cv2.imshow('Video', img)
                if cv2.waitKey(10) == ord('q'):
                    cap.release()
                    cv2.destroyAllWindows()
                    return render(request, "index.html")
            except Exception as e:
                return render(request, "index.html", {"errors": e})
