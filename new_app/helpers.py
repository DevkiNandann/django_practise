import cv2
import numpy as np
import random
from twilio.rest import Client
from new_project.settings import TWILIO_AUTH_TOKEN, TWILIO_ACCOUNT_SID, TWILIO_NUMBER
from collections import Counter


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


def filter_helper(image, type):
    if type == "edge_detection":
        img_canny = cv2.Canny(image, 100, 100)
        return img_canny

    elif type == "blur":
        img_blur = cv2.GaussianBlur(image, (15, 15), 0)
        return img_blur

    else:
        return apply_effects(image, type)


def resize_frame(img, scale=30):
    width = int(img.shape[1] * scale / 100)
    height = int(img.shape[0] * scale / 100)
    dim = (width, height)
    resize_image = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
    return resize_image


def remove_background(img_path):
    bg_color = BackgroundColorDetector(img_path)
    bgcolor = bg_color.detect()
    f_img = cv2.imread(img_path)
    f_img = cv2.cvtColor(f_img, cv2.COLOR_BGR2BGRA)
    f_img[np.all(f_img == bgcolor + [255], axis=2)] = [0, 0, 0, 0]
    filter_img = cv2.cvtColor(f_img, cv2.COLOR_BGRA2BGR)
    return filter_img


def apply_effects(img, effect):
    if effect == "lens":
        filter_image_path = "data/filter_glass.jpg"

    elif effect == "cat":
        filter_image_path = "data/snowcat.jpg"

    elif effect == "dog":
        filter_image_path = "data/dog1.jpg"

    path = cv2.data.haarcascades
    face_cascade = cv2.CascadeClassifier(path + "haarcascade_frontalface_default.xml")

    filter_img = remove_background(filter_image_path)

    original_filter_img_h, original_filter_img_w, filter_img_channels = filter_img.shape
    img_h, img_w, img_channels = img.shape

    # convert to gray
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    filter_img_gray = cv2.cvtColor(filter_img, cv2.COLOR_BGR2GRAY)

    ret, original_mask = cv2.threshold(filter_img_gray, 10, 255, cv2.THRESH_BINARY_INV)
    original_mask_inv = cv2.bitwise_not(original_mask)

    # find faces in image using classifier
    faces = face_cascade.detectMultiScale(img_gray, 1.3, 5)

    for (x, y, w, h) in faces:
        # coordinates of face region
        face_w = w
        face_h = h
        face_x1 = x
        face_x2 = face_x1 + face_w
        face_y1 = y
        face_y2 = face_y1 + face_h

        # filter_img size in relation to face by scaling
        filter_img_width = int(1 * face_w)
        filter_img_height = int(filter_img_width * original_filter_img_h / original_filter_img_w)

        # setting location of coordinates of filter_img
        filter_img_x1 = face_x2 - int(face_w/2) - int(filter_img_width/2)
        filter_img_x2 = filter_img_x1 + filter_img_width
        filter_img_y1 = face_y1
        filter_img_y2 = filter_img_y1 + filter_img_height

        # check to see if out of frame
        if filter_img_x1 < 0:
            filter_img_x1 = 0
        if filter_img_y1 < 0:
            filter_img_y1 = 0
        if filter_img_x2 > img_w:
            filter_img_x2 = img_w
        if filter_img_y2 > img_h:
            filter_img_y2 = img_h

        # Account for any out of frame changes
        filter_img_width = filter_img_x2 - filter_img_x1
        filter_img_height = filter_img_y2 - filter_img_y1

        # resize filter_img to fit on face
        filter_img = cv2.resize(filter_img, (filter_img_width,filter_img_height), interpolation=cv2.INTER_AREA)
        mask = cv2.resize(original_mask, (filter_img_width,filter_img_height), interpolation=cv2.INTER_AREA)
        mask_inv = cv2.resize(original_mask_inv, (filter_img_width,filter_img_height), interpolation=cv2.INTER_AREA)

        #take ROI for filter_img from background that is equal to size of filter_img image
        roi = img[filter_img_y1:filter_img_y2, filter_img_x1:filter_img_x2]

        # original image in background (bg) where filter_img is not present
        roi_bg = cv2.bitwise_and(roi, roi, mask=mask)
        roi_fg = cv2.bitwise_and(filter_img, filter_img, mask=mask_inv)
        dst = cv2.add(roi_bg, roi_fg)

        # put back in original image
        img[filter_img_y1:filter_img_y2, filter_img_x1:filter_img_x2] = dst
        return img


class BackgroundColorDetector():
    def __init__(self, imageLoc):
        self.img = cv2.imread(imageLoc, 1)
        self.manual_count = {}
        self.w, self.h, self.channels = self.img.shape
        self.total_pixels = self.w*self.h

    def count(self):
        for y in range(0, self.h):
            for x in range(0, self.w):
                RGB = (self.img[x, y, 2], self.img[x, y, 1], self.img[x, y, 0])
                if RGB in self.manual_count:
                    self.manual_count[RGB] += 1
                else:
                    self.manual_count[RGB] = 1

    def average_colour(self):
        red = 0
        green = 0
        blue = 0
        sample = 10
        for top in range(0, sample):
            red += self.number_counter[top][0][0]
            green += self.number_counter[top][0][1]
            blue += self.number_counter[top][0][2]

        average_red = red / sample
        average_green = green / sample
        average_blue = blue / sample
        return [average_red, average_green, average_blue]

    def twenty_most_common(self):
        self.count()
        self.number_counter = Counter(self.manual_count).most_common(20)

    def detect(self):
        self.twenty_most_common()
        self.percentage_of_first = (
            float(self.number_counter[0][1])/self.total_pixels)
        if self.percentage_of_first > 0.5:
            return list(self.number_counter[0][0])
        else:
            return self.average_colour()