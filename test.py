from multiprocessing import Process, Queue
import time

class Dummy:
    def __init__(self, Q):
        self.Q = Q
    
    def async_keys(self):
        time.sleep(2)
        i = 0 
        while i < 10:
            self.Q.put((i))
            i += 1
    
    def async_write(self):
        time.sleep(3)
        events = []
        i = 0 
        while i < 3:
            if self.Q.empty():
                i += 1
                time.sleep(0.05)
                continue
            i = 0 
            event = self.Q.get()
            print(event)
            events.append(event)
        print(events)

def main():
    q = Queue()
    testDum = Dummy(q)
    

    p1 = Process(target=testDum.async_keys())
    p2 = Process(target=testDum.async_write())

    p1.start()
    p2.start()

    p1.join()
    p2.join()

if __name__ == '__main__':
    main()