import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)  
servo_signal = 16
frequency = 50

GPIO.setup(servo_signal, GPIO.OUT)


servo_pwm = GPIO.PWM(servo_signal, frequency)
servo_pwm.start(0)

def servo(duty_cycle):
    servo_pwm.ChangeDutyCycle(duty_cycle)
    print(duty_cycle)
    time.sleep(1)

try:
    while True:
        servo(3.6)
        time.sleep(20)
        servo(2.7375)
        time.sleep(2)

except KeyboardInterrupt:
    servo_pwm.stop()
    GPIO.cleanup()
    