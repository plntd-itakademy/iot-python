from lcd_api import LcdApi
from i2c_lcd import I2cLcd
from gpiozero import LED
from time import sleep
import json
import requests
import threading

redled = LED(17)
greenled = LED(27)
text_line1 = ""
text_line2 = ""

# Codes disponbles :
# 258454125841
# 465659887454
code = input("Code barre du produit : ")
url = "http://localhost/testApi/api.php?code=" + code

def display_text(texte, lcd, ligne):
    if len(texte) > 16:
        for i in range(len(texte) - 15):
            sous_chaine = texte[i:i + 16]
            lcd.move_to(0, ligne)  
            lcd.putstr(sous_chaine)

            if i == 0:
                sleep(3)
            else:
                sleep(0.2)  # Réglez la durée d'affichage pour contrôler la vitesse de défilement
                 
    else:
        lcd.move_to(0, ligne)
        lcd.putstr(texte.ljust(16))

def is_json(string):
  try:
    json.loads(string)
  except ValueError as e:
    return False
  return True

def turn_off_leds():
    redled.off()
    greenled.off()

I2C_ADDR = 0x3F
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16

lcd = I2cLcd(1, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)
lcd.clear()

response = requests.get(url)

if (is_json(response.text)):
    response_json = response.json()
    greenled.on()
    text_line1 = response_json['name']
    text_line2 = str(response_json['price'])
else:
    redled.on()
    text_line1 = "Code barre inconnu"

thread = threading.Timer(2, turn_off_leds)
thread.start()

# Affiche uniquement sur la première ligne
lcd.move_to(0, 0)
lcd.putstr(text_line1.ljust(16))  # Remplit avec des espaces si la longueur est inférieure à 16

# Affiche sur la deuxième ligne
lcd.move_to(0, 1)
lcd.putstr(text_line2.ljust(16))  # Remplit avec des espaces si la longueur est inférieure à 16

cart = 0 # déclaration de notre panier afin de boucler

# Défile le texte s'il dépasse 16 caractères
while True:
    if (text_line1):
        display_text(text_line1, lcd, 0)
    
    if (text_line2):
        display_text(text_line2, lcd, 1)
    
    cart += 1
    sleep(3)
    greenled.off()
    redled.off()