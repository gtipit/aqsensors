# -*- coding: utf-8 -*-
"""Doc string."""

################################################################################
import socket

hostname = socket.gethostname()

# ASEMPARM = '0499'
OBJECTNO = '01000000'
DISPSITE = 'disp.asem.com.ua/upload.wsgi'
PKEYPATH = '/home/asem/.ssh/id_rsa'

MQTTHOST = 'tipit.kiev.ua'
# MQTTHOST = '81.95.183.44'
MQTTPORT = 1883
MQTTUSER = 'device'
MQTTPASS = 'sensor'

MQTTPUBT = 'tele/%s/SENSORS' % hostname

FLUXHOST = '127.0.0.1'
FLUXPORT = 8086
FLUXUSER = 'asem'
FLUXPASS = 'mesa'

FLUXDBNM = 'aqsensors'

# TELEPERIOD =
################################################################################
# The End
