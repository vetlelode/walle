import easygopigo3 as easy
import time


def move(bearing, cent_x, cent_y, line_scan_length, line_from_cent):
    gpg = easy.EasyGoPiGo3()
    gpg.turn_degrees(bearing/4)
    gpg.drive_cm(5)
