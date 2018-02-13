#!/usr/bin/env python
# Michael Saunby. April 2013
#
# Notes.da
# pexpect uses regular expression so characters that have special meaning
# in regular expressions, e.g. [ and ] must be escaped with a backslash.
#
#   Copyright 2013 Michael Saunby
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import pexpect
import sys
import time
from sensor_calcs import *
import json
import select

def floatfromhex(h):
    t = float.fromhex(h)
    if t > float.fromhex('7FFF'):
        t = -(float.fromhex('FFFF') - t)
        pass
    return t

class SensorTag:

    def __init__( self, bluetooth_adr ):
		self.con = pexpect.spawn('gatttool -b ' + bluetooth_adr + ' --interactive')
		self.con.expect('\[LE\]>', timeout=600)
		print "Preparing to connect to " + bluetooth_adr + ". You might need to press the side button..."
		self.con.sendline('connect')
        # test for success of connect
		self.con.expect('Connection successful.*\[LE\]>')
        # Earlier versions of gatttool returned a different message.  Use this pattern -
        #self.con.expect('\[CON\].*>')
		self.cb = {}
		return

		self.con.expect('\[CON\].*>')
		self.cb = {}
		return

    def char_write_cmd( self, handle, value ):
        # The 0%x for value is VERY naughty!  Fix this!
        cmd = 'char-write-cmd 0x%02x 0%x' % (handle, value)
        print cmd
        self.con.sendline( cmd )
        return

    def char_read_hnd( self, handle ):
        self.con.sendline('char-read-hnd 0x%02x' % handle)
        self.con.expect('descriptor: .*? \r')
        after = self.con.after
        rval = after.split()[1:]
        return [long(float.fromhex(n)) for n in rval]

    # Notification handle = 0x0025 value: 9b ff 54 07
    def notification_loop( self ):
        while True:
	    try:
              pnum = self.con.expect('Notification handle = .*? \r', timeout=4)
            except pexpect.TIMEOUT:
              print "TIMEOUT exception!"
              break
	    if pnum==0:
                after = self.con.after
	        hxstr = after.split()[3:]
            	handle = long(float.fromhex(hxstr[0]))
            	#try:
	        if True:
                  self.cb[handle]([long(float.fromhex(n)) for n in hxstr[2:]])
            	#except:
                #  print "Error in callback for %x" % handle
                #  print sys.argv[1]
                pass
            else:
              print "TIMEOUT!!"
        pass

    def register_cb( self, handle, fn ):
        self.cb[handle]=fn;
        return

barometer = None
datalog = sys.stdout

class SensorCallbacks:

	address = ''
	sensorId = 0
	data = {}

	def __init__(self, addr, data):
		self.address = addr
		self.data = data
		self.sensorId = int(str(int(addr.replace(":", ""), 16))[-9:])
		self.data['sensors'][str(self.sensorId)] = {'id': self.sensorId};
		
	def tmp006(self,v):
		objT = (v[1]<<8)+v[0]
		ambT = (v[3]<<8)+v[2]
		targetT = calcTmpTarget(objT, ambT)
		ambient = calcTmpAmbient(ambT)
		# self.data['sensors'][str(self.sensorId)]['irTemperature'] = targetT
		self.data['sensors'][str(self.sensorId)]['ambientTemperature'] = ambient

	def humidity(self, v):
		rawT = (v[1]<<8)+v[0]
		rawH = (v[3]<<8)+v[2]
		(temp, humidity) = calcHum(rawT, rawH)
		self.data['sensors'][str(self.sensorId)]['humidity'] = humidity
		# self.data['sensors'][str(self.sensorId)]['humidityTemperature'] = temp

class SensorTagManager:

    def __init__( self, bluetooth_adr, data_store ):

		print bluetooth_adr
		while True:
			try:   
				print "Starting..."

				tag = SensorTag(bluetooth_adr)
				cbs = SensorCallbacks(bluetooth_adr, data_store)
			
				# enable TMP006 sensor
				tag.register_cb(0x25,cbs.tmp006)
				tag.char_write_cmd(0x29,0x01)
				tag.char_write_cmd(0x26,0x0100)

				# enable humidity
				tag.register_cb(0x38, cbs.humidity)
				tag.char_write_cmd(0x3c,0x01)
				tag.char_write_cmd(0x39,0x0100)

				tag.notification_loop()
			except:
				# print sys.exc_info()[0]
				pass

def main():
	SensorTagManager("78:A5:04:8C:1F:4C", {})

if __name__ == "__main__":
    main()

