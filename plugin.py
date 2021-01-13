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
    IdBattery = 0xa2
    IdLight = 0xaa
    IdPosition = 0xa7
    IdPosition2 = 0xa8  #not used in code yet
    IdPosition3 = 0xa9  #not used in code yet
 
    def __init__(self):
        return

    def onStart(self):
        Domoticz.Log("onStart called")
        Domoticz.Heartbeat(30)
        if len(Devices) == 0:
            Domoticz.Device("Blinds", Unit=1, Used=1, Type=244, Subtype=73, Switchtype=13).Create()

    def onStop(self):
        Domoticz.Log("onStop called")
        
    def onConnect(self, Connection, Status, Description):
        Domoticz.Log("onConnect called")

    def onMessage(self, Connection, Data):
        Domoticz.Log("onMessage called")

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Log("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))
        try:
            dev = btle.Peripheral(Parameters["Address"])

            bSuccess = False
            BlindsControlService = dev.getServiceByUUID("fe50")
            if (BlindsControlService):
                BlindsControlServiceCharacteristic = BlindsControlService.getCharacteristics("fe51")[0]
                if (BlindControlServiceCharacteristic):
                    if str(Command) == "On":
                        bSuccess = write_message(BlindsControlServiceCharacteristic, dev, IdMove, [0], False)
                    elif str(Command) == "Off":
                        bSuccess = write_message(BlindsControlServiceCharacteristic, dev, IdMove, [100], False)
                    elif str(Command) == "Set Level":
                        bSuccess = write_message(BlindsControlServiceCharacteristic, dev, IdMove, [Level], False)
                    elif str(Command) == "Stop":
                        bSuccess = write_message(BlindsControlServiceCharacteristic, dev, IdMove, [0xcc], False)

            if (bSuccess):
                Devices[Unit].Update(nValue=1,sValue=str(Level))
            dev.disconnect()
        except btle.BTLEDisconnectError as e:
            Domoticz.Log(str(e))

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Log("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Log("onDisconnect called")

    def onHeartbeat(self):
        Domoticz.Log("onHeartbeat called")

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
        if (result["rsp"][0] == "wr"):
            ret = True
            if (bWaitForNotifications):
                if (dev.waitForNotifications(10)):
                    #print(datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S") + " -->  BTLE Notification recieved", flush=True)
                    pass
    return ret
