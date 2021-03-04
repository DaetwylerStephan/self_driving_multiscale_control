import usb.core
import usb.util
import sys

dev = usb.core.find(find_all=True)

# get next item from the generator
dev = usb.core.find(find_all=True)
# loop through devices, printing vendor and product ids in decimal and hex
for cfg in dev:
    sys.stdout.write('Decimal VendorID=' + str(cfg.idVendor) + ' & ProductID=' + str(cfg.idProduct)+ '\n')

    #sys.stdout.write('Hexadecimal VendorID=' + hex(cfg.idVendor) + ' & ProductID=' + hex(cfg.idProduct) + '\n\n')
    #print(str(cfg.port_number))
    #try:
    #    print(str(cfg.manufacturer))
    #except:
    #    print("oops")


#Decimal VendorID=1133 & ProductID=49948
#Hexadecimal VendorID=0x46d & ProductID=0xc31c

import usb.core
import usb.backend.libusb1

busses = usb.busses()
for bus in busses:
    devices = bus.devices
    for dev in devices:
        if dev != None:
            try:
                xdev = usb.core.find(idVendor=dev.idVendor, idProduct=dev.idProduct)
                if xdev._manufacturer is None:
                    xdev._manufacturer = usb.util.get_string(xdev, xdev.iManufacturer)
                if xdev._product is None:
                    xdev._product = usb.util.get_string(xdev, xdev.iProduct)
                stx = '%6d %6d: '+str(xdev._manufacturer).strip()+' = '+str(xdev._product).strip()
                print(stx % (dev.idVendor,dev.idProduct))
            except:
                pass




#laser has product id 59