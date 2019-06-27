import unittest
import ms5803py

class MS5803Test(unittest.TestCase):
    '''To run tests simply run "python3 test.py"'''

    def setUp(self):
        self.ms5803 = ms5803py.MS5803()

    def test_basic_read(self):
        print("pressure={} mBar, temperature={} C".format(*self.ms5803.read()))

    def test_pressure_reads(self):
        for osr in self.ms5803.OSRs:
            print("raw temp(osr={})={}".format(osr, self.ms5803.read_raw_pressure(osr=osr)))

    def test_temperature_reads(self):
        for osr in self.ms5803.OSRs:
            print("raw temp(osr={})={}".format(osr, self.ms5803.read_raw_temperature(osr=osr)))

    def test_stress(self):
        print("Reading the temperature as quickly as possible...")
        for _ in range(50):
            print("raw temp={}".format(self.ms5803.read_raw_temperature(osr=256)))

    def test_stress_init(self):
        print("Creating 50 sensors as quickly as possible...")
        for _ in range(50):
            print("pressure={} mBar, temperature={} C".format(*self.ms5803.read()))

    def test_conversion(self):
        '''Test with the example values given in figure 15 of the datasheet.'''
        old_coeffs = self.ms5803._coeffs
        self.ms5803._coeffs = 46546, 42845, 29751, 29457, 32745, 29059
        p, t = self.ms5803.convert_raw_readings(4311550, 8387300)
        self.ms5803._coeffs = old_coeffs

        self.assertAlmostEqual(p, 1000.5)
        self.assertAlmostEqual(t, 20.15)

if __name__ == '__main__':
    unittest.main(verbosity=2)
