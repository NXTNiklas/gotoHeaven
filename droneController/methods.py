#
##############################################################################
#
# @file       example.py
# @author     The LibrePilot Project, http://www.librepilot.org Copyright (C) 2017.
#             The OpenPilot Team, http://www.openpilot.org Copyright (C) 2011.
# @brief      Base classes for python UAVObject
#   
# @see        The GNU Public License (GPL) Version 3
#
#############################################################################/
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#
# 


import logging
import serial
import traceback
import sys
import time
import datetime

#Bibliotheken einbinden
import time
import math
import json
import threading    
 

from thread import start_new_thread
from librepilot.uavtalk.uavobject import *
from librepilot.uavtalk.uavtalk import *
from librepilot.uavtalk.objectManager import *
from librepilot.uavtalk.connectionManager import *
from bufferedSerialReader import BufferedSerialReader

def _hex02(value):
    return "%02X" % value

class UAVTalkDemo():
    def __init__(self,ws):
        self.__ws = ws
        self.__armed = False
        self.nbUpdates = 0
        self.lastRateCalc = time.time()
        self.updateRate = 0
        self.objMan = None
        self.connMan = None
        self.__setuped = False
        self.__running = True
        
        self.eprint("setuped!")
    
    def run(self):
        self.eprint("Drone started!")
        
        while self.__running:
            """ DO Stuff"""
           
            
            
        self.eprint("thread not running anymore")
        
    def eprint(self,message):
        print message
        #self.__ws.write_message(json.dumps(message))
        
    def terminate(self):
        self.__running = False

    

    def setup(self, port):
        # type: (WebSocket, int) ->
        self.eprint("Opening Port \"%s\"" % port)
        if port[:3].upper() == "COM":
            _port = int(port[3:]) - 1
        else:
            _port = port
        serPort = serial.Serial(_port, 57600, timeout=.5)
        if not serPort.isOpen():
            raise IOError("Failed to open serial port")

        self.eprint("Creating UavTalk")
        self.uavTalk = UavTalk(serPort, None)

        self.eprint("Starting ObjectManager")
        self.objMan = ObjManager(self.uavTalk)
        self.objMan.importDefinitions()

        self.eprint("Starting UavTalk")
        self.uavTalk.start()

        self.eprint("Starting ConnectionManager")
        self.connMan = ConnectionManager(self.uavTalk, self.objMan)

        self.eprint("Connecting...")
        self.connMan.connect()
        self.eprint("Connected")

        self.eprint("Getting all Data")
        self.objMan.requestAllObjUpdate()
        self.__setuped = True
        self.eprint("Complete!")

    # self.eprint("SN:",
    # sn = self.objMan.FirmwareIAPObj.CPUSerial.value
    # self.eprint("".join(map(_hex02, sn))

    def stop(self):
        try:
            if self.uavTalk:
               self.eprint("Stopping UavTalk")
               self.uavTalk.stop()
        except AttributeError:
            self.eprint("UAVTalk wasn't running!");
            
    def __takeControl(self):
        self.eprint("Taking control of self.ManualControl")
        if self.bHaveControl == False:
            self.objMan.ManualControlCommand.metadata.access = UAVMetaDataObject.Access.READONLY
            self.objMan.ManualControlCommand.metadata.updated()
            self.objMan.ManualControlCommand.Connected.value = True
            self.objMan.ManualControlCommand.updated()
            self.bHaveControl = True
    
    def __disarmBoard(self):
        self.eprint("Disarming board using Yaw left")
        # FIXME: Seems there is a issue with ArmedField.DISARMED, 0 equals to the DISARMED state
        while (self.objMan.FlightStatus.Armed.value != 0):
            self.objMan.ManualControlCommand.Yaw.value = -1
            self.objMan.ManualControlCommand.updated()
            time.sleep(0.3)

        self.__armed=False
        self.objMan.ManualControlCommand.Yaw.value = 0
        self.objMan.ManualControlCommand.updated()
        time.sleep(1)

    def __armBoard(self):
        self.eprint("Arming board using Yaw right")
        # FIXME: Seems there is a issue with ArmedField.ARMED, 2 equals to the ARMED state
        while (self.objMan.FlightStatus.Armed.value != 2):
            self.objMan.ManualControlCommand.Yaw.value = 1
            self.objMan.ManualControlCommand.updated()
            self.objMan.ManualControlCommand.Throttle.value = -1
            self.objMan.ManualControlCommand.updated()
            time.sleep(1)
        
        if (self.objMan.FlightStatus.Armed.value == 2):
            self.eprint("Board is armed !")
            self.__armed=True
            self.objMan.ManualControlCommand.Yaw.value = 0
            self.objMan.ManualControlCommand.updated()        

    def __freeControl(self):
        self.eprint("Back to self.ManualControl, controlled by RC radio")
        self.objMan.ManualControlCommand.metadata.access = UAVMetaDataObject.Access.READWRITE
        self.objMan.ManualControlCommand.metadata.updated()    
        self.objMan.ManualControlCommand.Connected.value = False
        self.objMan.ManualControlCommand.updated()
        
    def distanz(self):
        self.eprint("Get Distance")
        # setze Trigger auf HIGH
        GPIO.output(self.GPIO_TRIGGER, True)
        
        # setze Trigger nach 0.01ms aus LOW
        time.sleep(0.01)
        GPIO.output(self.GPIO_TRIGGER, False)
        
        StartZeit = time.time()
        StopZeit = time.time()
        self.eprint("echo == 0")
        # speichere Startzeit
        while GPIO.input(self.GPIO_ECHO) == 0:
            StartZeit = time.time()
        self.eprint("echo == 1")
        # speichere Ankunftszeit
        while GPIO.input(self.GPIO_ECHO) == 1:
            StopZeit = time.time()
        self.eprint("fin")
        # Zeit Differenz zwischen Start und Ankunft
        TimeElapsed = StopZeit - StartZeit
        # mit der Schallgeschwindigkeit (34300 cm/s) multiplizieren
        # und durch 2 teilen, da hin und zurueck
        distanz = (TimeElapsed * 34300) / 2
        eprint("Finished") 
        return distanz

    def initUltrasonic(self):
        self.uPort = none
        port = "/dev/ttyUSB0"
        print "Opening Port \"%s\"" % port
        if port[:3].upper() == "COM":
                _port = int(port[3:]) - 1
        else:
                _port = port
    
        self.uPort = serial.Serial(_port, 115200, timeout=.5)
        if not self.uPort.isOpen():
            raise IOError("Failed to open serial port")
        return serPort

    def getUSensor(self,index):
        buffer = ""
        if not self.uPort.isOpen():
            self.initUltrasonic
        actual = self.uPort.read()
        if(actual == "\n"):
            splitted=buffer.split(" ")
            return splitted[index]
        else:
            buffer+=actual
    
    def getBottumUSensor(self):
        value = self.getUSensor(self,0)
        return value

    def setControlValues(self, throttle, pitch, roll, yaw):
        self.eprint(str(throttle) + " " + str(pitch) + " " + str(roll) + " " + str(yaw))
        self.eprint("In ControlFunction!")
        if throttle > 1.0:
            self.eprint("throttle return" + str(throttle))
            return -1
        if pitch > 1.0:
            self.eprint("pitch return")
            return -1
        if yaw > 1.0:
            self.eprint("yaw return")
            return -1
        if roll > 1.0:
            self.eprint("roll return")
            return -1
        if self.bBoardInitialized == False:
            self.eprint("Board not armed - arming Board...")
            self.__takeControl()
            self.__armBoard()
            self.bBoardInitialized = True
        
        self.__takeControl()
        self.eprint("taking over control")            
        self.objMan.ManualControlCommand.Thrust.value = throttle
        self.objMan.ManualControlCommand.Pitch.value = pitch
        self.objMan.ManualControlCommand.Roll.value = yaw
        self.objMan.ManualControlCommand.Yaw.value = roll
        self.objMan.ManualControlCommand.updated()
        
        # just for debugging
        #time.sleep(1)
        #self.objMan.ManualControlCommand.Thrust.value = 0
        #self.objMan.ManualControlCommand.Pitch.value = 0
        #self.objMan.ManualControlCommand.Roll.value = 0
        #self.objMan.ManualControlCommand.Yaw.value = 0
        #self.objMan.ManualControlCommand.updated()
        #self.__freeControl()
    
    def hoverTest(self, height, minThrottle, maxThrottle, duration):
        self.eprint("Beginne AutoHover: Hoehe: " + str(height) + "cm minimal Thrust: " + minThrottle + " maximum Thrust: " + maxThrottle + " hover Zeit: " + duration + " Sekunden.")
        timer = 10
        self.eprint("Start in: " + str(timer))
        while(timer > 0):
            self.eprint(str(timer))
            timer = timer - 1
        self.eprint("Starte AutoHover")
        timer = 0
        while(timer < duration):
            position = self.getBottomUSensor()
            if position > 250:
                self.eprint("Hoehe ist groesser als 2.5m... starte neue Messung")
                position = self.getBottomUSensor()
                if position > 250:
                    self.eprint("Hoehe ist immer noch groesser als 2.5m... starte neue Messung")
                    position = self.getBottomUSensor()
                    if position > 250:
                        self.eprint("Hoehe ist immer noch groesser als 2.5m... starte Abschaltung der Motoren... MAYDAY MAYDAY MAYDAY... ")
                        self.setControlValues(0, 0, 0, 0)
            self.eprint("Gemessene Hoehe: " + str(position) + "cm. Verbleibende hover Zeit: " + str(duration - timer))
            factor = height - position * 0.05
            if factor < minThrottle:
                factor = minThrottle
                
            if factor > maxThrottle:
                factor =  maxThrottle
            self.eprint("Neu ermittelter Thrustfactor: " + str(factor) + " ... starte Anpassung")
            self.setControlValues(factor, 0, 0, 0)
            self.eprint("Neue Messung in 0,1 Sekunden...")
            time.sleep(0.1)
            timer = timer + 0.1

        self.eprint("Ende des Hover Vorgangs. Leite automatische Landung ein...")
        self.autoLand()
            
    def autoLand(self):
        heigth = 0
        position = self.getBottomUSensor()
        if position > 250:
                self.eprint("Hoehe ist groesser als 2.5m... starte neue Messung")
                position = self.getBottomUSensor()
                if position > 250:
                    self.eprint("Hoehe ist immer noch groesser als 2.5m... starte neue Messung")
                    position = self.getBottomUSensor()
                    if position > 250:
                        self.eprint("Hoehe ist immer noch groesser als 2.5m... starte Abschaltung der Motoren... MAYDAY MAYDAY MAYDAY... ")
                        self.setControlValues(0, 0, 0, 0)
        while(position > 10):
            position = self.getBottomUSensor
            self.eprint("Gemessene Hoehe: " + str(position) + "cm. Verbleibende Hoehe: " + str(position - height))
            factor = height - position
            factor = factor * 0.05
                
            if factor < minThrottle:
                factor = minThrottle
            if factor > maxThrottle:
                factor =  maxThrottle
            self.eprint("Neu ermittelter Thrustfactor: " + str(factor) + " ... starte Anpassung")
            self.setControlValues(factor, 0, 0, 0)
            self.eprint("Neue Messung in 0,1 Sekunden...")
            time.sleep(0.1)
            timer = timer + 0.1
        
        self.eprint("Landehoehe erreicht, schalte Motoren ab!")
        self.setControlValues(0, 0, 0, 0)
    
    def driveInput(self):
        self.__takecontrol()
    
        self.__armBoard()
    
        self.eprint("Applying Throttle")
    
        # self.objMan.ManualControlCommand.Throttle.value = 0.01 # very small value for safety
        # Assuming board do not control a helicopter, Thrust value will be equal to Throttle value.
        # Because a 'high' value can be read from latest real RC input value, 
        # initial value is set now to zero for safety reasons.
        self.objMan.ManualControlCommand.Thrust.value = 0.01
        # self.objMan.ManualControlCommand.Throttle.value = self.objMan.ManualControlCommand.Thrust.value
        self.objMan.ManualControlCommand.updated()
        time.sleep(0.3)
    
        count = 60
        self.eprint("Moving Pitch input")
        while (count > 0):
            count-=1
            if self.objMan.ManualControlCommand.Pitch.value < 1:
                 self.objMan.ManualControlCommand.Pitch.value += 0.05
                 self.objMan.ManualControlCommand.updated()
                 time.sleep(0.1)
            if self.objMan.ManualControlCommand.Pitch.value > 1:
                self.objMan.ManualControlCommand.Pitch.value = 0
                self.objMan.ManualControlCommand.updated()
                time.sleep(0.1)
    
        self.objMan.ManualControlCommand.Pitch.value = 0
        self.objMan.ManualControlCommand.updated()
        time.sleep(0.5)
    
        count = 60
        self.eprint("Moving Roll input")
        while (count > 0):
            count-=1
            if self.objMan.ManualControlCommand.Roll.value < 1:
                 self.objMan.ManualControlCommand.Roll.value += 0.05
                 self.objMan.ManualControlCommand.updated()
                 time.sleep(0.1)
    
            if self.objMan.ManualControlCommand.Roll.value > 1:
                self.objMan.ManualControlCommand.Roll.value = 0
                self.objMan.ManualControlCommand.updated()
                time.sleep(0.1)
    
        self.objMan.ManualControlCommand.Roll.value = 0
        self.objMan.ManualControlCommand.updated()
        time.sleep(0.5)
    
        self.eprint("Setting Throttle to minimum")
        self.objMan.ManualControlCommand.Throttle.value = -1
        self.objMan.ManualControlCommand.updated()
        time.sleep(1)
    
        self.__disarmBoard()
    
        self.__freeControl()
        
        
    def stopDrone(self):
        self.terminate();
        self.stop();
        self.eprint("Stoped Drone")
        
        return True
        
if __name__ == "__main__":
    try:
        uavTalk = UAVTalkDemo(None)
        uavTalk.setup("/dev/ttyS0")
        print('setup finished')
    except KeyboardInterrupt:
        uavTalk.stop()
        raise
    else:
        print threading.enumerate()
        
    #stop all:
    uavTalk.stop()