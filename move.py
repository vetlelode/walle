import easygopigo3 as easy

gpg = easy.EasyGoPiGo3()

for x in range(2):

    radius = 30
    gpg.orbit(-270, radius)  # to rotate to the left
    gpg.drive_cm(radius * 2)  # move forward
    gpg.orbit(270, radius)  # to rotate to the right
    gpg.drive_cm(radius * 2)  # move forward
    rn_degrees(720)
