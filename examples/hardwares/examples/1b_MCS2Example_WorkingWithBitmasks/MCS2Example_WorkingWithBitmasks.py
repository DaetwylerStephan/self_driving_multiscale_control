#!/usr/bin/python3
import sys
import smaract.ctl as ctl

# SmarAct MCS2 programming example: Working with bitmasks
#
# The technique of masking bits in a options parameter plays a
# major role when working with the MCS2 API.
#
# Several properties are used to define a specific behaviour of a function.
# In general, properties which specify their value as bitfield of independent flags,
# controlling different features of a function, are named "Options". (Like the Referencing Options).
# (The Channel State property returns the state as bitfield too)
# Bit masking should be used to define option bitfields of these properties.
# If you are not familiar with this techniques, see also available information from the internet
# to get some more explanation, e.g. https://en.wikipedia.org/wiki/Mask_(computing).
#
# In contrast, properties which set a specific value out of a defined set
# of valid values are named "Mode".
# (Like the Sensor Power Mode property).

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

print("************************************************************")
print("* SmarAct MCS2 Programming Example (Working with bitmasks) *")
print("************************************************************")

locator = "usb:ix:0"
d_handle = None
channel = 0

# All errors of SmarActCTL function calls are handled by the python build-in exception handling using the try/except statements.
try:
    assert_lib_compatibility()

    d_handle = ctl.Open(locator)
    print("MCS2 opened {}.".format(locator))
    # ----------------------------------------------------------------------------------------------------------------
    # Setting explicit modes:
    # Properties which define a specific mode may be set directly to their value.
    # Here we set the sensor power mode to "ctl.SensorPowerMode.ENABLED".
    # For this the enumeration types of the ctl module may be used instead of basic integers.
    ctl.SetProperty_i32(d_handle, channel, ctl.Property.SENSOR_POWER_MODE, ctl.SensorPowerMode.ENABLED)
    # ----------------------------------------------------------------------------------------------------------------
    # Reading a specific channel state flag:
    # -> Masking bits to "0"
    # Use bitwise AND to mask the channel state
    # to get only the information which is of interst. All other flags are set to zero and thus "ignored" for the check.

    # According to the rules:
    # Y AND 0 = 0
    # Y AND 1 = Y
    # one or more flags may be given to define the mask.
    # Here we only need the "sensorPresent" information, which is in bit 5 of the channel state.
    ch_state = ctl.GetProperty_i32(d_handle, channel, ctl.Property.CHANNEL_STATE)
    sensor_present = (ch_state & ctl.ChannelState.SENSOR_PRESENT) != 0
    if sensor_present:
        print("MCS2 channel {} has a sensor.".format(channel))
    # ----------------------------------------------------------------------------------------------------------------
    # Setting specific options flags:
    # -> Masking bits to "1"
    # Use bitwise OR to build the value of an options property.

    # According to the rules:
    # Y OR 1 = 1
    # Y OR 0 = Y
    # we combine the "startDirection" (Bit 0) and the "autoZero" (Bit 2) flags to define the referencing
    # behaviour.
    ref_options = ctl.ReferencingOption.START_DIR | ctl.ReferencingOption.AUTO_ZERO
    ctl.SetProperty_i32(d_handle, channel, ctl.Property.REFERENCING_OPTIONS, ref_options)
    # ----------------------------------------------------------------------------------------------------------------
    # Clear a specific flag:
    # -> Read -> Modify -> Write

    # In case we only want to clear a specific flag without explicitly modifying other ones,
    # we must read the value, modify the interesting flag (using bitmasking) and write back the value of the property.

    # Just to show this, we disable the "autoZero" option of the (previously set) referencing options.
    # To mask the bit to zero we must use the inverted value of the "AutoZero" flag. This clears the bit 2 but keeps
    # all other flags at their previous value.
    # Here we use the "~" operator to invert the value.
    # 0x00000004 inverted -> 0xFFFFFFFB
    ref_options = ctl.GetProperty_i32(d_handle, channel, ctl.Property.REFERENCING_OPTIONS)
    ref_options = ref_options & (~ctl.ReferencingOption.AUTO_ZERO)
    ctl.SetProperty_i32(d_handle, channel, ctl.Property.REFERENCING_OPTIONS, ref_options)
    # ----------------------------------------------------------------------------------------------------------------
    # Set a specific flag:
    # -> Read -> Modify -> Write

    # If we only want to set a specific flag without modifying other ones, we must read the value, modify the interesting
    # flag (using bitmasking) and write back the value of the property.

    # To show this, we again enable the "autoZero" referencing option.

    # To mask the bit to one we must OR bit 2 to the previously read value. This forces the "AutoZero" flag to one and
    # keeps all other flags at their previous value.
    ref_options = ctl.GetProperty_i32(d_handle, channel, ctl.Property.REFERENCING_OPTIONS)
    ref_options = ref_options | ctl.ReferencingOption.AUTO_ZERO
    ctl.SetProperty_i32(d_handle, channel, ctl.Property.REFERENCING_OPTIONS, ref_options)
    # ----------------------------------------------------------------------------------------------------------------
except ctl.Error as e:
    # Catching the "ctl.Error" exceptions may be used to handle errors of SmarActCTL function calls.
    # The "e.func" element holds the name of the function that caused the error and
    # the "e.code" element holds the error code.
    # Passing an error code to "GetResultInfo" returns a human readable string specifying the error.
    print("MCS2 {}: {}, error: {} (0x{:04X}) in line: {}."
          .format(e.func, ctl.GetResultInfo(e.code), ctl.ErrorCode(e.code).name, e.code, (sys.exc_info()[-1].tb_lineno)))

except Exception as ex:
    print("Unexpected error: {}, {} in line: {}".format(ex, type(ex), (sys.exc_info()[-1].tb_lineno)))
    raise

finally:
    # Before closing the program the connection to the device must be closed by calling "Close".
    # For this we can use the "finally" statement of the exception handling, which is executed in any case.
    if d_handle != None:
        ctl.Close(d_handle)
    print("MCS2 close.")
    print("*******************************************************")
    print("Done. Press return to exit.")
    input()
