#!/usr/bin/python3
import sys
import smaract.ctl as ctl

# SmarAct MCS2 programming example: GetProperty/SetProperty
#
# This programming example shows you how to connect to a
# SmarAct MCS2 device and how to use the blocking and non-blocking
# GetProperty and SetProperty functions to read and write
# device properties.
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
print("*  SmarAct MCS2 Programming Example (Get/Set-Property)*")
print("*******************************************************")

# Read the version of the library
# Note: this is the only function that does not require the library to be initialized.
version = ctl.GetFullVersionString()
print("SmarActCTL library version: '{}'.".format(version))
assert_lib_compatibility()

# MCS2 devices are identified with locator strings, similar to URLs used to locate web pages.
# Typical locators are:
# usb:sn:<serial>       - where <serial> is the device serial which is printed on the housing of the device.
#                        Example: usb:sn:MCS2-00000412
# usb:ix:<n>            - where the number <n> selects the nth device in the list of all currently attached
#                        devices with a USB interface. Example: usb:ix:0.
# network:sn:<serial>   - where <serial> is the device serial which is printed on the housing of the device.
#                        Example: network:sn:MCS2-00000412
# network:192.168.1.200 - where <ip> is an IPv4 address which consists of four integer numbers between 0 and 255
#                        separated by a dot. Example: network:192.168.1.200
# It is possible to list all available devices using the "FindDevices" function.
# This is shown in the further examples. Here we simply use a fixed locator string.
locator = "usb:ix:0"

# Note that there is no explicit communication mode (like synchronous or asynchronous)
# the user must decide upon, as it was in the previous controller systems.
# The application may decide on a per-call basis which method to use,
# thus being very flexible depending on the applications context.

# Before being able to communicate with a device it must be initialized with a call to "Open".
# This function connects to the device specified in the locator parameter and returns a handle to the
# device, if the call was successful. The returned device handle must be saved within the application
# and passed as a parameter to the other API functions. Once the connection is established,
# all the other functions may be used to interact with the connected device.
# Note: the additional configuration parameter is unused for now.
# The "Open" function returns the handle which must be passed to all functions to address the device.
d_handle = None

# All errors of SmarActCTL function calls are handled by the python build-in exception handling using the try/except statements.
try:
    d_handle = ctl.Open(locator)
    print("MCS2 opened {}.".format(locator))

    # Modifying or retrieving property values takes a major role in controlling a device by software.
    # Therefore, the API offers a variety of functions to get and set property values in order to meet all
    # requirements an application might have.

    # Basically there are GetProperty and SetProperty functions for the datatypes "string", "i32" (signed 32bit integer)
    # and "i64" (signed 64bit integer). The "i32" and "i64" versions may be used to process a single value
    # as well as an array of values.
    # Depending on the data type of the specific property, the corresponding variant of the the function must be used.
    # See the MCS2 Programmers Guide for a list of properties and their data types.
    # The passed "idx" parameter specifies the addressed module or channel depending on the specific property.
    # For system properties this parameter is unused and must be set to zero.
    # The "property key" defines the actual property. The predefined keys from the ctl.Property enum can be used.
    # The following code shows how to read several properties with different datatypes.

    # The easiest method to get a property value is the synchronous (blocking) read
    # consisting of only one simple function call.

    # First we read the device serial number which is a string property using "GetProperty_s".
    # Note that for string properties the ioArraySize must be explicitly passed as argument
    # (ctl.STRING_MAX_LENGTH+1) to specify the buffer size for the returned value.
    device_sn = ctl.GetProperty_s(d_handle, 0, ctl.Property.DEVICE_SERIAL_NUMBER)
    print("MCS2 device serial number: {}".format(device_sn))

    # Reading the number of channels of the system using "GetProperty_i32".
    # Note that the "idx" parameter is unused for this property and thus must be set to zero.
    no_of_channels = ctl.GetProperty_i32(d_handle, 0, ctl.Property.NUMBER_OF_CHANNELS)
    print("MCS2 number of channels: {}.".format(no_of_channels))

    # Now we read the state for all available channels.
    # The passed "idx" parameter (the channel index in this case) is zero-based.
    for channel in range(no_of_channels):
        state = ctl.GetProperty_i32(d_handle, channel, ctl.Property.CHANNEL_STATE)
        # The returned channel state holds a bit field of several state flags.
        # See the MCS2 Programmers Guide for the meaning of all state flags.
        # We pick the "sensorPresent" flag to check if there is a positioner connected
        # which has an integrated sensor.
        # Note that in contrast to previous controller systems the controller supports
        # hotplugging of the sensor module and the actuators.
        if state & ctl.ChannelState.SENSOR_PRESENT:
            print("MCS2 channel {} has a sensor.".format(channel))
        else:
            print("MCS2 channel {} has no sensor.".format(channel))

    # For the following steps we need a positioner connected to channel 0.
    channel = 0

    # First we want to know if the configured positioner type is a linear or a rotatory type.
    # For this purpose we can read the base unit property.
    base_unit = ctl.GetProperty_i32(d_handle, channel, ctl.Property.POS_BASE_UNIT)

    # Next we read the current position of channel 0. Position values have the data type int64,
    # thus we need to use "getProperty_i64".
    # Note that there is no distinction between linear and rotatory positioners regarding the functions which
    # need to be used (getPosition / getAngle) and there is no additional "revolutions" parameter for rotatory positioners
    # as it was in the previous controller systems.
    # Depending on the preceding read base unit, the position is in pico meter [pm] for linear positioners
    # or nano degree [ndeg] for rotatory positioners.
    # Note: it is also possible to read the base resolution of the unit using the property key "POS_BASE_RESOLUTION".
    # To keep things simple this is not shown in this example.
    position = ctl.GetProperty_i64(d_handle, channel, ctl.Property.POSITION)
    print("MCS2 position of channel {}: {}".format(channel, position), end='')
    print("pm.") if base_unit == ctl.BaseUnit.METER else print("ndeg.")

    # To show the use of the setProperty function, we set the position to 100 um respectively 100 milli degree.
    # This is the synchronous (blocking) method. The function call blocks until the property value was sent to
    # the controller and the reply was received.
    position = 100000000 # in pm | ndeg
    print("MCS2 set position of channel {} to {}".format(channel, position), end='')
    print("pm.") if base_unit == ctl.BaseUnit.METER else print("ndeg.")
    ctl.SetProperty_i64(d_handle, channel, ctl.Property.POSITION, position)

    # Now we want to read the the position again (and the channel state in addition).
    # This time we use the asynchronous (non-blocking) method.
    # This method requires two function calls for getting one property value.
    # One for requesting the property value and one for retrieving the answer.
    # The advantage of this method is that the application may request several property values in fast
    # succession and then perform other tasks before blocking on the reception of the results.

    # Received values can later be accessed via the obtained request ID and the corresponding ReadProperty functions.

    # The tHandle parameter is used for output buffering with the CreateOutputBuffer and FlushOutputBuffer functions.
    # (Not shown in this example.) By passing the transmit handle the request is associated with the output buffer
    # and therefore only sent when the buffer is flushed.
    # The transmit handle must be set to zero if output buffers are not used.

    # Issue requests for the two properties "position" and "channel state".
    r_id1 = ctl.RequestReadProperty(d_handle, channel, ctl.Property.POSITION, 0)
    # The function call returns immediately, allowing the application to issue another request or to perform other tasks.
    # We simply request a second property. (the channel state in this case)
    r_id2 = ctl.RequestReadProperty(d_handle, channel, ctl.Property.CHANNEL_STATE, 0)

    # ...process other tasks...

    # Receive the results
    # While the request-function is non-blocking the read-functions block until the desired data has arrived.
    # Note that we must use the correct "ReadProperty_ixx" function depending on the datatype of the requested property.
    # Otherwise a ctl.ErrorCode.INVALID_DATA_TYPE error is returned.
    position = ctl.ReadProperty_i64(d_handle, r_id1)
    state = ctl.ReadProperty_i32(d_handle, r_id2)

    # Print the results
    print("MCS2 current position of channel {}: {}".format(channel, position), end='')
    print("pm.") if base_unit == ctl.BaseUnit.METER else print("ndeg.")
    if (state & ctl.ChannelState.ACTIVELY_MOVING) == 0:
        print("MCS2 channel {} is stopped.".format(channel))

    # For the sake of completeness, finally we use the asynchronous (non-blocking) write function to
    # set the position to -0.1 mm respectively -100 degree.
    position = -100000000
    print("MCS2 set position of channel {} to {}".format(channel, position), end='')
    print("pm.") if base_unit == ctl.BaseUnit.METER else print("ndeg.")
    r_id = ctl.RequestWriteProperty_i64(d_handle, channel, ctl.Property.POSITION, position)
    # The function call returns immediately, without waiting for the reply from the controller.
    # ...process other tasks...

    # Wait for the result to arrive.
    ctl.WaitForWrite(d_handle, r_id)

    # Alternatively, the "call-and-forget" mechanism for asynchronous (non-blocking) write functions
    # may be used:
    # For property writes the result is only used to report errors. With the call-and-forget mechanism
    # the device does not generate a result for writes and the application can continue processing other
    # tasks immediately. Compared to asynchronous accesses, the application doesn’t need to keep
    # track of open requests and collect the results at some point. This mode should be used with care
    # so that written values are within the valid range.
    # The call-and-forget mechanism is activated by passing "False" to the optional pass_rID parameter of the
    # RequestWriteProperty_x functions.
    ctl.RequestWriteProperty_i64(d_handle, channel, ctl.Property.POSITION, position, pass_rID = False)
    # No result must be requested with the WaitForWrite function in this case.

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
