import smbus
import time

class Sensor(object):

    DEFAULT_SENSOR_ADDR = 0x76

    # found from MS5803 datasheet (http://www.te.com/commerce/DocumentDelivery/DDEController?Action=showdoc&DocId=Data+Sheet%7FMS5803-14BA%7FB3%7Fpdf%7FEnglish%7FENG_DS_MS5803-14BA_B3.pdf%7FCAT-BLPS0013)
    RESET_CMD                           = 0x1E
    READ_PRESS_SENSITIVITY_CMD          = 0xA2
    READ_PRESS_OFFSET_CMD               = 0xA4
    READ_TEMP_COEFF_OF_PRESS_SENS_CMD   = 0xA6
    READ_TEMP_COEFF_OF_PRESS_OFFSET_CMD = 0xA8
    READ_REF_TEMP_CMD                   = 0xAA
    READ_TEMP_COEFF_OF_TEMP_CMD         = 0xAC

    READ_ADC_CMD                        = 0x00
    SELECT_PRESSURE_CMD                 = 0x40
    SELECT_TEMP_CMD                     = 0x50

    SLEEP_TIME = .005

    def __init__(self, address=None):
        if address is None:
            address = Sensor.DEFAULT_SENSOR_ADDR
        self.bus = smbus.SMBus(1)
        self.address = address
        self.bus.write_byte(self.address, Sensor.RESET_CMD)
        time.sleep(Sensor.SLEEP_TIME)
        self._coeffs = self._read_calibration_coeffs()

    def read(self, units='celsius'):
        '''
        return (pressure, temperature) in millibars and degrees celsius.

        Read in the raw temp and pressure readings,
        then correct them as described in the MS5803 data sheet (http://www.te.com/commerce/DocumentDelivery/DDEController?Action=showdoc&DocId=Data+Sheet%7FMS5803-14BA%7FB3%7Fpdf%7FEnglish%7FENG_DS_MS5803-14BA_B3.pdf%7FCAT-BLPS0013)

        '''
        # read the raw pressure
        self.bus.write_byte(self.address, Sensor.SELECT_PRESSURE_CMD)
        time.sleep(Sensor.SLEEP_TIME) #wait for ADC conversion
        value = self.bus.read_i2c_block_data(self.address, Sensor.READ_ADC_CMD, 3)
        D1 = value[0] * 65536 + value[1] * 256 + value[2]

        time.sleep(Sensor.SLEEP_TIME) #wait for command to go

        # read the raw temp
        self.bus.write_byte(self.address, Sensor.SELECT_TEMP_CMD)
        time.sleep(Sensor.SLEEP_TIME) #wait for ADC conversion
        value = self.bus.read_i2c_block_data(self.address, Sensor.READ_ADC_CMD, 3)
        D2 = value[0] * 65536 + value[1] * 256 + value[2]

        # perform conversion
        C1, C2, C3, C4, C5, C6 = self._coeffs
        dT = D2 - C5 * 256
        TEMP = 2000 + dT * C6 / 8388608
        OFF = C2 * 65536 + (C4 * dT) / 128
        SENS = C1 * 32768 + (C3 * dT ) / 256
        T2 = 0
        OFF2 = 0
        SENS2 = 0

        if TEMP > 2000 :
            T2 = 7 * (dT * dT)/ 137438953472
            OFF2 = ((TEMP - 2000) * (TEMP - 2000)) / 16
            SENS2= 0
        elif TEMP < 2000 :
        	T2 = 3 * (dT * dT) / 8589934592
        	OFF2 = 3 * ((TEMP - 2000) * (TEMP - 2000)) / 8
        	SENS2 = 5 * ((TEMP - 2000) * (TEMP - 2000)) / 8
        	if TEMP < -1500:
        		OFF2 = OFF2 + 7 * ((TEMP + 1500) * (TEMP + 1500))
        		SENS2 = SENS2 + 4 * ((TEMP + 1500) * (TEMP + 1500))

        TEMP = TEMP - T2
        OFF = OFF - OFF2
        SENS = SENS - SENS2
        pressure = ((((D1 * SENS) / 2097152) - OFF) / 32768.0) / 100.0
        temp = TEMP / 100.0
        if units in ['fahrenheit', 'Fahrenheit', 'F', 'f']:
            temp = (temp * 9/5) + 32
        return pressure, temp

    def _read_calibration_coeffs(self):
        # Read 12 bytes of calibration data
        # Read pressure sensitivity
        data = self.bus.read_i2c_block_data(self.address, Sensor.READ_PRESS_SENSITIVITY_CMD, 2)
        C1 = data[0] * 256 + data[1]

        # Read pressure offset
        data = self.bus.read_i2c_block_data(self.address, Sensor.READ_PRESS_OFFSET_CMD, 2)
        C2 = data[0] * 256 + data[1]

        # Read temperature coefficient of pressure sensitivity
        data = self.bus.read_i2c_block_data(self.address, Sensor.READ_TEMP_COEFF_OF_PRESS_SENS_CMD, 2)
        C3 = data[0] * 256 + data[1]

        # Read temperature coefficient of pressure offset
        data = self.bus.read_i2c_block_data(self.address, Sensor.READ_TEMP_COEFF_OF_PRESS_OFFSET_CMD, 2)
        C4 = data[0] * 256 + data[1]

        # Read reference temperature
        data = self.bus.read_i2c_block_data(self.address, Sensor.READ_REF_TEMP_CMD, 2)
        C5 = data[0] * 256 + data[1]

        # Read temperature coefficient of the temperature
        data = self.bus.read_i2c_block_data(self.address, Sensor.READ_TEMP_COEFF_OF_TEMP_CMD, 2)
        C6 = data[0] * 256 + data[1]

        return C1, C2, C3, C4, C5, C6
