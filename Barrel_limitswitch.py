import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

barrel_step = 17
barrel_dir = 27
barrel_enable = 22

limit_switch = 3

GPIO.setup(barrel_step, GPIO.OUT)
GPIO.setup(barrel_dir, GPIO.OUT)
GPIO.setup(barrel_enable, GPIO.OUT)
GPIO.setup(limit_switch, GPIO.IN, pull_up_down = GPIO.PUD_UP)

barrel_spr = 1600
barrel_rpm = 1     # Change the RPM to 2 when it is connected to NEMA 23
barrel_delay = 60 / (barrel_spr * barrel_rpm)
barrel_alligned = False

def barrel():
    global barrel_alligned
    while True:
        
        GPIO.output(barrel_dir, GPIO.LOW)
        if barrel_alligned == False:
            if GPIO.input(limit_switch) == GPIO.HIGH:
                GPIO.output(barrel_step, GPIO.HIGH)
                time.sleep(barrel_delay / 2)
                GPIO.output(barrel_step, GPIO.LOW)
                time.sleep(barrel_delay / 2)
            else:
                time.sleep(2)
                print('Limit_switch_pressed')
                time.sleep(2)
                for steps_taken in range(175):
                    GPIO.output(barrel_step, GPIO.HIGH)
                    time.sleep(barrel_delay / 2)
                    GPIO.output(barrel_step, GPIO.LOW)
                    time.sleep(barrel_delay / 2)
                    print(steps_taken)
                print('Barrel is alligned')
                barrel_alligned = True
		
        else:
            time.sleep(2)
            barrel_alligned = False
         
try:
	while True:
		barrel()

except KeyboardInterrupt:
    GPIO.cleanup()