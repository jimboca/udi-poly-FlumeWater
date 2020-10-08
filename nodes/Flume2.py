
try:
    import polyinterface
except ImportError:
    import pgc_interface as polyinterface
import sys
import time
import urllib3
import pyflume
from datetime import timedelta
from requests import Session

LOGGER = polyinterface.LOGGER

class Flume2Node(polyinterface.Node):

    def __init__(self, controller, primary, address, name, device):
        super(Flume2Node, self).__init__(controller, primary, address, name)
        self.device = device
        self.device_id = device['id']
        self.lpfx = '%s:%s' % (address,name)

    def start(self):
        self.setDriver('ST', 1)
        self.session = Session()
        self.scan_interval = timedelta(minutes=self.controller.current_interval_minutes)
        self.flume = pyflume.FlumeData(
            self.controller.auth,
            self.device_id,
            self.device['location']['tz'],
            self.scan_interval,
            http_session=self.session,
        )
        self.update()

    def shortPoll(self):
        pass

    def longPoll(self):
        self.update()

    def update(self):
        LOGGER.debug("Values={}".format(self.flume.values))
        self.flume.update()
        self.setDriver('GV1',self.flume.values['current_interval'])
        self.setDriver('GV2',self.flume.values['last_60_min'])
        self.setDriver('GV3',self.flume.values['last_24_hrs'])
        self.setDriver('GV4',self.flume.values['today'])
        self.setDriver('GV5',self.flume.values['last_30_days'])
        self.setDriver('GV6',self.flume.values['week_to_date'])
        self.setDriver('GV7',self.flume.values['month_to_date'])

    def query(self,command=None):
        self.update()
        self.reportDrivers()

    "Hints See: https://github.com/UniversalDevicesInc/hints"
    hint = [1,2,3,4]
    id = 'flume2'
    drivers = [
        {'driver': 'ST', 'value': 0, 'uom': 2},
        {'driver': 'GV1', 'value': 0, 'uom': 69}, # Current current_interval
        {'driver': 'GV2', 'value': 0, 'uom': 69}, # Last 60 Min last_60_min
        {'driver': 'GV3', 'value': 0, 'uom': 69}, # Last 24 Hours last_24_hrs
        {'driver': 'GV4', 'value': 0, 'uom': 69}, # Today today
        {'driver': 'GV5', 'value': 0, 'uom': 69}, # Last 30 Days last_30_days
        {'driver': 'GV6', 'value': 0, 'uom': 69}, # Week To Date week_to_date
        {'driver': 'GV7', 'value': 0, 'uom': 69}, # Month To Date month_to_date
    ]
    commands = {
            }
