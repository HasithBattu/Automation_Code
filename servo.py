import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)  
servo_signal = 16
frequency = 50

GPIO.setup(servo_signal, GPIO.OUT)

# Create PWM instance outside the function
servo_pwm = GPIO.PWM(servo_signal, frequency)
servo_pwm.start(0)

def servo(duty_cycle):
    servo_pwm.ChangeDutyCycle(duty_cycle)
    print(duty_cycle)
    time.sleep(1)

try:
    servo(3.6)
    
except KeyboardInterrupt:
    servo_pwm.stop()
    GPIO.cleanup()
