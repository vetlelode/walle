from easygopigo3 import EasyGoPiGo3
from simple_pid import PID


def move(bearing, leftMotorSpeed, rightMotorSpeed, pid):
    gpg = EasyGoPiGo3()
    motorSpeed = 50
    output = pid(bearing)
    print(output)
    # calculate motor speedss
    leftMotorSpeed = int(motorSpeed + output)
    rightMotorSpeed = int(motorSpeed + output)
    if leftMotorSpeed == 0:
        leftMotorSpeed = 1
    if rightMotorSpeed == 0:
        rightMotorSpeed = 1
    if abs(bearing) <= 5:
        rightMotorSpeed = 100
        leftMotorSpeed = 100
    gpg.set_motor_dps(gpg.MOTOR_LEFT, dps=leftMotorSpeed)
    gpg.set_motor_dps(gpg.MOTOR_RIGHT, dps=rightMotorSpeed)
    return leftMotorSpeed, rightMotorSpeed, pid


def stop():
    gpg = EasyGoPiGo3()
    gpg.stop()
