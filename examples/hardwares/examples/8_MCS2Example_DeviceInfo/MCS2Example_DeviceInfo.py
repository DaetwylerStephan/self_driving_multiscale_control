#!/usr/bin/python3
import sys
import smaract.ctl as ctl

# SmarAct MCS2 programming example: Device-Info
#
# This programming example shows how to read device,
# module and channel properties to query various information
# about the device.
#
# For a full command reference see the MCS2 Programmers Guide.

def assert_lib_compatibility():
    """
    Checks that the major version numbers of the Python API and the
    loaded shared library are the same to avoid errors due to 
    incompatibilities.
    Raises a RuntimeError if the major version numbers are different.
    """
    vapi = ctl.api_version
    vlib = [int(i) for i in ctl.GetFullVersionString().split('.')]
    if vapi[0] != vlib[0]:
        raise RuntimeError("Incompatible SmarActCTL python api and library version.")

print("*******************************************************")
print("*  SmarAct MCS2 Programming Example (Device Info)     *")
print("*******************************************************")

# Read the version of the library
# Note: this is the only function that does not require the library to be initialized.
version = ctl.GetFullVersionString()
print("SmarActCTL library version: '{}'.".format(version))
assert_lib_compatibility()

# Find available MCS2 devices
try:
    buffer = ctl.FindDevices()
    if len(buffer) == 0:
        print("MCS2 no devices found.")
        sys.exit(1)
    locators = buffer.split("\n")
    for locator in locators:
        print("MCS2 available devices: {}".format(locator))
except:
    print("MCS2 failed to find devices. Exit.")
    input()
    sys.exit(1)

d_handle = None
try:
    # Open the first MCS2 device from the list
    d_handle = ctl.Open(locators[0])
    print("MCS2 opened {}.".format(locators[0]))

    # Note on properties:
    # Not all properties are applicable for all driver modules and their channels.
    # Refer to the Property Reference of the MCS2 Programmers Guide to determine if
    # a property is valid for a specific module. Reading or writing a property which
    # is not available returns a ctl.ErrorCode.INVALID_KEY error.
    # Read the "Interface Type".format("Module Type" or "Channel Type" properties to determine 
    # the type of the interface, module or channel.
    
    # Read device info

    # Note for device properties:
    # The controller is already addressed by the device handle. Therefore,
    # the index parameter is unused and must be set to zero.
    serial = ctl.GetProperty_s(d_handle, 0, ctl.Property.DEVICE_SERIAL_NUMBER)
    print("Device Serial Number: {}".format(serial))
    name = ctl.GetProperty_s(d_handle, 0, ctl.Property.DEVICE_NAME)
    print("Device Name: {}".format(name))
    type = ctl.GetProperty_i32(d_handle, 0, ctl.Property.INTERFACE_TYPE)
    if type == ctl.InterfaceType.USB:
        print("Interface Type: USB")
    elif type == ctl.InterfaceType.ETHERNET:
        print("Interface Type: Ethernet")
    state = ctl.GetProperty_i32(d_handle, 0, ctl.Property.DEVICE_STATE)
    print("Hand Control Module present: ", end='')
    if (state & ctl.DeviceState.HM_PRESENT) != 0:
        print("yes")
    else:
        print("no") 
    # Use bitwise AND to mask the channel/module state to get only the information
    # which is of interst. All other flags are set to zero and thus "ignored" for the check.
    no_of_bus_modules = ctl.GetProperty_i32(d_handle, 0, ctl.Property.NUMBER_OF_BUS_MODULES)
    print("Number of Bus Modules: {}".format(no_of_bus_modules))
    no_of_channels = ctl.GetProperty_i32(d_handle, 0, ctl.Property.NUMBER_OF_CHANNELS)
    print("Total Number of Channels: {}".format(no_of_channels))
    print("*******************************************************")
    # Read module info
    # The "moduleIndex" must be passed to all module properties. Note that it is zero-based.
    for i in range(no_of_bus_modules):
        mod_type = ctl.GetProperty_i32(d_handle, i, ctl.Property.MODULE_TYPE)
        print("Module {}".format(i), end='')
        if mod_type == ctl.ChannelModuleType.STICK_SLIP_PIEZO_DRIVER:
            print(" (Stick-Slip-Piezo-Driver):")
        elif mod_type == ctl.ChannelModuleType.MAGNETIC_DRIVER:
            print(" (Magnetic-Driver):")
        num = ctl.GetProperty_i32(d_handle, i, ctl.Property.NUMBER_OF_BUS_MODULE_CHANNELS)
        print("    Number of Bus Module Channels: {}".format(num))
        state = ctl.GetProperty_i32(d_handle, i, ctl.Property.MODULE_STATE)
        print("    Sensor Module present: ", end='')
        if (state & ctl.ModuleState.SM_PRESENT) != 0:
            print("yes")
        else:
            print("no")

    print("-------------------------------------------------------")
    # Read channel info
    # The "channelIndex" must be passed to all module properties. Note that it is zero-based.
    for i in range(no_of_channels):
        print("        Channel: {}".format(i))
        name = ctl.GetProperty_s(d_handle, i, ctl.Property.POSITIONER_TYPE_NAME)  
        pos_type = ctl.GetProperty_i32(d_handle, i, ctl.Property.POSITIONER_TYPE)
        print("        Positioner Type: {} ({})".format(name, pos_type))
        state = ctl.GetProperty_i32(d_handle, i, ctl.Property.CHANNEL_STATE)  
        print("        Amplifier enabled: ", end='')
        if (state & ctl.ChannelState.AMPLIFIER_ENABLED) != 0:
            print("yes")
        else:
            print("no")
        # Here we read the "Channel Type" property to determine which additional properties and flags are of interest.
        # E.g. the maxCLF property is only available for Stick-Slip-Driver channels and the "isPhased"
        # Channel State flag is only available for Magnetic-Driver channels.
        # Note that the "Module Type" and "Channel Type" properties share the same list of types.
        type = ctl.GetProperty_i32(d_handle, i, ctl.Property.CHANNEL_TYPE)
        if type == ctl.ChannelModuleType.STICK_SLIP_PIEZO_DRIVER:
            max_clf = ctl.GetProperty_i32(d_handle, i, ctl.Property.MAX_CL_FREQUENCY)
            print("        Max-CLF: {} Hz".format(max_clf))
        elif type == ctl.ChannelModuleType.MAGNETIC_DRIVER:
            print("        Channel is phased: ", end='')
            if (state & ctl.ChannelState.IS_PHASED) != 0:
                print("yes")
            else:
                print("no")
        print("-------------------------------------------------------")

except ctl.Error as e:
    # Passing an error code to "GetResultInfo" returns a human readable string
    # specifying the error.
    print("MCS2 {}: {}, error: {} (0x{:04X}) in line: {}."
          .format(e.func, ctl.GetResultInfo(e.code), ctl.ErrorCode(e.code).name, e.code, (sys.exc_info()[-1].tb_lineno)))

except Exception as ex:
    print("Unexpected error: {}, {} in line: {}".format(ex, type(ex), (sys.exc_info()[-1].tb_lineno)))
    raise

finally:
    # Before closing the program the connection to the device must be closed by calling "Close".
    if d_handle != None:
        ctl.Close(d_handle)
    print("MCS2 close.")
    print("*******************************************************")
    print("Done. Press return to exit.")
    input()
