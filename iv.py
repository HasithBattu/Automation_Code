import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

iv_step = 18
iv_dir = 23
iv_enable = 24

GPIO.setup(iv_step, GPIO.OUT)
GPIO.setup(iv_dir, GPIO.OUT)
GPIO.setup(iv_enable, GPIO.OUT)

iv_spr = 1600
iv_rpm = 50
iv_delay = 60 / (iv_spr * iv_rpm)
iv_rotations =  10 # Check with the number of rotations
iv_total_Steps = (iv_spr * iv_rotations) + 450

def iv():
    for i in range(50):
        GPIO.output(iv_dir, GPIO.LOW)
        for _ in range(iv_total_Steps):
            GPIO.output(iv_step, GPIO.HIGH)
            time.sleep(iv_delay / 2)
            GPIO.output(iv_step, GPIO.LOW)
            time.sleep(iv_delay / 2)
        
        
            
try:
	while True:
		iv()
    

except KeyboardInterrupt:
    GPIO.cleanup()
    
