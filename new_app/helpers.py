from twilio.rest import Client
import random

TWILIO_ACCOUNT_SID = "AC453f82620fa80b3f657ba4e3095ecffa"
TWILIO_AUTH_TOKEN = "eff909ec23165a54c2c32d1a6865e968"
TWILIO_NUMBER = "+18509903869"


def generate_otp():
    otp = ""
    for _ in range(4):
        otp += str(random.randint(0, 9))
    return otp


class MessageClient:
    def __init__(self):

        self.twilio_number = TWILIO_NUMBER
        self.twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    def send_message(self, body, to):
        self.twilio_client.messages.create(body=body, to=to, from_=self.twilio_number)
