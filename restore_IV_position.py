import RPi.GPIO as GPIO
import time
import os
import logging

# Set up logging
logging.basicConfig(filename='/home/Asclepion/Desktop/git/restore_iv.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Define GPIO pins
iv_step = 18
iv_dir = 23
iv_log_path = '/home/Asclepion/Desktop/git/iv_position.log'

# Set up GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(iv_step, GPIO.OUT)
GPIO.setup(iv_dir, GPIO.OUT)
iv_spr = 1600
iv_rpm = 200
iv_delay = 60 / (iv_spr * iv_rpm)
def restore_iv_position():
    logging.info('Restore IV Position script started')

    # Read the log file
    if not os.path.exists(iv_log_path):
        logging.info('No IV position log file found.')
        return

    with open(iv_log_path, 'r') as log_file:
        steps = log_file.readlines()
    
    total_steps = sum(1 if step.strip() == '1' else -1 for step in steps)

    if total_steps != 0:
        GPIO.output(iv_dir, GPIO.LOW if total_steps > 0 else GPIO.HIGH)
        for _ in range(abs(total_steps)):
            GPIO.output(iv_step, GPIO.HIGH)
            time.sleep(iv_delay / 2)  # Adjust timing as needed
            GPIO.output(iv_step, GPIO.LOW)
            time.sleep(iv_delay / 2)  # Adjust timing as needed
        logging.info(f'IV motor adjusted by {total_steps} steps')

    # Clean up
    if os.path.exists(iv_log_path):
        os.remove(iv_log_path)
        logging.info('IV position log file deleted after restoration')

    GPIO.cleanup()
    logging.info('Restore IV Position script completed')

if __name__ == '__main__':
    restore_iv_position()
