from i2c_lcd import I2cLcd
from gpiozero import LED
from time import sleep
import json
import requests
import threading
import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="barcodepro"
)

red_led = LED(17)
green_led = LED(27)
cart_items_count = 0
total_price = 0
scroll_threads_running = [False, False]

I2C_ADDR = 0x3F
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16

lcd = I2cLcd(1, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)
lcd.clear()


def scroll_text(text, line, index):
    while scroll_threads_running[index]:
        for i in range(len(text) - 15):
            sub_str = text[i:i + 16]
            lcd.move_to(0, line)
            lcd.putstr(sub_str)

            if (i == 0 or i == len(text) - 16):
                sleep(2)
            else:
                sleep(0.2)


def display_text(text, line):
    global scroll_threads_running

    if (len(text) > 16):
        scroll_threads_running[line] = True
        thread = threading.Thread(target=scroll_text, args=(text, line, line))
        thread.start()
    else:
        lcd.move_to(0, line)
        lcd.putstr(text.ljust(16))
        scroll_threads_running[line] = False


def turn_on_led(led, seconds=0):
    led.on()

    if (seconds > 0):
        thread = threading.Timer(seconds, lambda: led.off())
        thread.start()


def is_json(string):
    try:
        json.loads(string)
    except ValueError as e:
        return False
    return True


def scan_item(code):
    global cart_items_count
    global total_price

    url = "http://localhost/testApi/api.php?code=" + code
    response = requests.get(url)

    if (not is_json(response.text) or not "price" in response.json() or not "name" in response.json()):
        turn_on_led(red_led, 2)
        display_text("", 1)
        display_text("Code barre inconnu", 0)
        return

    response_json = response.json()
    green_led.on()
    cart_items_count += 1
    total_price += response_json['price']

    turn_on_led(green_led, 2)

    # Insert scanned product to logs
    cursor = db.cursor()
    query = "INSERT INTO scan_history (barcode, product_name, price) VALUES (%s, %s, %s)"
    values = (code, response_json['name'], response_json['price'])
    cursor.execute(query, values)
    db.commit()

    display_text(response_json['name'][:16], 0)
    display_text(str(response_json['price']), 1)

    sleep(2)

    display_text('Nbr article : ' + str(cart_items_count), 0)
    display_text('Total : ' + str(round(total_price, 2)), 1)


# Codes disponbles :
# 258454125841
# 465659887454
# 3124480167026
# 3398284433537
# X000U80C67


while True:
    scanned_code = input("Code barre du produit : ")
    scroll_threads_running = [False, False]
    scan_item(scanned_code)
