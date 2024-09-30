import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

sensor_echo = 20
sensor_trig = 21

GPIO.setup(sensor_trig, GPIO.OUT)
GPIO.setup(sensor_echo, GPIO.IN)

speed_of_sound = 34300   # speed of sound (cms / s) at 20°C

def measure_distance():
    GPIO.output(sensor_trig, GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(sensor_trig, GPIO.LOW)
    pulse_start_time = time.time()
    pulse_end_time = time.time()
    while GPIO.input(sensor_echo) == 0:
        pulse_start_time = time.time()
    while GPIO.input(sensor_echo) == 1:
        pulse_end_time = time.time()
        
    pulse_duration = pulse_end_time - pulse_start_time
    
    distance = pulse_duration * (speed_of_sound / 2)
    print(f'Distance : {distance:.2f} cms')
    if distance < 5:
		    print(f'Distance is less than 5 cms: {distance:.2f} cms')
    
try:
    while True:
        measure_distance()
        # time.sleep(0.5)
    
except KeyboardInterrupt:
    GPIO.cleanup()
    
