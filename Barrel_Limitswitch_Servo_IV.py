import RPi.GPIO as GPIO
import time


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

barrel_step = 17
barrel_dir = 27
barrel_enable = 22
 
limit_switch =4

servo_signal = 16

GPIO.setup(barrel_step, GPIO.OUT)
GPIO.setup(barrel_dir, GPIO.OUT)
GPIO.setup(barrel_enable, GPIO.OUT)

GPIO.setup(limit_switch, GPIO.IN, pull_up_down = GPIO.PUD_UP)

GPIO.setup(servo_signal, GPIO.OUT)

barrel_spr = 1600
barrel_rpm = 1      # Change the RPM to 2 when it is connected to NEMA 23
barrel_delay = 60 / (barrel_spr * barrel_rpm)
barrel_alligned = False
barrel_lock = threading.Lock()
tag_found = False

def barrel():
    # with barrel_lock:
    global barrel_alligned, current_try, max_tries, distance
    while True:

        GPIO.output(barrel_dir, GPIO.HIGH)
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
                for steps_taken in range(320):
                    GPIO.output(barrel_step, GPIO.HIGH)
                    time.sleep(barrel_delay / 2)
                    GPIO.output(barrel_step, GPIO.LOW)
                    time.sleep(barrel_delay / 2)
                    print(steps_taken)
                print('Barrel is alligned')
                barrel_alligned = True
                time.sleep(1)
                servo_open = False
                servo()
                time.sleep(1)
                servo_open = True
                servo()     
                 
        else:
            GPIO.output(barrel_step, GPIO.LOW)

servo_open = False
frequency = 50
servo_pwm = GPIO.PWM(servo_signal, frequency)
servo_pwm.start(0)
# servo_lock = threading.Lock()
def servo():
    global servo_open
    # with servo_lock:
    if servo_open == False:
        servo_pwm = GPIO.PWM(servo_signal, 50)
        servo_pwm.start(0)
        servo_pwm.ChangeDutyCycle(2.67475)
        time.sleep(1)
        print('Servo is open')
        servo_open = True
        
    else:
        time.sleep(2)
        servo_pwm = GPIO.PWM(servo_signal, 50)
        servo_pwm.start(0)
        servo_pwm.ChangeDutyCycle(3.6)
        print('Servo is closed')
        servo_open = False
        
try:
    barrel()

except KeyboardInterrupt:
    GPIO.cleanup()
    