import easygopigo3 as easy
import time


def move(bearing, cent_x, cent_y, line_scan_length, line_from_cent, direction):
    gpg = easy.EasyGoPiGo3()
    # Really stupid simple way of doing some basic error corrections
    if line_from_cent >= 180 and bearing <= 0 and direction == "r":
        gpg.turn_degrees(20)
        return
    elif line_from_cent <= 180 and bearing >= 10 and direction == "l":
        print("lEFt")
        gpg.turn_degrees(-20)
        return

    if (abs(bearing) <= 10):
        gpg.turn_degrees(bearing/2, False)
        gpg.drive_cm(8)

    else:
        if (abs(bearing) >= 60):
            gpg.turn_degrees(bearing / 3)
        else:
            gpg.turn_degrees(bearing / 4)

        gpg.drive_cm(5)
