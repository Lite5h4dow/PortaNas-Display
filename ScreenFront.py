import digitalio
import board
import math
import os
import time
import socket
import psutil
import shutil
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7735 as st7735  # pylint: disable=unused-import

# Configuration for CS and DC pins (these are PiTFT defaults):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = digitalio.DigitalInOut(board.D24)

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 24000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()

# pylint: disable=line-too-long
# Create the display:
disp = st7735.ST7735R(spi, rotation=90,                           # 1.8" ST7735R
                      cs=cs_pin,
                      dc=dc_pin,
                      rst=reset_pin,
                      baudrate=BAUDRATE,
                      )
# pylint: enable=line-too-long

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
if disp.rotation % 180 == 90:
    height = disp.width  # we swap height/width to rotate it to landscape!
    width = disp.height
else:
    width = disp.width  # we swap height/width to rotate it to landscape!
    height = disp.height
image = Image.new("RGB", (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

maxDiv = 4
textPadding = 5
sectionMin = 30

fontPath = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
fontSize = 10

mainDrive = "/dev/mmcblk0p2"

total, used, free = shutil.disk_usage("/")


class section():
    def __init__(self, header, body, backColour, textColour):
        self.header = header,
        self.body = body,
        self.backColour = backColour,
        self.textColour = textColour,
        self.font = ImageFont.truetype(
            fontPath, fontSize
        )

    def render(self, xStart, yStart, xEnd, yEnd, colour, textColour):
        draw.rectangle((xStart, yStart, xEnd, yEnd), outline=0, fill=colour)

        headerHeight = 10

        bodyPadding = headerHeight+(textPadding*2)

        # print((self.body[0])())

        draw.text((xStart+textPadding, yStart+textPadding),
                  self.header[0], font=self.font, fill=textColour)

        draw.text((xStart+textPadding, yStart+bodyPadding),
                  self.body[0](), font=self.font, fill=textColour)


sections = []

sections.append(
    section(
        "Host Name",
        lambda: socket.gethostname(),
        (0, 0, 0),
        "#ffffff"
    )
)

sections.append(
    section(
        "CPU",
        lambda: str(psutil.cpu_percent(interval=1)) + "% used",
        (0, 0, 0),
        "#FFFFFF"
    )
)

sections.append(
    section(
        "IP Address",
        lambda: socket.gethostbyname(socket.gethostname()),
        (0, 0, 0),
        "#ffffff"
    )
)

sections.append(
    section(
        "Main Drive",
        lambda: str(round(free/(1024**3), 2)) + "GB left",
        (0, 0, 0),
        "#FFFFFF"
    )
)

sections.append(
    section(
        "Storage",
        lambda: "test",
        (0, 0, 255),
        "#000000"
    )
)


while(True):
    if len(sections) > 1:
        sectionHeight = height / (math.ceil(len(sections)/2))
        for i, section in enumerate(sections, start=1):
            xStart = width/2
            xEnd = width
            if i % 2 != 0:
                xStart = 0
                xEnd = width/2

            # print(xStart)
            # print(xEnd)

            row = math.ceil(i/2) - 1

            if(i == len(sections)):
                xEnd = width

            section.render(xStart, sectionHeight * row, xEnd, (sectionHeight * row) + sectionHeight,
                           section.backColour[0], section.textColour[0])

    elif len(sections) == 1:
        sections[0].render(0, 0, width, height,
                           sections[0].backColour[0], sections[0].textColour[0])

    disp.image(image)
    time.sleep(10)
