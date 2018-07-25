import ms5803py
import time

s = ms5803py.Sensor()
while True
    press, temp = s.read()
    print("pressure=%f mBar, temp=%f C"% (press, temp))
    time.sleep(1)
