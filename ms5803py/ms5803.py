import smbus
import time

class MS5803(object):
    '''MS5803-14BA temperature and pressure sensor for Raspberry Pi over i2c.

    This will work for the TE Connectivity MS5803-14BA (14 bar) sensor, whose
    datasheet can be found at https://www.te.com/commerce/DocumentDelivery/DDEController?Action=showdoc&DocId=Data+Sheet%7FMS5803-14BA%7FB3%7Fpdf%7FEnglish%7FENG_DS_MS5803-14BA_B3.pdf%7FCAT-BLPS0013.
    This will also work for the SparkFun breakout board (https://www.sparkfun.com/products/12909).

    This class allows you to read both the pressure and temperature
    in one simple read() request, or you can use read_raw_pressure(),
    read_raw_temperature(), and convert_raw_readings() functions individually,
    if you need finer-grained control.

    You can read the temp and pressure at different OverSampling Rates (OSR).
    A higher OSR leads to greater resolution/accuracy but requires a longer
    conversion time. The available OSR rates are available in MS5803.OSRs.
    More info on OSR at https://www.cypress.com/file/236481/download.
    '''

    # The address of the i2c or SPI device is either 0x76 or 0x77,
    # depending on if the CSB (chip select) pin is pulled high or low.
    # On the SparkFun breakout board it is pulled high, therefore we
    # use this as the default.
    DEFAULT_SENSOR_ADDR = 0x76

    # Command to reset the MS5803, should be sent at startup.
    _CMD_RESET                           = 0x1E

    # At the factory the sensor is calibrated, with 6 calibration
    # constants written to the sensor's ROM. We read these at device
    # initialization and use them to correct the raw temperature
    # and pressure readings from the sensor.
    # Read pressure sensitivity.
    _CMD_READ_C1                         = 0xA2
    # Read pressure offset.
    _CMD_READ_C2                         = 0xA4
    # Read temperature coefficient of pressure sensitivity.
    _CMD_READ_C3                         = 0xA6
    # Read temperature coefficient of pressure offset.
    _CMD_READ_C4                         = 0xA8
    # Read reference temperature.
    _CMD_READ_C5                         = 0xAA
    # Read temperature coefficient of the temperature.
    _CMD_READ_C6                         = 0xAC

    # Commands to start ADC conversion at different OSR values.
    _CMD_SELECT_PRESSURE_OSR256          = 0x40
    _CMD_SELECT_PRESSURE_OSR512          = 0x42
    _CMD_SELECT_PRESSURE_OSR1024         = 0x44
    _CMD_SELECT_PRESSURE_OSR2048         = 0x46
    _CMD_SELECT_PRESSURE_OSR4096         = 0x48

    # Commands to start ADC conversion at different OSR values.
    _CMD_SELECT_TEMPERATURE_OSR256       = 0x50
    _CMD_SELECT_TEMPERATURE_OSR512       = 0x52
    _CMD_SELECT_TEMPERATURE_OSR1024      = 0x54
    _CMD_SELECT_TEMPERATURE_OSR2048      = 0x56
    _CMD_SELECT_TEMPERATURE_OSR4096      = 0x58

    # After starting a conversion with one of the SELECT commands above and
    # waiting for the conversion to finish, read the value from the ADC.
    _CMD_READ_ADC                        = 0x00

    # Map from different OSR values to commands.
    _SELECT_PRESSURE_COMMANDS = {
        256:  _CMD_SELECT_PRESSURE_OSR256,
        512:  _CMD_SELECT_PRESSURE_OSR512,
        1024: _CMD_SELECT_PRESSURE_OSR1024,
        2048: _CMD_SELECT_PRESSURE_OSR2048,
        4096: _CMD_SELECT_PRESSURE_OSR4096,
    }
    _SELECT_TEMPERATURE_COMMANDS = {
        256:  _CMD_SELECT_TEMPERATURE_OSR256,
        512:  _CMD_SELECT_TEMPERATURE_OSR512,
        1024: _CMD_SELECT_TEMPERATURE_OSR1024,
        2048: _CMD_SELECT_TEMPERATURE_OSR2048,
        4096: _CMD_SELECT_TEMPERATURE_OSR4096,
    }

    # According to the ADC table in the PERFORMANCE SPECIFICATIONS section of
    # the datasheet, the following are the number of seconds we need to
    # wait between making a read request and actually reading a value, for a
    # given OSR value. If we don't wait long enough, the ADC will return 0!
    CONVERSION_TIMES = {
        256:   .60/1000,
        512:  1.17/1000,
        1024: 2.28/1000,
        2048: 4.54/1000,
        4096: 9.04/1000,
    }

    # Utility for users of this class.
    OSRs = [256, 512, 1024, 2048, 4096]

    def __init__(self, bus=1, address=None):
        '''Create and reset a sensor instance, then read calibration coefficients.

        Keyword arguments:
        bus -- i2c bus. Default is 1.
        address -- i2c address of the sensor. Default is 0x76.
        '''
        self.bus = smbus.SMBus(bus)
        if address is None:
            address = MS5803.DEFAULT_SENSOR_ADDR
        self.address = address
        self._write(MS5803._CMD_RESET)
        # We seem to need to give the sensor a chance to reset or reading
        # the coefficients fails. 2ms seems to be the threshold for me, so
        # use 5ms to be safe.
        time.sleep(.005)
        self._coeffs = self._read_calibration_coeffs()

    def read(self, pressure_osr=4096, temperature_osr=4096):
        '''Return current (pressure, temperature) in millibars and Celsius.

        Keyword arguments:
        pressure_osr -- passed onwards to read_raw_pressure(osr=pressure_osr).
                        Default is 4096.
        temperature_osr -- passed onwards to read_raw_temperature(osr=temperature_osr)
                           Default is 4096.
        '''
        raw_pressure = self.read_raw_pressure(osr=pressure_osr)
        raw_temperature = self.read_raw_temperature(osr=temperature_osr)

        return self.convert_raw_readings(raw_pressure, raw_temperature)

    def read_raw_pressure(self, osr=4096):
        '''Return the raw pressure value from the sensor.

        The raw reading should be converted with convert_raw_readings().

        Keyword arguments:
        osr -- OverSampling Rate. Default is 4096, the most accurate but slowest.
        '''
        self._write(MS5803._SELECT_PRESSURE_COMMANDS[osr])
        time.sleep(MS5803.CONVERSION_TIMES[osr])
        return self._read(MS5803._CMD_READ_ADC, 3)

    def read_raw_temperature(self, osr=256):
        '''Return the raw temperature value from the sensor.

        The raw reading should be converted with convert_raw_readings().

        Keyword arguments:
        osr -- OverSampling Rate. Default is 4096, the most accurate but slowest.
        '''
        self._write(MS5803._SELECT_TEMPERATURE_COMMANDS[osr])
        time.sleep(MS5803.CONVERSION_TIMES[osr])
        return self._read(MS5803._CMD_READ_ADC, 3)

    def convert_raw_readings(self, raw_pressure, raw_temperature):
        '''Convert raw pressure and temperature values to millibars and Celsius.

        Uses the factory-calibrated coefficients retrieved from sensor ROM to
        perform the 2nd order temperature correction described in figure 16
        of the datasheet.
        '''
        # It actually is important to use integer division here, or the conversion
        # does not follow the example values in figure 15 of the datasheet.
        C1, C2, C3, C4, C5, C6 = self._coeffs
        # Difference between raw temp and reference temp.
        dT = raw_temperature - (C5 * 2**8)
        # Actual temperature (-40...85C with units of 0.01C).
        TEMP = 2000 + ((dT * C6) // 2**23)

        # Pressure offset at actual temperature.
        OFF  = (C2 * 2**16) + ((C4 * dT) // 2**7)
        # Pressure sensitivity at actual temperature.
        SENS = (C1 * 2**15) + ((C3 * dT) // 2**8)

        # Do second order temperature correction of TEMP, OFF, and SENS.
        if TEMP < 2000 :
            # Colder than 20C.
            T2 = (3 * dT**2) // 2**33
            OFF2 =  (3 * (TEMP - 2000)**2) // 2**1
            SENS2 = (5 * (TEMP - 2000)**2) // 2**3
            if TEMP < -1500:
                # Colder than -15C, adjust OFF2 and SENS2 a bit more.
                OFF2 =  OFF2  + (7 * (TEMP + 1500)**2)
                SENS2 = SENS2 + (4 * (TEMP + 1500)**2)
        else:
            T2 = (7 * dT**2) // 2**37
            OFF2 = (TEMP - 2000)**2 // 2**4
            SENS2 = 0
        TEMP = TEMP - T2
        OFF  = OFF  - OFF2
        SENS = SENS - SENS2

        # Temperature compensated pressure (0...14bar with units of 0.1mbar).
        PRESS = (((raw_pressure * SENS) // 2**21) - OFF) // 2**15

        # Convert to floating point mbar and degrees celsius.
        pressure = PRESS / 10.0
        temp = TEMP / 100.0

        return pressure, temp

    def _write(self, cmd):
        self.bus.write_byte(self.address, cmd)

    def _read(self, cmd, size):
        '''
        Read a |size| byte integer from the sensor after making request |cmd|.

        Individual bytes are returned over i2c most-significant-first,
        so bit shift them into one int.
        '''
        bytes = self.bus.read_i2c_block_data(self.address, cmd, size)
        result = 0
        for i, byte in enumerate(bytes):
            shift = ((size - i) - 1) * 8
            result |= byte << shift

        return result

    def _read_calibration_coeffs(self):
        C1 = self._read(MS5803._CMD_READ_C1, 2)
        C2 = self._read(MS5803._CMD_READ_C2, 2)
        C3 = self._read(MS5803._CMD_READ_C3, 2)
        C4 = self._read(MS5803._CMD_READ_C4, 2)
        C5 = self._read(MS5803._CMD_READ_C5, 2)
        C6 = self._read(MS5803._CMD_READ_C6, 2)
        return C1, C2, C3, C4, C5, C6
