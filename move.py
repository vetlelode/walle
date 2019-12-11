
import easygopigo3 as easy
from simple_pid import PID


def move(bearing, leftMotorSpeed, rightMotorSpeed, pid):
    gpg = easy.Easygopigo3()
    motorSpeed = 100
    output = pid(bearing)
    # calculate motor speedss
    leftMotorSpeed = int(motorSpeed + output)
    rightMotorSpeed = int(motorSpeed - output)
    if leftMotorSpeed == 0:
        leftMotorSpeed = 1
    if rightMotorSpeed == 0:
        rightMotorSpeed = 1
    gpg.set_motor_dps(gpg.MOTOR_LEFT, dps=leftMotorSpeed)
    gpg.set_motor_dps(gpg.MOTOR_RIGHT, dps=rightMotorSpeed)
    return leftMotorSpeed, rightMotorSpeed, pid
