# *****************************************************************************
# * | File        :	  epd4in2.py
# * | Author      :   Waveshare team
# * | Function    :   Electronic paper driver
# * | Info        :
# *----------------
# * | This version:   V4.0
# * | Date        :   2019-06-20
# # | Info        :   python demo
# -----------------------------------------------------------------------------
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#


import logging
from . import epdconfig

# Display resolution
EPD_WIDTH       = 400
EPD_HEIGHT      = 300


class EPD:
    def __init__(self):
        self.reset_pin = epdconfig.RST_PIN
        self.dc_pin = epdconfig.DC_PIN
        self.busy_pin = epdconfig.BUSY_PIN
        self.cs_pin = epdconfig.CS_PIN
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT

    
    # Hardware reset
    def reset(self):
        epdconfig.digital_write(self.reset_pin, 1)
        epdconfig.delay_ms(200) 
        epdconfig.digital_write(self.reset_pin, 0)
        epdconfig.delay_ms(10)
        epdconfig.digital_write(self.reset_pin, 1)
        epdconfig.delay_ms(200)   

    def send_command(self, command):
        epdconfig.digital_write(self.dc_pin, 0)
        epdconfig.digital_write(self.cs_pin, 0)
        epdconfig.spi_writebyte([command])
        epdconfig.digital_write(self.cs_pin, 1)

    def send_data(self, data):
        epdconfig.digital_write(self.dc_pin, 1)
        epdconfig.digital_write(self.cs_pin, 0)
        epdconfig.spi_writebyte([data])
        epdconfig.digital_write(self.cs_pin, 1)
        
    def ReadBusy(self):
        logging.debug("e-Paper busy")
        while(epdconfig.digital_read(self.busy_pin) == 0):
            epdconfig.delay_ms(100)
        logging.debug("e-Paper busy release")
    
    def init(self):
        if (epdconfig.module_init() != 0):
            return -1
        # EPD hardware init start
        self.reset()

        self.send_command(0x01)  # POWER_SETTING
        self.send_data(0x07)
        self.send_data(0x00)
        self.send_data(0x08)
        self.send_data(0x00)
        self.send_command(0x06)  # BOOSTER_SOFT_START
        self.send_data(0x07)
        self.send_data(0x07)
        self.send_data(0x07)
        self.send_command(0x04)  # POWER_ON

        self.ReadBusy()

        self.send_command(0X00)  # PANEL_SETTING
        self.send_data(0xCF)
        self.send_command(0X50)  # VCOM_AND_DATA_INTERVAL_SETTING
        self.send_data(0x17)
        self.send_command(0x30)  # PLL_CONTROL
        self.send_data(0x39)
        self.send_command(0x61)  # TCON_RESOLUTION set x and y
        self.send_data(0x31)  # RAM x address end at 31h(49+1)*8->400
        self.send_data(0x00)
        self.send_data(0x2B)  # RAM y address start at 12Bh
        self.send_data(0x01)
        self.send_command(0x82)  # VCM_DC_SETTING_REGISTER
        self.send_data(0x0E)
        # EPD hardware init end
        return 0
        
    def Init_4Gray(self):
        if (epdconfig.module_init() != 0):
            return -1
        # EPD hardware init start
        self.reset()
        
        self.send_command(0x01)			#POWER SETTING
        self.send_data (0x03)
        self.send_data (0x00)       #VGH=20V,VGL=-20V
        self.send_data (0x2b)		#VDH=15V															 
        self.send_data (0x2b)		#VDL=-15V
        self.send_data (0x13)

        self.send_command(0x06)         #booster soft start
        self.send_data (0x17)		#A
        self.send_data (0x17)		#B
        self.send_data (0x17)		#C 

        self.send_command(0x04)
        self.ReadBusy()

        self.send_command(0x00)			#panel setting
        self.send_data(0x3f)		#KW-3f   KWR-2F	BWROTP 0f	BWOTP 1f

        self.send_command(0x30)			#PLL setting
        self.send_data (0x3c)      	#100hz 

        self.send_command(0x61)			#resolution setting
        self.send_data (0x01)		#400
        self.send_data (0x90)     	 
        self.send_data (0x01)		#300
        self.send_data (0x2c)

        self.send_command(0x82)			#vcom_DC setting
        self.send_data (0x12)

        self.send_command(0X50)			#VCOM AND DATA INTERVAL SETTING			
        self.send_data(0x97)

    def getbuffer(self, image):
        # logging.debug("bufsiz = ",int(self.width/8) * self.height)
        buf = [0xFF] * (int(self.width/8) * self.height)
        image_monocolor = image.convert('1')
        imwidth, imheight = image_monocolor.size
        pixels = image_monocolor.load()
        # logging.debug("imwidth = %d, imheight = %d",imwidth,imheight)
        if(imwidth == self.width and imheight == self.height):
            logging.debug("Horizontal")
            for y in range(imheight):
                for x in range(imwidth):
                    # Set the bits for the column of pixels at the current position.
                    if pixels[x, y] == 0:
                        buf[int((x + y * self.width) / 8)] &= ~(0x80 >> (x % 8))
        elif(imwidth == self.height and imheight == self.width):
            logging.debug("Vertical")
            for y in range(imheight):
                for x in range(imwidth):
                    newx = y
                    newy = self.height - x - 1
                    if pixels[x, y] == 0:
                        buf[int((newx + newy*self.width) / 8)] &= ~(0x80 >> (y % 8))
        return buf

    def display(self, blackimage):
        # send black data
        if (blackimage != None):
            self.send_command(0x10)  # DATA_START_TRANSMISSION_1
            for i in range(0, int(self.width * self.height / 8)):
                temp = 0x00
                for bit in range(0, 4):
                    if (blackimage[i] & (0x80 >> bit) != 0):
                        temp |= 0xC0 >> (bit * 2)
                self.send_data(temp)
                temp = 0x00
                for bit in range(4, 8):
                    if (blackimage[i] & (0x80 >> bit) != 0):
                        temp |= 0xC0 >> ((bit - 4) * 2)
                self.send_data(temp)

        self.send_command(0x12)  # DISPLAY_REFRESH
        self.ReadBusy()


    def Clear(self):
        self.send_command(0x10)
        for i in range(0, int(self.width * self.height / 8)):
            self.send_data(0xFF)
            
        self.send_command(0x13)
        for i in range(0, int(self.width * self.height / 8)):
            self.send_data(0xFF)
            
        self.send_command(0x12) 
        self.ReadBusy()

    def sleep(self):
        self.send_command(0x50)  # VCOM_AND_DATA_INTERVAL_SETTING
        self.send_data(0x17)
        self.send_command(0x82)  # to solve Vcom drop
        self.send_data(0x00)
        self.send_command(0x01)  # power setting
        self.send_data(0x02)  # gate switch to external
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x00)
        self.ReadBusy()

        self.send_command(0x02)  # power off

        epdconfig.module_exit()
        
### END OF FILE ###

