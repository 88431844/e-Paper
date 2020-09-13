#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd4in2_WF
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

logging.basicConfig(level=logging.DEBUG)

try:
    logging.info("epd4in2_WF Demo")
    
    epd = epd4in2_WF.EPD()
    logging.info("init and Clear")
    epd.init()
    epd.Clear()
    time.sleep(1)
    
    # Drawing on the image
    logging.info("1.Drawing on the image...")
    blackimage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    font = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
    font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
    
    drawblack = ImageDraw.Draw(blackimage)
    drawblack.rectangle((0, 10, 200, 34), fill = 0)
    drawblack.text((8, 12), 'hello world', font = font, fill = 255)
    drawblack.text((8, 36), u'微雪电子', font = font18, fill = 0)
    drawblack.line((16, 60, 56, 60), fill = 0)
    drawblack.line((56, 60, 56, 110), fill = 0)
    drawblack.line((16, 110, 56, 110), fill = 0)

    epd.display(epd.getbuffer(blackimage))
    time.sleep(1)

    logging.info("Clear...")
    epd.init()
    epd.Clear()
    
    logging.info("Goto Sleep...")
    epd.sleep()
        
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd4in2_WF.epdconfig.module_exit()
    exit()
