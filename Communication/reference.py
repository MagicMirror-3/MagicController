#!/usr/bin/python3

"""Copyright (c) 2019, Douglas Otwell
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import time

import dbus

from advertisement import Advertisement
from service import Application, Service, Characteristic, Descriptor

GATT_CHRC_IFACE = "org.bluez.GattCharacteristic1"
NOTIFY_TIMEOUT = 5000


class ThermometerAdvertisement(Advertisement):
    def __init__(self, index):
        Advertisement.__init__(self, index, "peripheral")
        self.add_local_name("MagicMirror")
        self.include_tx_power = True


class HelloService(Service):
    HELLO_SVC_UUID = "00000001-710e-4a5b-8d75-3e5b444bc3cf"

    def __init__(self, index):
        Service.__init__(self, index, self.HELLO_SVC_UUID, True)
        self.add_characteristic(HelloCharacteristic(self))


class HelloCharacteristic(Characteristic):
    HELLO_CHARACTERISTIC_UUID = "00000002-710e-4a5b-8d75-3e5b444bc3cf"

    def __init__(self, service):

        Characteristic.__init__(
            self, self.HELLO_CHARACTERISTIC_UUID,
            ["read", "write", "notify"], service)
        self.add_descriptor(TempDescriptor(self))

    def WriteValue(self, value, options):
        """
        App sends value to characteristics

        """

        request = str(value[0])
        print("request", request)

        time.sleep(0.5)

        # send response
        value = []
        reply = 'OK'
        value.append(dbus.Byte(reply.encode()))
        print("Notify response: OK")
        self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": value}, [])

    def ReadValue(self, options):
        """
        App reads characteristic from Pi

        """

        value = []
        reply = 'OK'
        value.append(dbus.Byte(reply.encode()))
        print("Normal read: OK")

        return value

class TempDescriptor(Descriptor):
    TEMP_DESCRIPTOR_UUID = "2901"
    TEMP_DESCRIPTOR_VALUE = "CPU Temperature"

    def __init__(self, characteristic):
        Descriptor.__init__(
            self, self.TEMP_DESCRIPTOR_UUID,
            ["read"],
            characteristic)

    def ReadValue(self, options):
        value = []
        desc = self.TEMP_DESCRIPTOR_VALUE

        for c in desc:
            value.append(dbus.Byte(c.encode()))

        return value



app = Application()
app.add_service(HelloService(0))
app.register()

adv = ThermometerAdvertisement(0)
adv.register()

try:
    app.run()
except KeyboardInterrupt:
    app.quit()
