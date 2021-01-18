# BlueBlindsPlugin
#
# Author: Mario Peters
#
"""
<plugin key="BlueBlindsPlugin" name="BlueBlindsPlugin" author="Mario Peters" version="1.0.0" wikilink="https://github.com/mario-peters/BlueBlindsPlugin/wiki" externallink="https://github.com/mario-peters/BlueBlindsPlugin">
    <description>
        <h2>BlueBlindsPlugin</h2><br/>
        Plugin for controlling bluetooth blinds.
        <h3>Configuration</h3>
        <ul style="list-style-type:square">
            <li>MAC Address is the MAC Address of the bluetooth blind.</li>
        </ul>
        <br/><br/>
    </description>
    <params>
        <param field="Address" label="MAC Address" width="200px" required="true"/>
        <param field="Mode1" label="Bluetooth device" width="100px">
            <options>
                <option label="0" value="0" default="true"/>
                <option label="1" value="1"/>
                <option label="2" value="2"/>
            </options>
        </param>
        <param field="Mode2" label="Light sensor" width="100px">
            <options>
                <option label="True" value="True"/>
                <option label="False" value="False" default="true"/>
            </options>
        </param>
    </params>
</plugin>
"""
import Domoticz
from bluepy import btle

class BasePlugin:

    # AM43 Notification Identifiers
    # Msg format: 9a <id> <len> <data * len> <xor csum>
    IdMove = 0x0d  #not used in code yet
    IdStop = 0x0a
    IdPosition = 0xa7
    IdPosition2 = 0xa8  #not used in code yet
    IdPosition3 = 0xa9  #not used in code yet
 
    def __init__(self):
        return

    def onStart(self):
        Domoticz.Log("onStart called")
        Domoticz.Heartbeat(30)
        Domoticz.Log("Address: "+Parameters["Address"])
        if len(Devices) == 0:
            Domoticz.Device("Blinds", Unit=1, Used=1, Type=244, Subtype=73, Switchtype=13).Create()
            Domoticz.Device("Position", Unit=2, Used=1, TypeName="Percentage").Create()
            if Parameters["Mode2"] == "True":
                Domoticz.Device("Light", Unit=3, Used=1, TypeName="Percentage").Create()

    def onStop(self):
        Domoticz.Log("onStop called")
        
    def onConnect(self, Connection, Status, Description):
        Domoticz.Log("onConnect called")

    def onMessage(self, Connection, Data):
        Domoticz.Log("onMessage called")

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Log("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))
        try:
            #dev = btle.Peripheral("02:14:a1:87:28:f5", iface=0)
            dev = btle.Peripheral(Parameters["Address"], iface=int(Parameters["Mode1"]))
            
            bSuccess = False
            BlindsControlService = dev.getServiceByUUID("fe50")
            #Domoticz.Log(str(BlindsControlService))
            BlindsControlServiceCharacteristic = BlindsControlService.getCharacteristics("fe51")[0]
            #Domoticz.Log(str(BlindsControlServiceCharacteristic))
            if str(Command) == "On":
                #bSuccess = write_message(BlindsControlServiceCharacteristic, dev, 0x0d, [100], False)
                bSuccess = write_message(BlindsControlServiceCharacteristic, dev, self.IdMove, [0], False)
            elif str(Command) == "Off":
                #bSuccess = write_message(BlindsControlServiceCharacteristic, dev, 0x0d, [0], False)
                bSuccess = write_message(BlindsControlServiceCharacteristic, dev, self.IdMove, [100], False)
            elif str(Command) == "Set Level":
                #bSuccess = write_message(BlindsControlServiceCharacteristic, dev, 0x0d, [Level], False)
                bSuccess = write_message(BlindsControlServiceCharacteristic, dev, self.IdMove, [Level], False)
            dev.disconnect()
 
            if (bSuccess):
                theLevel = Level
                if str(Command) == "On":
                    theLevel = 100
                elif str(Command) == "Off":
                    theLevel = 0
                Devices[Unit].Update(nValue=theLevel,sValue=str(theLevel))
                Devices[2].Update(nValue=theLevel,sValue=str(theLevel))
        except btle.BTLEException as err:
            Domoticz.Log(str(err))

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Log("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Log("onDisconnect called")

    def onHeartbeat(self):
        Domoticz.Log("onHeartbeat called")
        try:
            dev = btle.Peripheral(Parameters["Address"], iface=int(Parameters["Mode1"]))
            BlindsControlService = dev.getServiceByUUID("fe50")
            if (BlindsControlService):
                BlindsControlServiceCharacteristic = BlindsControlService.getCharacteristics("fe51")[0]
                if (BlindsControlServiceCharacteristic):
                    if BlindsControlServiceCharacteristic.supportsRead():
                        dev.setDelegate(BlindDelegate())
                        global IdBattery
                        write_message(BlindsControlServiceCharacteristic, dev, IdBattery, [0x01], True)
                        global BatteryPct
                        Domoticz.Log("Battery: "+str(BatteryPct))
                        Devices[1].Update(nValue=Devices[1].nValue,sValue=Devices[1].sValue,BatteryLevel=BatteryPct)
                        if Parameters["Mode2"] == "True":
                            write_message(BlindsControlServiceCharacteristic, dev, IdLight, [0x01], True)
                            global LightPct
                            Domoticz.Log("Light: "+str(LightPct))
                            Devices[3].Update(nValue=int(LightPct),sValue=str(LightPct))
            dev.disconnect()
        except btlee.BTLEException as err:
            Domoticz.Log(str(err))

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

    # Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return

def write_message(characteristic, dev, id, data, bWaitForNotifications):
    ret = False

    # Construct message
    msg = bytearray({0x9a})
    msg += bytearray({id})
    msg += bytearray({len(data)})
    msg += bytearray(data)

    # Calculate checksum (xor)
    csum = 0
    for x in msg:
        csum = csum ^ x
    msg += bytearray({csum})
    
    #print("".join("{:02x} ".format(x) for x in msg))
    
    if (characteristic):
        result = characteristic.write(msg)
        Domoticz.Log(str(result))
        if (result["rsp"][0] == "wr"):
            ret = True
            if (bWaitForNotifications):
                if (dev.waitForNotifications(10)):
                    #print(datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S") + " -->  BTLE Notification recieved", flush=True)
                    pass
    return ret

BatteryPct = None
LightPct = None

IdBattery = 0xa2
IdLight = 0xaa

class BlindDelegate(btle.DefaultDelegate):
    def __init__(self):
        btle.DefaultDelegate.__init__(self)
    def handleNotification(self, cHandle, data):
        print(data)
        #if (data[1] == IdBattery):
        if (data[1] == 0xa2):
            global BatteryPct
            BatteryPct = data[7]
        #elif (data[1] == IdPosition):
        elif (data[1] == 0xa7):
            global PositionPct
            PositionPct = data[5]
        #elif (data[1] == IdLight):
        elif (data[1] == 0xaa):
            global LightPct
            LightPct = data[4] * 12.5
        else:
            print("Unknown identifier notification recieved: " + str(data[1:2]))
