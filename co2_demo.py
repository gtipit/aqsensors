# -*- coding: utf-8 -*-
"""
Created on Aug 19, 2016.

@author: matuschd
"""

from pmsensor import co2sensor

if __name__ == '__main__':
    ppm = co2sensor.read_mh_z19("/dev/ttyS2")
    print("CO2 concentration is {} ppm".format(ppm))
    print(co2sensor.read_mh_z19_with_temperature("/dev/ttyS2"))
    # print("CO2 concentration is {} ppm".format(ppm))
