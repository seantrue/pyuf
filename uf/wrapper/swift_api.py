#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, UFactory, Inc.
# All rights reserved.
#
# Author: Duke Fong <duke@ufactory.cc>


from __future__ import absolute_import
from time import sleep
from ..ufc import ufc_init
from ..swift import Swift
from ..utils.log import *
from itertools import imap


# SERVO NUMBER INDEX
SERVO_BOTTOM = 0
SERVO_LEFT = 1
SERVO_RIGHT = 2
SERVO_HAND = 3

## EEPROM DATA TYPE INDEX
EEPROM_DATA_TYPE_BYTE = 1
EEPROM_DATA_TYPE_INTEGER = 2
EEPROM_DATA_TYPE_FLOAT = 4


class SwiftAPI(object):
    u'''
    The API wrapper of swift and swift_pro
    default kwargs: dev_port = None, baud = 115200, filters = {'hwid': 'USB VID:PID=2341:0042'}
    '''
    def __init__(self, **kwargs):
        u'''
        '''
        
        self._ufc = ufc_init()
        
        # init swift node:
        
        swift_iomap = {
            u'pos_in':       u'pos_to_dev',
            u'pos_out':      u'pos_from_dev',
            u'buzzer':       u'buzzer',
            u'service':      u'service',
            u'gripper':      u'gripper',
            u'pump':         u'pump',
            u'limit_switch': u'limit_switch',
            u'keys':         u'keys',
            u'key0':         u'key0',
            u'key1':         u'key1',
            u'ptc_sync':     u'ptc_sync',
            u'ptc_report':   u'ptc_report',
            u'ptc':          u'ptc'
        }
        
        self._nodes = {}
        self._nodes[u'swift'] = Swift(self._ufc, u'swift', swift_iomap, **kwargs)
        
        
        # init swift_api node:
        
        self._ports = {
            u'pos_to_dev':   {u'dir': u'out', u'type': u'topic'},
            u'pos_from_dev': {u'dir': u'in', u'type': u'topic', u'callback': self._pos_from_dev_cb},
            u'buzzer':       {u'dir': u'out', u'type': u'topic'},
            u'service':      {u'dir': u'out', u'type': u'service'},
            u'gripper':      {u'dir': u'out', u'type': u'service'},
            u'pump':         {u'dir': u'out', u'type': u'service'},
            u'limit_switch': {u'dir': u'in', u'type': u'topic', u'callback': self._limit_switch_cb},
            u'keys':         {u'dir': u'out', u'type': u'service'},
            u'key0':         {u'dir': u'in', u'type': u'topic', u'callback': self._key0_cb},
            u'key1':         {u'dir': u'in', u'type': u'topic', u'callback': self._key1_cb},
            u'ptc':          {u'dir': u'out', u'type': u'service'}
        }
        
        self._iomap = {
            u'pos_to_dev':   u'pos_to_dev',
            u'pos_from_dev': u'pos_from_dev',
            u'buzzer':       u'buzzer',
            u'service':      u'service',
            u'gripper':      u'gripper',
            u'pump':         u'pump',
            u'limit_switch': u'limit_switch',
            u'keys':         u'keys',
            u'key0':         u'key0',
            u'key1':         u'key1',
            u'ptc':          u'ptc'
        }
        
        self.pos_from_dev_cb = None
        self._dev_info = None
        
        self._node = u'swift_api'
        self._logger = logging.getLogger(self._node)
        self._ufc.node_init(self._node, self._ports, self._iomap)
        
    
    def _pos_from_dev_cb(self, msg):
        if self.pos_from_dev_cb != None:
            values = list(imap(lambda i: float(i[1:]), msg.split(u' ')))
            self.pos_from_dev_cb(values)
    
    def _limit_switch_cb(self, msg):
        pass
    def _key0_cb(self, msg):
        pass
    def _key1_cb(self, msg):
        pass
    
    def reset(self):
        u'''
        Reset include below action:
          - Attach all servos
          - Move to default position (150, 0, 150) with speed 200mm/min
          - Turn off pump/gripper
          - Set wrist servo to angle 90
        
        Returns:
            None
        '''
        self.set_servo_attach()
        sleep(0.1)
        self.set_position(150, 0, 150, speed = 200, wait = True)
        self.set_pump(False)
        self.set_gripper(False)
        self.set_wrist(90)
    
    def send_cmd_sync(self, msg):
        u'''
        This function will block until receive the response message.
        
        Args:
            msg: string, serial command
        
        Returns:
            string response
        '''
        return self._ports[u'service'][u'handle'].call(u'set cmd_sync ' + msg)
    
    def send_cmd_async(self, msg):
        u'''
        This function will send out the message and return immediately.
        
        Args:
            msg: string, serial command
        
        Returns:
            None
        '''
        self._ports[u'service'][u'handle'].call(u'set cmd_async ' + msg)
    
    def get_device_info(self):
        u'''
        Get the device info.
        
        Returns:
            string list: [device model, hardware version, firmware version, api version, device UID]
        '''
        ret = self._ports[u'service'][u'handle'].call(u'get dev_info')
        if ret.startswith(u'ok'):
            return list(imap(lambda i: i[1:], ret.split(u' ')[1:]))
        self._logger.error(u'get_dev_info ret: %s' % ret)
        return None
    
    def get_is_moving(self):
        u'''
        Get the arm current moving status.
        
        Returns:
            boolean True or False
        '''
        ret = self._ports[u'service'][u'handle'].call(u'set cmd_sync M2200')
        if ret == u'ok V0':
            return False
        if ret == u'ok V1':
            return True
        self._logger.error(u'get_is_moving ret: %s' % ret)
        return None
    
    def flush_cmd(self):
        u'''
        Wait until all async command return
        
        Returns:
            boolean True or False
        '''
        ret = self._ports[u'ptc'][u'handle'].call(u'set flush')
        if ret == u'ok':
            return True
        return False
    
    def set_position(self, x = None, y = None, z = None,
                           speed = None, relative = False, wait = False):
        u'''
        Move arm to the position (x,y,z) unit is mm, speed unit is mm/sec
        
        Args:
            x
            y
            z
            speed
            relative
            wait: if True, will block the thread, until get response or timeout
        
        Returns:
            True if successed
        '''
        if wait:
            cmd = u'set cmd_sync'
        else:
            cmd = u'set cmd_async'
        
        if relative:
            cmd += u' G2204'
        else:
            cmd += u' G0'
        
        if x != None:
            cmd += u' X{}'.format(x)
        if y != None:
            cmd += u' Y{}'.format(y)
        if z != None:
            cmd += u' Z{}'.format(z)
        if speed != None:
            cmd += u' F{}'.format(speed)
        
        ret = self._ports[u'service'][u'handle'].call(cmd)
        return ret.startswith(u'ok') # device return 'ok' even out of range
    
    def get_position(self):
        u'''
        Get current arm position (x,y,z)
        
        Returns:
            float array of the format [x, y, z] of the robots current location
        '''
        ret = self._ports[u'service'][u'handle'].call(u'set cmd_sync P2220')
        
        if ret.startswith(u'ok '):
            values = list(imap(lambda i: float(i[1:]), ret.split(u' ')[1:]))
            return values
        self._logger.error(u'get_position ret: %s' % ret)
        return None
    
    def set_polar(self, s = None, r = None, h = None, 
                        speed = None, relative = False, wait = False):
        u'''
        Polar coordinate, rotation, stretch, height.
        
        Args:
            stretch(mm)
            rotation(degree)
            height(mm)
            speed: speed(mm/min)
            relative
            wait: if True, will block the thread, until get response or timeout
        
        Returns:
            True if successed
        '''
        if wait:
            cmd = u'set cmd_sync'
        else:
            cmd = u'set cmd_async'
        
        if relative:
            cmd += u' G2205'
        else:
            cmd += u' G2201'
        
        if s != None:
            cmd += u' S{}'.format(s)
        if r != None:
            cmd += u' R{}'.format(r)
        if h != None:
            cmd += u' H{}'.format(h)
        if speed != None:
            cmd += u' F{}'.format(speed)
        
        ret = self._ports[u'service'][u'handle'].call(cmd)
        return ret.startswith(u'ok')
    
    def get_polar(self):
        u'''
        Get polar coordinate
        
        Returns:
            float array of the format [rotation, stretch, height]
        '''
        ret = self._ports[u'service'][u'handle'].call(u'set cmd_sync P2221')
        
        if ret.startswith(u'ok '):
            values = list(imap(lambda i: float(i[1:]), ret.split(u' ')[1:]))
            return values
        self._logger.error(u'get_polar ret: %s' % ret)
        return None
    
    def set_servo_angle(self, servo_id, angle, wait = False):
        u'''
        Set servo angle, 0 - 180 degrees, this Function will include the manual servo offset.
        
        Args:
            servo_id: SERVO_BOTTOM, SERVO_LEFT, SERVO_RIGHT, SERVO_HAND
            angle: 0 - 180 degrees
            wait: if True, will block the thread, until get response or timeout
        
        Returns:
            succeed True or failed False
        '''
        cmd = u'set cmd_sync' if wait else u'set cmd_async'
        cmd += u' G2202 N{} V{}'.format(servo_id, angle)
        ret = self._ports[u'service'][u'handle'].call(cmd)
        return ret.startswith(u'ok')
    
    def set_wrist(self, angle, wait = False):
        u'''
        Set swift hand wrist angle. include servo offset.
        
        Args:
            angle: 0 - 180 degrees
            wait: if True, will block the thread, until get response or timeout
        
        Returns:
            succeed True or failed False
        '''
        return self.set_servo_angle(SERVO_HAND, angle, wait = wait)
    
    def get_servo_angle(self, servo_id = None):
        u'''
        Get servo angle
        
        Args:
            servo_id: return an array if servo_id not provided,
                      else specify: SERVO_BOTTOM, SERVO_LEFT, SERVO_RIGHT, SERVO_HAND
        
        Returns:
            array of float or single float
        '''
        values = [None] * 3
        if servo_id != SERVO_HAND:
            ret = self._ports[u'service'][u'handle'].call(u'set cmd_sync P2200')
            if ret.startswith(u'ok '):
                values = list(imap(lambda i: float(i[1:]), ret.split(u' ')[1:]))
            else:
                self._logger.error(u'get_servo_angle N0~2 ret: %s' % ret)
        if servo_id == SERVO_HAND or servo_id == None:
            ret = self._ports[u'service'][u'handle'].call(u'set cmd_sync P2206 N3')
            if ret.startswith(u'ok '):
                values.append(float(ret[4:]))
            else:
                self._logger.error(u'get_servo_angle N3 ret: %s' % ret)
        
        if servo_id == None:
            return values
        else:
            return values[servo_id]
    
    def set_servo_attach(self, servo_id = None, wait = False):
        u'''
        Set servo status attach, servo attach will lock the servo, you can't move swift with your hands.
        
        Args:
            servo_id: if None, will attach all servos, else specify: SERVO_BOTTOM, SERVO_LEFT, SERVO_RIGHT, SERVO_HAND
            wait: if True, will block the thread, until get response or timeout
        
        Returns:
            succeed True or Failed False
        '''
        cmd = u'set cmd_sync' if wait else u'set cmd_async'
        if servo_id == None:
            cmd += u' M17'
        else:
            cmd += u' M2201 N{}'.format(servo_id)
        ret = self._ports[u'service'][u'handle'].call(cmd)
        return ret.startswith(u'ok')
    
    def set_servo_detach(self, servo_id = None, wait = False):
        u'''
        Set Servo status detach, Servo Detach will unlock the servo, You can move swift with your hands.
        But move function won't be effect until you attach.
        
        Args:
            servo_id: if None, will detach all servos, else specify: SERVO_BOTTOM, SERVO_LEFT, SERVO_RIGHT, SERVO_HAND
            wait: if True, will block the thread, until get response or timeout
        
        Returns:
            succeed True or Failed False
        '''
        cmd = u'set cmd_sync' if wait else u'set cmd_async'
        if servo_id == None:
            cmd += u' M2019'
        else:
            cmd += u' M2202 N{}'.format(servo_id)
        ret = self._ports[u'service'][u'handle'].call(cmd)
        return ret.startswith(u'ok')
    
    def get_servo_attach(self, servo_id = None):
        u'''
        Check servo attach status
        
        Args:
            servo_id: SERVO_BOTTOM, SERVO_LEFT, SERVO_RIGHT, SERVO_HAND
            wait: if True, will block the thread, until get response or timeout
        
        Returns:
            succeed True or Failed False
        '''
        cmd = u'set cmd_sync M2203 N{:d}'.format(servo_id)
        ret = self._ports[u'service'][u'handle'].call(cmd)
        if ret == u'ok V0':
            return False
        if ret == u'ok V1':
            return True
        self._logger.error(u'get_servo_attach ret: %s' % ret)
        return None
    
    def set_report_position(self, interval):
        u'''
        Report currentpPosition in (interval) seconds.
        
        Args:
            interval: seconds, if 0 disable report
        
        Returns:
            None
        '''
        cmd = u'set report_pos on {}'.format(round(interval, 2))
        ret = self._ports[u'service'][u'handle'].call(cmd)
        if ret.startswith(u'ok'):
            return
        self._logger.error(u'set_report_position ret: %s' % ret)
    
    def register_report_position_callback(self, callback = None):
        u'''
        Set function to receiving current position [x, y, z, r], r is wrist angle.
        
        Args:
            callback: set the callback function, undo by setting to None
        
        Returns:
            None
        '''
        self.pos_from_dev_cb = callback
    
    def set_buzzer(self, freq = 1000, time = 200):
        u'''
        Control buzzer.
        
        Args:
            freq: frequency
            time: time period
        
        Returns:
            None
        '''
        self._ports[u'buzzer'][u'handle'].publish(u'F{} T{}'.format(freq, time))
    
    def set_pump(self, on, timeout = None):
        u'''
        Control pump on or off
        
        Args:
            on: True on, False off
            timeout: unsupported currently
        
        Returns:
            succeed True or failed False
        '''
        cmd = u'set value on' if on else u'set value off'
        ret = self._ports[u'pump'][u'handle'].call(cmd)
        if ret.startswith(u'ok'):
            return True
        self._logger.warning(u'set_pump ret: %s' % ret)
        return False
    
    def set_gripper(self, catch, timeout = None):
        u'''
        Turn on/off gripper
        
        Args:
            catch: True on / False off
            wait: if True, will block the thread, until get response or timeout
        
        Returns:
            succeed True or failed False
        '''
        cmd = u'set value on' if catch else u'set value off'
        ret = self._ports[u'gripper'][u'handle'].call(cmd)
        if ret.startswith(u'ok'):
            return True
        self._logger.warning(u'set_gripper ret: %s' % ret)
        return False
    
    def get_analog(self, pin):
        u'''
        Get analog value from specific pin
        
        Args:
            pin: pin number
        
        Returns:
            integral value
        '''
        ret = self._ports[u'service'][u'handle'].call(u'set cmd_sync P2241 N{}'.format(pin))
        if ret.startswith(u'ok '):
            return int(ret[4:])
        self._logger.error(u'get_analog ret: %s' % ret)
        return None
    
    def get_digital(self, pin):
        u'''
        Get digital value from specific pin.
        
        Args:
            pin: pin number
        
        Returns:
            high True or low False
        '''
        ret = self._ports[u'service'][u'handle'].call(u'set cmd_sync P2240 N{}'.format(pin))
        if ret == u'ok V1':
            return True
        elif ret == u'ok V0':
            return False
        self._logger.error(u'get_digital ret: %s' % ret)
        return None
    
    def set_rom_data(self, address, data, data_type = EEPROM_DATA_TYPE_BYTE):
        u'''
        Set data to eeprom
        
        Args:
            address: 0 - 64K byte
            data_type: EEPROM_DATA_TYPE_FLOAT, EEPROM_DATA_TYPE_INTEGER, EEPROM_DATA_TYPE_BYTE
        
        Returns:
            True on success
        '''
        ret = self._ports[u'service'][u'handle'].call(u'set cmd_sync M2212 N1 A{} T{} V{}'.format(address, data_type, data))
        if ret.startswith(u'ok'):
            return True
        self._logger.error(u'get_rom_data ret: %s' % ret)
        return None
    
    def get_rom_data(self, address, data_type = EEPROM_DATA_TYPE_BYTE):
        u'''
        Get data from eeprom
        
        Args:
            address: 0 - 64K byte
            data_type: EEPROM_DATA_TYPE_FLOAT, EEPROM_DATA_TYPE_INTEGER, EEPROM_DATA_TYPE_BYTE
        
        Returns:
            int or float value
        
        Notes:
            EEPROM default data format, each item is one offline record data (no header at beginning):
              [p0, p1, p2, p3, p4, p5 ... p_end]
            
            each record data is 10 bytes, and each item inside is 2 bytes:
              [a0, a1, a2, a3, accessories_state]
            
            a0~3: unsigned fixed point of servos' angle (multiply by 100)
            
            accessories_state:
              bit0: pump on/off
              bit4: griper on/off
            
            p_end indicate the end of records, filled by 0xffff
        '''
        ret = self._ports[u'service'][u'handle'].call(u'set cmd_sync M2211 N1 A{} T{}'.format(address, data_type))
        if ret.startswith(u'ok '):
            return int(ret[4:]) if data_type != EEPROM_DATA_TYPE_FLOAT else float(ret[4:])
        self._logger.error(u'get_rom_data ret: %s' % ret)
        return None

