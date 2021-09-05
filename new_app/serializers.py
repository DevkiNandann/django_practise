from new_app.models.user import User
from rest_framework import serializers


class Userserializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "phone_number", "user_id"]
