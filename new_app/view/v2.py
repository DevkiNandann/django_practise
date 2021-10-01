import stripe
from django.conf import settings
from django.contrib.auth.hashers import make_password
from rest_framework import permissions, status
from rest_framework.response import Response
from new_app.models.user import User
from new_app.models.product import Product
from rest_framework.views import APIView
from new_app.serializers import (
    SignupSerializer,
    UserSerializerV2,
    CreateProductSerializer,
)
from django.utils import timezone
from django.utils.translation import gettext as _
from django.shortcuts import render
from django.core.mail import send_mail


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


class CreateProduct(APIView):
    """
    API to create a product
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CreateProductSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        name = serializer.validated_data["name"]
        price = serializer.validated_data["price"]

        Product.objects.create(name=name, price=price)

        return Response(
            data={
                _("message"): _("product created successfully"),
                _("user"): CreateProductSerializer(request.data).data,
            },
            status=status.HTTP_201_CREATED,
        )


class SuccessView(APIView):
    def get(self, request):
        return render(request, "success.html")


class CancelView(APIView):
    def get(self, request):
        return render(request, "cancel.html")


class GetProduct(APIView):
    """
    API to get all the products available
    """

    def get(self, request):
        products = Product.objects.all()
        return render(request, "all_product.html", {"products": products})


class SellProduct(APIView):
    """
    API to sell the product
    """

    def get(self, request, id):
        product = Product.objects.get(id=id)
        return render(request, "checkout.html", {"product": product})


class CreateCheckoutSession(APIView):
    """
    API to create checkout
    """

    def post(self, request, id):
        stripe.api_key = settings.STRIPE_SECRET_KEY

        try:
            product = Product.objects.get(id=id)
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "unit_amount": product.price,
                            "product_data": {
                                "name": product.name,
                            },
                        },
                        "quantity": 1,
                    },
                ],
                payment_method_types=[
                    "card",
                ],
                metadata={"product_id": product.id},
                mode="payment",
                success_url=settings.BASE_URL + "checkout_success",
                cancel_url=settings.BASE_URL + "checkout_cancel",
            )

        except Exception as e:
            return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)

        response = {
            "session_url": checkout_session.url,
            "message": "Checkout successfully. Please click the link below",
        }
        return Response(response, status.HTTP_200_OK)


class WebhookView(APIView):
    """
    Event handler
    """

    def post(self, request):
        payload = request.body
        sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )

        except ValueError as e:
            return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)

        except stripe.error.SignatureVerificationError as e:
            return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]

            customer_email = session["customer_details"]["email"]
            product_id = session["metadata"]["product_id"]

            product = Product.objects.get(id=product_id)

            send_mail(
                "Here is your product",
                f"Thanks for your purchase. Here is the product you ordered. Your product is {product.name}",
                "devki.gupta@unthinkable.co",
                [
                    customer_email,
                ],
            )

        return Response(payload, status=status.HTTP_200_OK)


class CreatePayment(APIView):
    """
    APi to create the payment
    """

    def post(self, request, id):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        data = request.data
        product = Product.objects.get(id=id)

        # Create or use a preexisting Customer to associate with the payment
        customer = stripe.Customer.create(
            email=settings.TEST_EMAIL,
            description="vacation",
            name="XYZ",
            address={
                "city": "x",
                "country": "AF",
                "line1": "x",
                "line2": "x",
                "postal_code": "90210",
                "state": "x",
            },
        )

        intent = stripe.PaymentIntent.create(
            amount=product.price,
            currency="usd",
            customer=customer["id"],
            metadata={"product_id": product.id},
            description="vacation",
        )
        try:
            return Response(
                {
                    "publicKey": settings.STRIPE_PUBLISHABLE_KEY,
                    "clientSecret": intent.client_secret,
                    "id": intent.id,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response({"error": e}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
