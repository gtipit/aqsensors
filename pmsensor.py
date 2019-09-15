#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PMS1003.

Get data and store to influx db.
"""
import os
import sys
import logging
import time
# from pmsensor import serial_data_collector as pm
from pmsensor import serial_pm as pm

from influxdb import InfluxDBClient
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#
# from datetime import datetime
#
from local_conf import FLUXHOST, FLUXPORT, FLUXUSER, FLUXPASS, FLUXDBNM
# from local_conf import SOURDEST
##
path = os.path.dirname(__file__)
sys.path.append(path)
os.chdir(path)


def main():
    """Doc string."""
    logging.basicConfig(level=logging.INFO)
    sensors = []
#    sensors.append(pm.PMDataCollector("/dev/tty.wchusbserial144740",
#                                      pm.SUPPORTED_SENSORS["novafitness,sds011"]))
#    sensors.append(pm.PMDataCollector("/dev/tty.SLAB_USBtoUART",
#                                      pm.SUPPORTED_SENSORS["oneair,s3"]))
    sensors.append(pm.PMDataCollector("/dev/ttyS1",
                                      pm.SUPPORTED_SENSORS["plantower,pms1003"]))

    client = InfluxDBClient(FLUXHOST, FLUXPORT, FLUXUSER, FLUXPASS, FLUXDBNM)

    for s in sensors:
        print(s.supported_values())

    while True:
        for s in sensors:
            # print(s.read_data())
            iso = int(time.time() * 1000000000)
            sdata = s.read_data()
            print(sdata)
            measurement = 'ug/m3'
            for i in sdata:
                print(i, sdata[i])
                data = [
                    {
                        "measurement": measurement,
                        "tags": {
                            "parameter": i,
                        },
                        "time": iso,
                        "fields": {
                            "value": sdata[i]
                        }
                    }
                ]
                print(data)
                # # Send the JSON data to InfluxDB
                client.write_points(data)

        time.sleep(15)

if __name__ == '__main__':
    main()
