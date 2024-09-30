import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

conveyor_step = 5
conveyor_dir = 6
conveyor_enable = 26

GPIO.setup(conveyor_step, GPIO.OUT)
GPIO.setup(conveyor_dir, GPIO.OUT)
GPIO.setup(conveyor_enable, GPIO.OUT)

conveyor_spr = 1600
conveyor_rpm = 40
conveyor_delay = 60 / (conveyor_spr * conveyor_rpm)


def conveyor():
    while True:
        GPIO.output(conveyor_dir, GPIO.LOW)
        GPIO.output(conveyor_step, GPIO.HIGH)
        time.sleep(conveyor_delay / 2)
        GPIO.output(conveyor_step, GPIO.LOW)
        time.sleep(conveyor_delay / 2)
      
try:
    conveyor()

except KeyboardInterrupt:
    GPIO.cleanup()