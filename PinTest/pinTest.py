import RPi.GPIO as GPIO
import time
import threading
import os
import subprocess
import requests

PIN = 35
GPIO.setmode(GPIO.BOARD)
GPIO.setup(PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
pin_high = threading.Event()
pin_check = threading.Event()
pin_check.set()
press_counter = 0
def check_pin():
    while pin_check.is_set():
        time.sleep(0.25)
        inp = GPIO.input(PIN)
        if inp:
            pin_high.set()
        else:
            pin_high.clear()
            press_counter = 0

check_pin_thread = threading.Thread(target=check_pin)

check_pin_thread.start()

flipped_direction = False

try:
    while True:
        if not pin_high.is_set():
            press_counter = 0
            flipped_direction = False
        pin_high.wait()
        press_counter +=1
        if not flipped_direction:
            requests.post("http://localhost:5000/default-direction")
            flipped_direction = True
        time.sleep(.5)
        if press_counter>3:
            subprocess.call(['sh','/home/pi/Documents/gitProj/MTAProject/PinTest/shutdown.sh'])
except KeyboardInterrupt:
    print("Exiting..")
    pin_check.clear()
    raise 
