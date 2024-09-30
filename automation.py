import RPi.GPIO as GPIO
import time
import threading
import os
import logging
import sys


logging.basicConfig(filename='/home/Asclepion/Desktop/git/automation.log', level=logging.INFO, format='%(asctime)s - %(message)s')

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
GPIO.setup(limit_switch, GPIO.IN, pull_up_down=GPIO.PUD_UP)
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
barrel_spr = 1600
barrel_rpm = 1.5
barrel_delay = 60 / (barrel_spr * barrel_rpm)
iv_spr = 1600
iv_rpm = 200
iv_delay = 60 / (iv_spr * iv_rpm)
iv_rotations = 13
iv_total_steps = (iv_spr * iv_rotations) + 300   
speed_of_sound = 34300
iv_log_path = '/home/Asclepion/Desktop/git/iv_position.log'
programmed_units_file_path = '/home/Asclepion/Desktop/lattepanda_share/programmed_units_count.txt'
faulty_units_file_path = '/home/Asclepion/Desktop/lattepanda_share/faulty_units_count.txt'

barrel_alligned = False
barrel_lock = threading.Lock()
tag_found = False
units_to_program = int(sys.argv[1]) if len(sys.argv) > 1 else 1
programmed_units = 0
faulty_units = 0
automation_active = True
stop_conveyor_flag = False
servo_open = False
conveyor_running = True
hold_iv = False
sensor_running = True
conveyor_lock = threading.Lock()
loaded_tags = int(sys.argv[2]) if len(sys.argv) > 2 else None

def update_programmed_units_file():
    with open(programmed_units_file_path, 'w') as f:
        f.write(str(programmed_units))

def update_faulty_units_file():
    with open(faulty_units_file_path, 'w') as f:
        f.write(str(faulty_units))

def barrel():
    global barrel_alligned, current_try, max_tries, distance, tag_found, conveyor_running, sensor_running, programmed_units, faulty_units, units_to_program, automation_active
    with barrel_lock:
        for i in range(8):
            if not automation_active:
                break
            while True:
                GPIO.output(barrel_dir, GPIO.LOW)
                if not barrel_alligned:
                    if GPIO.input(limit_switch) == GPIO.HIGH:
                        GPIO.output(barrel_step, GPIO.HIGH)
                        time.sleep(barrel_delay / 2)
                        GPIO.output(barrel_step, GPIO.LOW)
                        time.sleep(barrel_delay / 2)
                    else:
                        time.sleep(0.5)
                        logging.info('Limit switch pressed')
                        time.sleep(1)
                        for steps_taken in range(166):
                            GPIO.output(barrel_step, GPIO.HIGH)
                            time.sleep(barrel_delay / 2)
                            GPIO.output(barrel_step, GPIO.LOW)
                            time.sleep(barrel_delay / 2)
                            logging.info(f'Steps taken: {steps_taken}')
                        logging.info('Barrel is aligned')
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
                            while time.time() - start_time < 4:
                                if sensor_running:
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
                                    logging.info(f'Distance: {distance:.2f} cm')
                                    if distance > 6:
                                        time.sleep(1)
                                        logging.info('Tag found at scanning antenna')
                                        conveyor_running = False
                                        sensor_running = False
                                        time.sleep(1)
                                        directory_path = '/home/Asclepion/Desktop/lattepanda_share/'
                                        ready_file_path = os.path.join(directory_path, 'next_tag_is_ready_for_programming.txt')
                                        success_file_path = os.path.join(directory_path, 'programming_of_current_tag_succeeded.txt')

                                        if not os.path.exists(directory_path):
                                            os.makedirs(directory_path)
                                        
                                        with open(ready_file_path, 'w') as file:
                                            file.write('1')

                                        
                                        current_try = 0
                                        
                                        while not os.path.exists(success_file_path):
                                            time.sleep(1)
                                        with open(success_file_path, 'r') as success_file:
                                            success_content = success_file.read().strip()
                                        conveyor_running = True
                                        sensor_running = True
                                        if success_content == '1':
                                            programmed_units += 1
                                            update_programmed_units_file()  
                                            rotate_conveyor_clockwise()
                                        elif success_content == '0':
                                            faulty_units += 1
                                            update_faulty_units_file()
                                            rotate_conveyor_anticlockwise()
                                        os.remove(success_file_path)
                                        
                                        if programmed_units >= units_to_program:
                                            logging.info(f'Programmed {programmed_units} units. Conveyor running for 5 seconds before stopping.')
                                            conveyor_running = True
                                            time.sleep(2)
                                            os.remove(programmed_units_file_path)
                                            os.remove(faulty_units_file_path)
                                            time.sleep(3)
                                            conveyor_running = False
                                            automation_active = False

                                            if loaded_tags is not None:
                                                if programmed_units >= loaded_tags:
                                                    servo()
                                            
                                            return  
                                        
                                        break
                                    time.sleep(0.1)
                            else:
                                if not tag_found:
                                    if i != 7:
                                        if current_try == 0:
                                            logging.info(f'current_try: {current_try} No tag found at the antenna, trying one more time')
                                            current_try += 1
                                        else:
                                            logging.info(f'current_try: {current_try} No tag found at the antenna, rotating barrel')
                                            time.sleep(1)
                                            servo()
                                            break
                                    else:
                                        if current_try == 0:
                                            logging.info(f'current_try: {current_try} No tag found at the antenna, trying one more time')
                                            current_try += 1
                                        else:
                                            logging.info(f'current_try: {current_try} No tag found at the antenna, all the magazines are empty')
                                            time.sleep(1)
                                            conveyor_running = False
                                            servo()
                                            break
                                tag_found = False
                                time.sleep(5)
                        break
                else:
                    time.sleep(1)
                
                    barrel_alligned = False


def servo():
    global servo_open
    if not servo_open:
        servo_pwm = GPIO.PWM(servo_signal, 50)
        servo_pwm.start(0)
        servo_pwm.ChangeDutyCycle(2.67475)
        time.sleep(1)
        logging.info('Servo is open')
        servo_open = True
    else:
        time.sleep(2)
        servo_pwm = GPIO.PWM(servo_signal, 50)
        servo_pwm.start(0)
        servo_pwm.ChangeDutyCycle(3.75)
        logging.info('Servo is closed')
        servo_open = False

def iv():
    global hold_iv, automation_active

    if not hold_iv and automation_active:

        if os.path.exists(iv_log_path):
            os.remove(iv_log_path)

        with open(iv_log_path, 'w') as log_file:
            GPIO.output(iv_dir, GPIO.HIGH)

            logging.info('Starting forward movement of IV motor')
            for _ in range(iv_total_steps):
                GPIO.output(iv_step, GPIO.HIGH)
                time.sleep(iv_delay / 2)
                GPIO.output(iv_step, GPIO.LOW)
                time.sleep(iv_delay / 2)
                log_file.write('1\n')
                
            logging.info('Forward movement complete')

            time.sleep(0.5)
            GPIO.output(iv_dir, GPIO.LOW)

            logging.info('Starting backward movement of IV motor')
            for _ in range(iv_total_steps):
                GPIO.output(iv_step, GPIO.HIGH)
                time.sleep(iv_delay / 2)
                GPIO.output(iv_step, GPIO.LOW)
                time.sleep(iv_delay / 2)
                log_file.write('0\n')  

            logging.info('Backward movement complete')

        if os.path.exists(iv_log_path):
            os.remove(iv_log_path)
            logging.info('IV position log file deleted after completion')
    else:
        GPIO.output(iv_step, GPIO.LOW)

def conveyor():
    with conveyor_lock:
        conveyor_spr = 1600
        conveyor_rpm = 70
        conveyor_delay = 60 / (conveyor_spr * conveyor_rpm)
        global conveyor_running, stop_conveyor_flag
        GPIO.output(conveyor_dir, GPIO.HIGH)
        while True:
            if conveyor_running:
                GPIO.output(conveyor_step, GPIO.HIGH)
                time.sleep(conveyor_delay / 2)
                GPIO.output(conveyor_step, GPIO.LOW)
                time.sleep(conveyor_delay / 2)
            elif stop_conveyor_flag:
                GPIO.output(conveyor_step, GPIO.HIGH)
                time.sleep(conveyor_delay / 2)
                GPIO.output(conveyor_step, GPIO.LOW)
                time.sleep(conveyor_delay / 2)
            else:
                time.sleep(1)

def measure_distance():
    global sensor_running, conveyor_running, distance, current_try, max_tries, tag_found
    while current_try < max_tries:
        start_time = time.time()
        while time.time() - start_time < 7:
            if sensor_running:
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
                logging.info(f'Distance: {distance:.2f} cm')

def rotate_conveyor_clockwise():
    GPIO.output(conveyor_dir, GPIO.HIGH)

def rotate_conveyor_anticlockwise():
    GPIO.output(conveyor_dir, GPIO.LOW)
    time.sleep(10)
    GPIO.output(conveyor_dir, GPIO.HIGH)

def restore_iv_position():
    if not os.path.exists(iv_log_path):
        print("No IV position log file found.")
        return
    
    with open(iv_log_path, 'r') as log_file:
        steps = log_file.readlines()
    
    GPIO.output(iv_dir, GPIO.HIGH)
    for step in steps:
        if step.strip() == '1':
            GPIO.output(iv_step, GPIO.HIGH)
            time.sleep(iv_delay / 2)
            GPIO.output(iv_step, GPIO.LOW)
            time.sleep(iv_delay / 2)
        elif step.strip() == '0':
            GPIO.output(iv_dir, GPIO.LOW)
            GPIO.output(iv_step, GPIO.HIGH)
            time.sleep(iv_delay / 2)
            GPIO.output(iv_step, GPIO.LOW)
            time.sleep(iv_delay / 2)
    
    logging.info('IV motor position restored')

try:
    
    barrel_thread = threading.Thread(target=barrel)
    barrel_thread.start()

    conveyor_thread = threading.Thread(target=conveyor)
    conveyor_thread.start()
    
except KeyboardInterrupt:
    GPIO.cleanup()