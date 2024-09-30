import RPi.GPIO as GPIO
import time
import threading

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

barrel_step = 17
barrel_dir = 27
barrel_enable = 22
 
limit_switch = 3

servo_signal = 16

iv_step = 18
iv_dir = 23
iv_enable = 24

conveyor_step = 5
conveyor_dir = 6
conveyor_enable = 26

sensor_echo = 20
sensor_trig = 21

GPIO.setup(barrel_step, GPIO.OUT)
GPIO.setup(barrel_dir, GPIO.OUT)
GPIO.setup(barrel_enable, GPIO.OUT)

GPIO.setup(limit_switch, GPIO.IN, pull_up_down = GPIO.PUD_UP)

GPIO.setup(servo_signal, GPIO.OUT)

GPIO.setup(iv_step, GPIO.OUT)
GPIO.setup(iv_dir, GPIO.OUT)
GPIO.setup(iv_enable, GPIO.OUT)

GPIO.setup(conveyor_step, GPIO.OUT)
GPIO.setup(conveyor_dir, GPIO.OUT)
GPIO.setup(conveyor_enable, GPIO.OUT)

GPIO.setup(sensor_trig, GPIO.OUT)
GPIO.setup(sensor_echo, GPIO.IN)

max_tries = 2
current_try = 0
barrel_spr = 1600
barrel_rpm = 1      # Change the RPM to 2 when it is connected to NEMA 23
barrel_delay = 60 / (barrel_spr * barrel_rpm)
barrel_alligned = False
barrel_lock = threading.Lock()
tag_found = False
def barrel():
    with barrel_lock:
        global barrel_alligned, current_try, max_tries, distance, pulse_Start_time, pulse_end_time, mag_finished, tag_found, conveyor_running, sensor_running
        while True:
            
            for _ in range(8):
				
                GPIO.output(barrel_dir, GPIO.LOW )
                if barrel_alligned == False:
                    if GPIO.input(limit_switch) == GPIO.HIGH:
                        GPIO.output(barrel_step, GPIO.HIGH)
                        time.sleep(barrel_delay / 2)
                        GPIO.output(barrel_step, GPIO.LOW)
                        time.sleep(barrel_delay / 2)
                    else:
                        time.sleep(0.5)
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
                        time.sleep(0.5)
                        servo_open = False
                        servo()
                        time.sleep(1)
                        current_try = 0
                        distance = 0
                        while current_try < max_tries:
                            iv()
                            start_time = time.time()
                            while time.time() - start_time < 5:  # Adjust the time condition
                                if sensor_running:
                                    GPIO.output(sensor_trig, GPIO.HIGH)
                                    time.sleep(0.5)
                                    GPIO.output(sensor_trig, GPIO.LOW)
                                    pulse_start_time = time.time()
                                    pulse_end_time = time.time()
                                    pulse_end_time = time.time()
                                    while GPIO.input(sensor_echo) == 0:
                                        pulse_start_time = time.time()
                                    while GPIO.input(sensor_echo) == 1:
                                        pulse_end_time = time.time()
                                    
                                    pulse_duration = pulse_end_time - pulse_start_time

                                    distance = pulse_duration * (speed_of_sound / 2)
                                    print(f'Distance: {distance:.2f} cms')
                                    
                                    if distance > 7:
                                        time.sleep(2)
                                        print('Tag found at scanning antenna')
                                        conveyor_running = False
                                        sensor_running = False
                                        current_try = 0
                                        # Reset flags to restart
                                        conveyor_running = True
                                        sensor_running = True                                          
                                        break
                                    time.sleep(0.1)
                                                
                            else:
                                if tag_found == False:
                                    if current_try == 0:
                                        print('current_try:', current_try, 'No tag found at the antenna, trying one more time')
                                        current_try += 1
                                        
                                    else:
                                        print('current_try:', current_try, 'No tag found at the antenna, rotating barrel')
                                        time.sleep(1)  # Add a delay if needed before rotating the barrel
                                        servo()
                                        current_try += 1
                                        break
                                tag_found = False
                                
                                time.sleep(5)
                    break
servo_open = False
# servo_lock = threading.Lock()
def servo():
    global servo_open
    # with servo_lock:
    if servo_open == False:
        servo_pwm = GPIO.PWM(servo_signal, 50)
        servo_pwm.start(0)
        servo_pwm.ChangeDutyCycle(10)
        time.sleep(1)
        print('Servo is open')
        servo_open = True
        
    else:
        time.sleep(2)
        servo_pwm = GPIO.PWM(servo_signal, 50)
        servo_pwm.start(0)
        servo_pwm.ChangeDutyCycle(2)
        print('Servo is closed')
        servo_open = False

iv_spr = 1600
iv_rpm = 200      
iv_delay = 60 / (iv_spr * iv_rpm)
iv_rotations = 4   # Check with the number of rotations
iv_total_Steps = (iv_spr * iv_rotations) + 450
hold_iv = False
def iv():
    if hold_iv == False:
        GPIO.output(iv_dir, GPIO.LOW)
        for _ in range(iv_total_Steps):
            GPIO.output(iv_step, GPIO.HIGH)
            time.sleep(iv_delay / 2)
            GPIO.output(iv_step, GPIO.LOW)
            time.sleep(iv_delay / 2)
        time.sleep(2)
        print('Inlet Valve is open')
        GPIO.output(iv_dir, GPIO.HIGH)
        for _ in range(iv_total_Steps):
            GPIO.output(iv_step, GPIO.HIGH)
            time.sleep(iv_delay / 2)
            GPIO.output(iv_step, GPIO.LOW)
            time.sleep(iv_delay / 2)
        time.sleep(2)
        print('Inlet Valve is closed')
    else:
        GPIO.output(iv_step, GPIO.LOW)

conveyor_running = True
sensor_running = True
conveyor_lock = threading.Lock()

def conveyor():
    with conveyor_lock:
        conveyor_spr = 1600
        conveyor_rpm = 60
        conveyor_delay = 60 / (conveyor_spr * conveyor_rpm)
        global conveyor_running

        while True:
            GPIO.output(conveyor_dir, GPIO.LOW)
            if conveyor_running == True:
                GPIO.output(conveyor_step, GPIO.HIGH)
                time.sleep(conveyor_delay / 2)
                GPIO.output(conveyor_step, GPIO.LOW)
                time.sleep(conveyor_delay / 2)

            else:
                time.sleep(5)
                conveyor_running = True

speed_of_sound = 34300   # speed of sound (cms / s) at 20 Degree Celsius
sensor_lock = threading.Lock()
dist = 0
def measure_distance():
    with sensor_lock:
        global sensor_running, conveyor_running
        start_time = time.time()
        while time.time() - start_time < 7:  # Adjust the time condition
            if sensor_running == True:
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
                
                # Add a delay to measure distance every 0.5 seconds
                time.sleep(0.1)
                if distance < 5:
                    conveyor_running = False
                    sensor_running = False
                
            else:
                time.sleep(5)
                sensor_running = True
        return distance
try:
    
    barrel_thread = threading.Thread(target = barrel)
    barrel_thread.start()
    

    conveyor_thread = threading.Thread(target = conveyor)
    conveyor_thread.start()
    # conveyor_thread.join()
    # barrel_thread.join()

except KeyboardInterrupt:
    GPIO.cleanup()