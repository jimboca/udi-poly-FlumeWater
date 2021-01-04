

"""
Get the polyinterface objects we need.  Currently Polyglot Cloud uses
a different Python module which doesn't have the new LOG_HANDLER functionality
"""
try:
    from polyinterface import Controller,LOG_HANDLER,LOGGER
except ImportError:
    from pgc_interface import Controller,LOGGER
import logging
from requests import Session
import pyflume

# My Template Node
from nodes import Flume1Node,Flume2Node
from node_funcs import id_to_address,get_valid_node_name,get_valid_node_address
KEY_DEVICE_TYPE = "type"
KEY_DEVICE_ID = "id"
TYPE_TO_NAME = {1: 'Hub', 2: 'Sensor'}

# IF you want a different log format than the current default
#LOG_HANDLER.set_log_format('%(asctime)s %(threadName)-10s %(name)-18s %(levelname)-8s %(module)s:%(funcName)s: %(message)s')

class Controller(Controller):
    """
    The Controller Class is the primary node from an ISY perspective. It is a Superclass
    of polyinterface.Node so all methods from polyinterface.Node are available to this
    class as well.
    """
    def __init__(self, polyglot):
        super(Controller, self).__init__(polyglot)
        self.name = 'Flume Water Controller'
        self.hb = 0
        self._mydrivers = {}
        # This can be used to call your function everytime the config changes
        # But currently it is called many times, so not using.
        #self.poly.onConfig(self.process_config)

    def start(self):
        # TODO: Currently fails on PGC
        try:
            serverdata = self.poly.get_server_data(check_profile=True)
        except Exception as ex:
            LOGGER.error('get_server_data failed, is this PGC?: {}'.format(ex))
            serverdata = {}
            serverdata['version'] = "FIXME_PGC"
            self.poly.installprofile()
        LOGGER.info('Started Template NodeServer {}'.format(serverdata['version']))
        #LOGGER.debug('ST=%s',self.getDriver('ST'))
        self.set_driver('ST', 1)
        self.set_driver('GV2', 0)
        self.heartbeat(0)
        self.ready = self.check_params()
        #self.set_debug_level(self.getDriver('GV1'))
        if self.ready:
            if self.connect():
                self.discover()

    def shortPoll(self):
        for node in self.nodes:
            if node != self.address:
                self.nodes[node].shortPoll()

    def longPoll(self):
        LOGGER.debug('longPoll')
        self.heartbeat()
        for node in self.nodes:
            if node != self.address:
                self.nodes[node].longPoll()

    def query(self,command=None):
        self.check_params()
        for node in self.nodes:
            self.nodes[node].reportDrivers()

    def delete(self):
        LOGGER.info('Oh God I\'m being deleted. Nooooooooooooooooooooooooooooooooooooooooo.')

    def stop(self):
        LOGGER.debug('NodeServer stopped.')

    def process_config(self, config):
        # this seems to get called twice for every change, why?
        # What does config represent?
        LOGGER.info("process_config: Enter config={}".format(config))
        LOGGER.info("process_config: Exit")

    def heartbeat(self,init=False):
        LOGGER.debug('heartbeat: init={}'.format(init))
        if init is not False:
            self.hb = init
        LOGGER.debug('heartbeat: hb={}'.format(self.hb))
        if self.hb == 0:
            self.reportCmd("DON",2)
            self.hb = 1
        else:
            self.reportCmd("DOF",2)
            self.hb = 0

    def set_debug_level(self,level):
        LOGGER.debug('set_debug_level: {}'.format(level))
        if level is None:
            level = 10
        level = int(level)
        if level == 0:
            level = 30
        LOGGER.info('set_debug_level: Set GV1 to {}'.format(level))
        self.set_driver('GV1', level)
        # 0=All 10=Debug are the same because 0 (NOTSET) doesn't show everything.
        if level <= 10:
            LOGGER.setLevel(logging.DEBUG)
        elif level == 20:
            LOGGER.setLevel(logging.INFO)
        elif level == 30:
            LOGGER.setLevel(logging.WARNING)
        elif level == 40:
            LOGGER.setLevel(logging.ERROR)
        elif level == 50:
            LOGGER.setLevel(logging.CRITICAL)
        else:
            LOGGER.debug("set_debug_level: Unknown level {}".format(level))
        if level < 10:
            LOG_HANDLER.set_basic_config(True,logging.DEBUG)
        else:
            # This is the polyinterface default
            LOG_HANDLER.set_basic_config(True,logging.WARNING)

    def check_params(self):
        """
        This is an example if using custom Params for user and password and an example with a Dictionary
        """
        self.removeNoticesAll()
        default_username = "YourUserName"
        default_password = "YourPassword"
        default_client_id = "YourClientId"
        default_client_secret = "YourClientSecret"
        default_current_interval_minutes = 5
        add_param = False

        self.username = self.getCustomParam('username')
        if self.username is None:
            self.username = default_username
            LOGGER.error('check_params: username not defined in customParams, please add it.  Using {}'.format(self.username))
            add_param = True

        self.password = self.getCustomParam('password')
        if self.password is None:
            self.password = default_password
            LOGGER.error('check_params: password not defined in customParams, please add it.  Using {}'.format(self.password))
            add_param = True

        self.client_id = self.getCustomParam('client_id')
        if self.client_id is None:
            self.client_id = default_client_id
            LOGGER.error('check_params: client_id not defined in customParams, please add it.  Using {}'.format(self.client_id))
            add_param = True

        self.client_secret = self.getCustomParam('client_secret')
        if self.client_secret is None:
            self.client_secret = default_client_secret
            LOGGER.error('check_params: client_secret not defined in customParams, please add it.  Using {}'.format(self.client_secret))
            add_param = True

        self.current_interval_minutes = self.getCustomParam('current_interval_minutes')
        if self.current_interval_minutes is None:
            self.current_interval_minutes = default_current_interval_minutes
            add_param = True

        if (add_param):
            self.addCustomParam({
                'username': self.username,
                'password': self.password,
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'current_interval_minutes': self.current_interval_minutes
                })

        # Add a notice if they need to change the username/password from the default.
        if self.username == default_username or self.password == default_password or self.client_id == default_client_id or self.client_secret == default_client_secret:
            # This doesn't pass a key to test the old way.
            msg = 'Please set your information in configuration page, and restart this nodeserver'
            self.addNotice({'config': msg})
            LOGGER.error(msg)
            return False
        else:
            return True

    def connect(self):
        self.session = Session()
        LOGGER.info("Connecting to Flume...")
        self.set_driver('GV2',1)
        try:
            self.auth = pyflume.FlumeAuth(
                self.username, self.password, self.client_id, self.client_secret, http_session=self.session
            )
            self.set_driver('GV2',2)
            LOGGER.info("Flume Auth={}".format(self.auth))
        except Exception as ex:
            self.set_driver('GV2',3)
            msg = 'Error from PyFlue: ' + ex
            LOGGER.error(msg)
            self.addNotice({'auth': msg})
            return False
        except:
            self.set_driver('GV2',3)
            msg = 'Unknown Error from PyFlue: ' + ex
            LOGGER.error(msg)
            self.addNotice({'auth': msg})
            LOGGER.error(msg,exc_info=True)
            return False
        self.flume_devices = pyflume.FlumeDeviceList(self.auth)
        devices = self.flume_devices.get_devices()
        LOGGER.info("Connecting complete...")
        return True

    def discover(self, *args, **kwargs):
        cst = int(self.get_driver('GV2'))
        if cst == 2:
            for device in self.flume_devices.device_list:
                if device[KEY_DEVICE_TYPE] <= 2:
                    ntype   = 'Flume{}Node'.format(device[KEY_DEVICE_TYPE])
                    address = id_to_address(device[KEY_DEVICE_ID])
                    name    = 'Flume {} {}'.format(TYPE_TO_NAME[device[KEY_DEVICE_TYPE]],device[KEY_DEVICE_ID])
                    # TODO: How to use ntype as the function to call?
                    if (device[KEY_DEVICE_TYPE] == 1):
                        self.addNode(Flume1Node(self, self.address, address, name, device))
                    else:
                        self.addNode(Flume2Node(self, self.address, address, name, device))
        else:
            if cst == 0:
                LOGGER.error("Can not discover, Connection has not started")
            elif cst == 1:
                LOGGER.error("Can not discover, Connection is started but not complete")
            elif cst == 3:
                LOGGER.error("Can not discover, Connection Failed")
            else:
                LOGGER.error("Can not discover, Unknown error")

    def set_driver(self,drv,val):
        self._mydrivers[drv] = val
        self.setDriver(drv,val)

    def get_driver(self,drv):
        if drv in self._mydrivers:
            return self._mydrivers[drv]
        return self.getDriver(drv)

    def update_profile(self,command):
        LOGGER.info('update_profile:')
        st = self.poly.installprofile()
        return st

    def cmd_set_debug_mode(self,command):
        val = int(command.get('value'))
        LOGGER.debug("cmd_set_debug_mode: {}".format(val))
        self.set_debug_level(val)

    """
    """
    id = 'controller'
    commands = {
        'QUERY': query,
        'DISCOVER': discover,
        'SET_DM': cmd_set_debug_mode,
        'UPDATE_PROFILE': update_profile,
    }
    drivers = [
        {'driver': 'ST',  'value': 1, 'uom':  2},
        {'driver': 'GV1', 'value': 10, 'uom': 25}, # Debug (Log) Mode, default=30=Warning
        {'driver': 'GV2', 'value':  0, 'uom': 25}, # Authorization status
    ]
