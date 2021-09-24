from new_app.models.user import User
from twilio.rest import Client
import random
from new_project.settings import TWILIO_AUTH_TOKEN, TWILIO_ACCOUNT_SID, TWILIO_NUMBER


def save_model(model):
    model.save()
    model.pk = None
    model.save(using="user_db")


def generate_otp() -> str:
    otp = str(random.randint(1000, 9999))
    return otp


class MessageClient:
    """
    Messgae client to send the otp
    """

    def __init__(self):

        self.twilio_number = str(TWILIO_NUMBER)
        self.twilio_client = Client(str(TWILIO_ACCOUNT_SID), str(TWILIO_AUTH_TOKEN))

    def send_message(self, body, to):
        self.twilio_client.messages.create(body=body, to=to, from_=self.twilio_number)


class DataBaseConfiguration(object):
    """
    sets which db to be use for which operation
    """

    route_app_labels = ["new_app"]

    def db_for_read(self, model, **hints):
        """
        Attempts to read auth and contenttypes models go to auth_db.
        """
        if model._meta.app_label in self.route_app_labels:
            return "user_db"
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write auth and contenttypes models go to auth_db.
        """
        if model._meta.app_label in self.route_app_labels:
            return "default"
        return None
