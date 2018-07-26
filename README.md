[![MS5803-14BA](ms5803.jpg)](https://www.sparkfun.com/products/12909)

# ms5803py
Python 3 library for MS5803-14BA pressure sensor for Raspberry Pi

Based off of the [Adafruit Arduino Library](https://github.com/sparkfun/MS5803-14BA_Breakout) and the [Control Everything Python Library](https://github.com/ControlEverythingCommunity/MS5803-14BA). Some of the math is complicated when correcting raw readings to actual temperatures and pressures, that math can be verified from the [MS5803-14BA datasheet](http://www.te.com/commerce/DocumentDelivery/DDEController?Action=showdoc&DocId=Data+Sheet%7FMS5803-14BA%7FB3%7Fpdf%7FEnglish%7FENG_DS_MS5803-14BA_B3.pdf%7FCAT-BLPS0013).

## Installation
This should be on pypi soon, and so you can install on your RPi using
````
pip3 install ms5803py
````

## Usage
The MS5803 and the RPi use the I2C protocol to communicate, so you need to have I2C set up on your pi, as explained in [this Adafruit tutorial](https://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-i2c). After that, the MS5803 needs to be hooked up to the Raspberry Pi as described in [this Adafruit tutorial](https://learn.sparkfun.com/tutorials/ms5803-14ba-pressure-sensor-hookup-guide).

After doing that, you must find the I2C address of your MS5803. To do this, run the following command both before and after plugging in the MS5803. Whatever address shows up is the one you want:
```
sudo i2cdetect -y 1
````
It should be either `0X76` or `0x77`, as described in the [MS5803-14BA datasheet](http://www.te.com/commerce/DocumentDelivery/DDEController?Action=showdoc&DocId=Data+Sheet%7FMS5803-14BA%7FB3%7Fpdf%7FEnglish%7FENG_DS_MS5803-14BA_B3.pdf%7FCAT-BLPS0013), depending on if the CSB (Chip Select) pin on the MS5803 is high or low. On the [Sparkfun breakout board](https://www.sparkfun.com/products/12909) the I2C address is `0x76`, so I have that set as the default if you don't specify an address when initializing the sensor.
