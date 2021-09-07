from new_app.models.user import User
from rest_framework import serializers


class Userserializer_v1(serializers.ModelSerializer):
    """
    User serializer for version v1
    """

    class Meta:
        model = User
        fields = [
            "email",
            "phone_number",
            "user_id",
            "is_active",
            "date_created",
            "is_superuser",
            "last_login",
        ]


class Userserializer_v2(serializers.ModelSerializer):
    """
    User serializer for version v2
    """

    class Meta:
        model = User
        fields = [
            "email",
            "phone_number",
            "user_id",
            "is_active",
            "date_created",
            "is_superuser",
            "last_login",
            "address",
        ]
