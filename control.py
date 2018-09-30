from flask import Flask, jsonify, request, Response
import RPi.GPIO as GPIO
import time
import json

GPIO.setmode(GPIO.BCM)
pwmA_pin = 23
pwmB_pin = 24
in1_pin = 17
in2_pin = 27
in3_pin = 5
in4_pin = 6
GPIO.setup(pwmA_pin, GPIO.OUT)
GPIO.setup(pwmB_pin, GPIO.OUT)
GPIO.setup(in1_pin, GPIO.OUT)
GPIO.setup(in2_pin, GPIO.OUT)
GPIO.setup(in3_pin, GPIO.OUT)
GPIO.setup(in4_pin, GPIO.OUT)
pwm_motor1 = GPIO.PWM(pwmA_pin, 100)
pwm_motor2 = GPIO.PWM(pwmB_pin, 100)
pwm_motor1.start(0)
pwm_motor2.start(0)

app = Flask(__name__)


@app.route('/messages', methods=['POST'])
def api_message():
    data = request.args.get('data')
    control(data)


def control(key):
    print(key)

    if key == 'w':
        print ("forward")
        pwm_motor1.ChangeDutyCycle(0)
        pwm_motor2.ChangeDutyCycle(80)
        GPIO.output(in1_pin, True)
        GPIO.output(in2_pin, False)
        GPIO.output(in3_pin, False)
        GPIO.output(in4_pin, True)
    elif key == 'a':
        print ("Left")
        pwm_motor1.ChangeDutyCycle(60)
        pwm_motor2.ChangeDutyCycle(80)
        GPIO.output(in1_pin, False)
        GPIO.output(in2_pin, True)
        GPIO.output(in3_pin, False)
        GPIO.output(in4_pin, True)
    elif key == 'd':
        print ("Right")
        pwm_motor1.ChangeDutyCycle(60)
        pwm_motor2.ChangeDutyCycle(80)
        GPIO.output(in1_pin, True)
        GPIO.output(in2_pin, False)
        GPIO.output(in3_pin, False)
        GPIO.output(in4_pin, True)

    elif key == 'quit':
        quit()


if __name__ == '__main__':
    app.run(host='192.168.0.8', port=5002, debug=False)
