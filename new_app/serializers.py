from new_app.models.user import User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator


class UserSerializerV1(serializers.ModelSerializer):
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


class UserSerializerV2(serializers.ModelSerializer):
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


class LoginUserSerializer(serializers.Serializer):
    """
    Serializer for login post API
    """

    email = serializers.EmailField(required=True, max_length=255)
    password = serializers.CharField(required=True, max_length=255)


class SignupSerializer(serializers.Serializer):
    """
    Serializer for signup post api
    """

    email = serializers.EmailField(
        required=True,
        max_length=255,
        validators=[UniqueValidator(queryset=User.objects.all())],
    )
    phone_number = serializers.CharField(
        required=True,
        max_length=255,
        validators=[UniqueValidator(queryset=User.objects.all())],
    )
    password = serializers.CharField(required=True, max_length=255)
    confirm_password = serializers.CharField(required=True, max_length=255)
    address = serializers.CharField(max_length=255)

    def validate(self, attrs):
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")

        if password != confirm_password:
            raise serializers.ValidationError(
                "New password and confirm new password does not match"
            )

        return attrs


class ChangePasswordUserSerializer(serializers.Serializer):
    """
    Serializer for change password post api
    """

    old_password = serializers.CharField(required=True, max_length=255)
    new_password = serializers.CharField(required=True, max_length=255)
    confirm_new_password = serializers.CharField(required=True, max_length=255)

    def validate(self, attrs):
        new_password = attrs.get("new_password")
        confirm_new_password = attrs.get("confirm_new_password")

        if new_password != confirm_new_password:
            raise serializers.ValidationError(
                "New password and confirm new password does not match"
            )

        return attrs


class ForgotPasswordEmailSerializer(serializers.Serializer):
    """
    Serializer for forgot password through email post api
    """

    email = serializers.EmailField(required=True, max_length=255)


class ForgotPasswordOtpSerializer(serializers.Serializer):
    """
    Serializer for forgot password using otp post api
    """

    phone_number = serializers.CharField(required=True, max_length=255)
    country_code = serializers.CharField(required=True, max_length=255)


class ValidateOtpSerializer(serializers.Serializer):
    """
    Serializer for vallidate otp post api
    """

    otp = serializers.CharField(required=True, max_length=255)
    phone_number = serializers.CharField(required=True, max_length=255)
    country_code = serializers.CharField(required=True, max_length=255)


class ResetPasswordSerializer(serializers.Serializer):
    """
    Serializer for reset password post api
    """

    new_password = serializers.CharField(required=True, max_length=255)
    confirm_new_password = serializers.CharField(required=True, max_length=255)
    user_id = serializers.IntegerField(required=True)

    def validate(self, attrs):
        new_password = attrs.get("new_password")
        confirm_new_password = attrs.get("confirm_new_password")

        if new_password != confirm_new_password:
            raise serializers.ValidationError(
                "New password and confirm new password does not match"
            )

        return attrs


class CreateProductSerializer(serializers.Serializer):
    """
    Serializer for creating product
    """

    name = serializers.CharField(max_length=255)
    price = serializers.IntegerField()
