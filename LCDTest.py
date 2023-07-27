from i2c_lcd import I2cLcd
from gpiozero import LED
from time import sleep
import json
import requests
import threading

red_led = LED(17)
green_led = LED(27)
cart_items_count = 0 # Compteur nbr d'articles scannés

I2C_ADDR = 0x3F
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16

lcd = I2cLcd(1, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)
lcd.clear()

def display_text(text, line):
    if len(text) > 16:
        while True:
            for i in range(len(text) - 15):
                sub_str = text[i:i + 16]
                lcd.move_to(0, line)  
                lcd.putstr(sub_str)            

                if (i == 0 or i == len(text) - 16):
                    sleep(2) # Pause avant que le texte commence/recommence à défiler
                else:
                    sleep(0.2) # Vitesse défilement
    else:
        lcd.move_to(0, line)
        lcd.putstr(text.ljust(16))

def is_json(string):
  try:
    json.loads(string)
  except ValueError as e:
    return False
  return True

def scan_item(code):
    global cart_items_count
    url = "http://localhost/testApi/api.php?code=" + code
    response = requests.get(url)

    if (is_json(response.text)):
        response_json = response.json()
        green_led.on()
        cart_items_count += 1

        thread = threading.Timer(2, lambda: green_led.off())
        thread.start()

        display_text('Nbr article : ' + str(cart_items_count), 0)
        sleep(2)
        display_text(response_json['name'], 0)
        display_text(str(response_json['price']), 1)
    else:
        red_led.on()
        thread = threading.Timer(2, lambda: red_led.off())
        thread.start()
        display_text("Code barre inconnu", 0)

# Codes disponbles :
# 258454125841
# 465659887454
scanned_code = input("Code barre du produit : ")
scan_item(scanned_code)
