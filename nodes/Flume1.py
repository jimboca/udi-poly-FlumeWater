
try:
    import polyinterface
except ImportError:
    import pgc_interface as polyinterface
import sys
import time
import urllib3

LOGGER = polyinterface.LOGGER

class Flume1Node(polyinterface.Node):

    def __init__(self, controller, primary, address, name):
        super(Flume1Node, self).__init__(controller, primary, address, name)
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
        {'driver': 'GV1', 'value': 0, 'uom': 69}, #
        {'driver': 'GV2', 'value': 0, 'uom': 69}, #
        {'driver': 'GV3', 'value': 0, 'uom': 69}, #
        {'driver': 'GV4', 'value': 0, 'uom': 69}, #
        {'driver': 'GV5', 'value': 0, 'uom': 69}, #
        {'driver': 'GV6', 'value': 0, 'uom': 69}, #
        {'driver': 'GV7', 'value': 0, 'uom': 69}, #
    ]
    id = 'flume1'
    commands = {
                }
