import RPi.GPIO as GPIO
import time
import threading

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

conveyor_step = 5
conveyor_dir = 6
conveyor_enable = 26

sensor_echo = 20
sensor_trig = 21

GPIO.setup(sensor_trig, GPIO.OUT)
GPIO.setup(sensor_echo, GPIO.IN)

GPIO.setup(conveyor_step, GPIO.OUT)
GPIO.setup(conveyor_dir, GPIO.OUT)
GPIO.setup(conveyor_enable, GPIO.OUT)

conveyor_running = True
sensor_running = True
conveyor_lock = threading.Lock()
sensor_lock = threading.Lock()

speed_of_sound = 34300  # speed of sound (cms/s) at 20°C

def rotate_conveyor_clockwise():
    GPIO.output(conveyor_dir, GPIO.HIGH)
    time.sleep(5)
    GPIO.output(conveyor_dir, GPIO.LOW)

def rotate_conveyor_anticlockwise():
    GPIO.output(conveyor_dir, GPIO.LOW)
    time.sleep(5)
    GPIO.output(conveyor_dir, GPIO.HIGH)

def conveyor():
    with conveyor_lock:
        conveyor_spr = 1600
        conveyor_rpm = 60
        conveyor_delay = 60 / (conveyor_spr * conveyor_rpm)
        global conveyor_running

        while True:
            if conveyor_running:
                GPIO.output(conveyor_step, GPIO.HIGH)
                time.sleep(conveyor_delay / 2)
                GPIO.output(conveyor_step, GPIO.LOW)
                time.sleep(conveyor_delay / 2)

def stop_conveyor():
    global conveyor_running, sensor_running
    conveyor_running = False
    sensor_running = False
    time.sleep(5)
    conveyor_running = True
    sensor_running = True

def measure_distance():
    with sensor_lock:
        global sensor_running, conveyor_running
        while True:
            if sensor_running and conveyor_running:
                GPIO.output(sensor_trig, GPIO.HIGH)
                time.sleep(0.5) 
                GPIO.output(sensor_trig, GPIO.LOW)
                
                pulse_start_time = time.time()
                while GPIO.input(sensor_echo) == 0:
                    pulse_start_time = time.time()
                
                pulse_end_time = time.time()
                while GPIO.input(sensor_echo) == 1:
                    pulse_end_time = time.time()

                pulse_duration = pulse_end_time - pulse_start_time
                distance = pulse_duration * (speed_of_sound / 2)
                print(f'Distance: {distance:.2f} cms')

                if distance > 7:
                    time.sleep(2)
                    print('Barrel is printing')
                    stop_conveyor()

                time.sleep(0.1)

try:
    conveyor_thread = threading.Thread(target=conveyor, daemon=True)
    sensor_thread = threading.Thread(target=measure_distance, daemon=True)
    conveyor_thread.start()
    sensor_thread.start()

    conveyor_thread.join()
    sensor_thread.join()

except KeyboardInterrupt:
    GPIO.cleanup()
