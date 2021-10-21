from twilio.rest import Client
import random
from new_project.settings import TWILIO_AUTH_TOKEN, TWILIO_ACCOUNT_SID, TWILIO_NUMBER


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
