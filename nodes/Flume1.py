
try:
    import polyinterface
except ImportError:
    import pgc_interface as polyinterface
import sys
import time
import urllib3

LOGGER = polyinterface.LOGGER

class Flume1Node(polyinterface.Node):

    def __init__(self, controller, primary, address, name, device):
        super(Flume1Node, self).__init__(controller, primary, address, name)
        self.device = device
        self.lpfx = '%s:%s' % (address,name)

    def start(self):
        self.setDriver('ST', 1)

    def shortPoll(self):
        pass

    def longPoll(self):
        pass

    def query(self,command=None):
        self.reportDrivers()

    "Hints See: https://github.com/UniversalDevicesInc/hints"
    hint = [1,2,3,4]
    drivers = [
        {'driver': 'ST', 'value': 0, 'uom': 2},
    ]
    id = 'flume1'
    commands = {
                }
