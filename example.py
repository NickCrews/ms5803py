import ms5803py
import time

s = ms5803py.Sensor()
for _ in range(5):
    press, temp = s.read()
    print("pressure=%f mBar, temp=%f C"% (press, temp))
    time.sleep(1)
