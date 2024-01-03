from djitellopy import Tello
import cv2
from pynput import keyboard
from pynput.keyboard import Key, KeyCode
from os.path import join
import time
from threading import Thread
from multiprocessing import Queue

# Speed of the drone
S = 60
# Frames per second of the pygame window display
# A low number also results in input lag, as input information is processed once per frame.
FPS = 30
data_dir = "/Users/max/Desktop/Swifty/data"

class FrontEnd(object):
    """ Maintains the Tello display and moves it through the keyboard keys.
        Press escape key to quit.
        The controls are:
            - T: Takeoff
            - L: Land
            - Arrow keys: Forward, backward, left and right.
            - A and D: Counter clockwise and clockwise rotations (yaw)
            - W and S: Up and down.

    """

    def __init__(self, Q):

        # Init Tello object that interacts with the Tello drone
        self.tello = Tello()

        # Drone velocities between -100~100
        self.for_back_velocity = 0
        self.left_right_velocity = 0
        self.up_down_velocity = 0
        self.yaw_velocity = 0
        self.speed = 10
        self.send_rc_control = False
        self.Q = Q
        self.online = False

    def run(self):

        self.tello.connect()
        self.tello.set_speed(self.speed)

        # In case streaming is on. This happens when we quit this program without the escape key.
        self.tello.streamoff()
        self.tello.streamon()

        self.online = True
        print("getting frame")
        frame_read = self.tello.get_frame_read()
        time.sleep(0.5)
        print("coming online")
        print(f"Battery % : {self.tello.get_battery()}")
        while self.online:
            self.update() # update for every event
            # capturing the current drone state
            state = {
                "fb" : self.for_back_velocity,
                "lr" : self.left_right_velocity,
                "ud" : self.up_down_velocity,
                "yw" : self.yaw_velocity
            }
            # capturing the telemetry
            telem = self.tello.get_current_state()
            self.Q.put((telem, frame_read.frame, state))
            # sleepy time
            time.sleep(1/30)
        # Call it always before finishing. To deallocate resources.
        self.tello.streamoff()
        print(f"Battery % : {self.tello.get_battery()}")
        self.tello.end()

    def keydown(self, key):
        """ Update velocities based on key pressed
        Arguments:
            key: pygame key
        """
        # update callback
        if key == Key.up:  # set forward velocity
            self.for_back_velocity = S
        elif key == Key.down:  # set backward velocity
            self.for_back_velocity = -S
        elif key == Key.left:  # set left velocity
            self.left_right_velocity = -S
        elif key == Key.right:  # set right velocity
            self.left_right_velocity = S
        elif key == KeyCode.from_char('w'):  # set up velocity
            self.up_down_velocity = S
        elif key == KeyCode.from_char('s'):  # set down velocity
            self.up_down_velocity = -S
        elif key == KeyCode.from_char('a'):  # set yaw counter clockwise velocity
            self.yaw_velocity = -S
        elif key == KeyCode.from_char('d'):  # set yaw clockwise velocity
            self.yaw_velocity = S

    def keyup(self, key):
        """ Update velocities based on key released
        Arguments:
            key: pygame key
        """
        if key == Key.up or key == Key.down:  # set zero forward/backward velocity
            self.for_back_velocity = 0
        elif key == Key.left or key == Key.right:  # set zero left/right velocity
            self.left_right_velocity = 0
        elif key == KeyCode.from_char('w') or key == KeyCode.from_char('s'):  # set zero up/down velocity
            self.up_down_velocity = 0
        elif key == KeyCode.from_char('a') or key == KeyCode.from_char('d'):  # set zero yaw velocity
            self.yaw_velocity = 0
        elif key == KeyCode.from_char('t'):  # takeoff
            try: 
                self.tello.takeoff()
                self.send_rc_control = True
            except Exception as e:
                print(e)
        elif key == KeyCode.from_char('l'):  # land
            self.tello.land()
            self.send_rc_control = False
        elif key == Key.esc: # break loop
            self.send_rc_control = False
            self.online = False

    def update(self):
        """ Update routine. Send velocities to Tello.
        """
        time.sleep(0.001)
        if self.send_rc_control:
            self.tello.send_rc_control(self.left_right_velocity, self.for_back_velocity,
                self.up_down_velocity, self.yaw_velocity)

    def write_video(self):
        # setting up video recorder
        print("writing to disk")
        # screen dims: h = 300, w = 400
        video = cv2.VideoWriter(join(data_dir,'video.avi'), cv2.VideoWriter_fourcc(*'XVID'), 30, (960, 720))
        while not self.Q.empty():
            # getting items from the Q
            telem, frame, state = self.Q.get()
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            # writing video
            video.write(frame)
            
            # writing telemetry
            with open(join(data_dir,'telemetry.txt'), 'a') as file:
                # writing telemetry 
                file.write(str(telem)+"\n")
            
            # input is important for training
            with open(join(data_dir,'input.txt'), 'a') as file:
                # writing telemetry 
                file.write(str(state)+"\n")
        print("write end.")

# main idea: 
# two processes, one sends/receives data irt and offloads data to the queue,
# the seconds writes the data to the disk async

def main():
    q = Queue()
    fe = FrontEnd(q)

    listener = keyboard.Listener(
        on_press=fe.keydown,
        on_release=fe.keyup)
    listener.start()
    fe.run()
    listener.stop()

    # because blocking I guess
    fe.write_video()
    # recorder = Thread(target=fe.write_video())
    # recorder.start()
    # recorder.join()

if __name__ == '__main__':
    main()