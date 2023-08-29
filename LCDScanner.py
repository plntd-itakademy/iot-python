from i2c_lcd import I2cLcd
from gpiozero import LED
from time import sleep

I2C_ADDR = 0x3F
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16

lcd = I2cLcd(1, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)
lcd.clear()

item_count = 0

scode = ""

lcd.putstr("Hello please")

while True:
    scode = input()  # Wait to get input from barcode reader
    
    lcd.clear()
    lcd.putstr("Scanned Barcode", 1)
    lcd.putstr(scode,2)

    sleep(2)

    lcd.clear()
    lcd.putstr("   Item Added", 1)

    sleep(2)

    item_count += 1
    ic_str = str(item_count)

    lcd.clear()
    lcd.putstr("  Total Item =", 1)
    lcd.putstr(ic_str, 2)

    sleep(1)
