import time, cv2
from threading import Thread
from djitellopy import Tello

tello = Tello()

tello.connect()

print(tello.get_battery())