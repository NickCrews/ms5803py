import ms5803py
import time

s = ms5803py.MS5803()
while True:
    # Do the batteries-included version, optionally specifying an OSR.
    press, temp = s.read(pressure_osr=512)
    print("quick'n'easy pressure={} mBar, temperature={} C".format(press, temp))

    # Use the raw reads for more control, e.g. you need a faster sample
    # rate for pressure than for temperature. Use a high OverSampling Rate (osr)
    # value for a slow but accurate temperature read, and a low osr value
    # for quick and inaccurate pressure readings.
    raw_temperature = s.read_raw_temperature(osr=4096)
    for i in range(5):
        raw_pressure = s.read_raw_pressure(osr=256)
        press, temp = s.convert_raw_readings(raw_pressure, raw_temperature)
        print("advanced pressure={} mBar, temperature={} C".format(press, temp))

    time.sleep(1)
