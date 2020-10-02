#!/usr/bin/python3
import sys
import smaract.ctl as ctl

# SmarAct MCS2 programming example: MagneticDriver
#
# This programming example demonstrates how to control
# electromagnetic driven positioners with the MCS2
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

def waitWhile(channel, mask):
    """ Poll channel state until masked flags are set"""
    while (True):
        state = ctl.GetProperty_i32(d_handle, channel, ctl.Property.CHANNEL_STATE)
        if (state & mask) == 0: break

print("***************************************************************")
print("*  SmarAct MCS2 Programming Example (Electromagnetic Driver)  *")
print("***************************************************************")

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

    channel = 0
    # Verify that there is an electromagnetic driven positioner available.
    type = ctl.GetProperty_i32(d_handle, channel, ctl.Property.CHANNEL_TYPE) 
    state = ctl.GetProperty_i32(d_handle, channel, ctl.Property.CHANNEL_STATE)
    if type != ctl.ChannelModuleType.MAGNETIC_DRIVER:
        print("MCS2 channel {} is not an electromagnetic driver channel, abort.".format(channel))
        ctl.Close(d_handle)
        input()
        sys.exit(1)
    elif (state & ctl.ChannelState.SENSOR_PRESENT) == 0:
        print("MCS2 no positioner connected to channel {}, abort.".format(channel))
        ctl.Close(d_handle)
        input()
        sys.exit(1)

    # The amplifier of electromagnetic driver channels is disabled at startup and must be explicitly enabled
    # before being able to perform closed-loop movements. This also implicitly starts the phasing sequence of
    # the positioner if it is not already phased.
    # The AMPLIFIER_ENABLED channel state bit reflects the state of the amplifier.
    if (state & ctl.ChannelState.AMPLIFIER_ENABLED) == 0:
        print("*******************************************************")
        print("-> Press return to enable the amplifier (and start the phasing sequence).")
        input()
        ctl.SetProperty_i32(d_handle, channel, ctl.Property.AMPLIFIER_ENABLED, ctl.TRUE)

        if (state & ctl.ChannelState.IS_PHASED) == 0:
            print("MCS2 phasing...")
            # Note that no external force or displacement must be applied to the positioner while the sequence is running.
            # The phasing takes some time to complete. During this time the ACTIVELY_MOVING
            # channel state bit is set.
            # The channel generates a PHASING_FINISHED event once the sequence has finished.
            # In this example we poll the channel state to determine the end of the phasing sequence instead of
            # listening to events.
            waitWhile(channel, ctl.ChannelState.ACTIVELY_MOVING)
            # The IS_PHASED channel state flag should then be checked to verify that the
            # phasing sequence finished successfully.
            state = ctl.GetProperty_i32(d_handle, channel, ctl.Property.CHANNEL_STATE)
            if (state & ctl.ChannelState.IS_PHASED) == 0:
                print("MCS2 could not establish the phasing reference for channel {}, abort.".format(channel))
                ctl.Close(d_handle)
                input()
                sys.exit(1)
            else:
                print("MCS2 phase reference found.")

    # Perform referencing sequence if physical position is not known
    if (state & ctl.ChannelState.IS_REFERENCED) == 0:
        # Since the physical scale is not known yet no range limits can be used here.
        # Make sure to use a moderate move velocity for the referencing sequence.
        # Disable software range limits while referencing.
        ctl.SetProperty_i64(d_handle, channel, ctl.Property.RANGE_LIMIT_MIN, 0)
        ctl.SetProperty_i64(d_handle, channel, ctl.Property.RANGE_LIMIT_MAX, 0)
        ctl.SetProperty_i32(d_handle, channel, ctl.Property.REFERENCING_OPTIONS, 0)
        # The move velocity and acceleration properties also define the parameters for the referencing.
        ctl.SetProperty_i64(d_handle, channel, ctl.Property.MOVE_VELOCITY, 2000000000)
        ctl.SetProperty_i64(d_handle, channel, ctl.Property.MOVE_ACCELERATION, 100000000000)
        
        print("*******************************************************")
        print("-> Press return to start the referencing.")
        input()
        print("MCS2 referencing...")
        ctl.Reference(d_handle, channel)
        waitWhile(channel, ctl.ChannelState.REFERENCING)
        # Check if the referencing was successful.
        state = ctl.GetProperty_i32(d_handle, channel, ctl.Property.CHANNEL_STATE)
        # The MOVEMENT_FAILED indicates a failed referencing.
        if (state & ctl.ChannelState.MOVEMENT_FAILED) != 0:
            # The channel error property may then be read to determine the reason of the error.
            error = ctl.GetProperty_i32(d_handle, channel, ctl.Property.CHANNEL_ERROR)
            print("MCS2 referencing failed: {} (error: 0x{:04X}), abort.".format(ctl.GetResultInfo(error), error))
            ctl.Close(d_handle)
            input()
            sys.exit(1)
        else:
            print("MCS2 reference found.")
    # Note that electromagnetic driven positioners can reach very high velocities!
    # Moving into a physical endstop with high velocity can damage the positioner.
    # Therefore it is recommended to use the software range limits to define the active movement
    # range of the positioner. When commanding the positioner towards a limit the positioner is
    # decelerated to zero velocity in a way that it comes to a halt on the specified limit position.
    # Note: adjust this limits to match the movement range of your positioner!
    ctl.SetProperty_i64(d_handle, channel, ctl.Property.RANGE_LIMIT_MIN, -20000000000)
    ctl.SetProperty_i64(d_handle, channel, ctl.Property.RANGE_LIMIT_MAX, 20000000000)

    print("*******************************************************")
    print("-> Press return to start the movement.")
    input()
    # Set move mode to absolute movement.
    # Note: Open-loop movement is not available for electromagnetic driver channels.
    # (only the CL_ABSOLUTE and CL_RELATIVE move modes are valid)
    ctl.SetProperty_i32(d_handle, channel, ctl.Property.MOVE_MODE, ctl.MoveMode.CL_ABSOLUTE)
    # Set move velocity and acceleration.
    # Note that the velocity and acceleration control must be used for all movements. A velocity / acceleration
    # value of 0 (to disable the velocity / acceleration control) is invalid for magnetic driver channels.
    ctl.SetProperty_i64(d_handle, channel, ctl.Property.MOVE_VELOCITY, 10000000000)
    ctl.SetProperty_i64(d_handle, channel, ctl.Property.MOVE_ACCELERATION, 10000000000)

    positions = [2000000000,-2000000000,10000000000,-10000000000] # in pm
    for i in range(4):
        print("MCS2 move channel {} to position: {}...".format(channel, positions[i]))
        ctl.Move(d_handle, channel, positions[i])
        waitWhile(channel, ctl.ChannelState.ACTIVELY_MOVING)
        # Check if the movement was successful.
        state = ctl.GetProperty_i32(d_handle, channel, ctl.Property.CHANNEL_STATE)
        # The MOVEMENT_FAILED channel state flag indicates a failed movement.
        if (state & ctl.ChannelState.MOVEMENT_FAILED) != 0:
            # The channel error property may then be read to determine the reason of the error.
            error = ctl.GetProperty_i32(d_handle, channel, ctl.Property.CHANNEL_ERROR)
            print("MCS2 movement failed: {} (error: 0x{:04X}).".format(ctl.GetResultInfo(error), error))
            break
            # Alternatively, the following channel state flags may be tested to determine the reason
            # of a failed movement:
            # - END_STOP_REACHED
            # - RANGE_LIMIT_REACHED
            # - FOLLOWING_LIMIT_REACHED
            # - POSITIONER_OVERLOAD
            # - POSITIONER_FAULT
            # See the MCS2 Programmers Guide for more information on the specific channel state flags.

        # The electromagnetic driver monitors the output current of each channel to detect an overload condition
        # of the positioner. This prevents thermal overheating and potential damage of the positioners coils,
        # isolation and permanent magnets.
        # If an over load is detected the control-loop is disabled to protect the positioner.
        # WARNING
        # Electromagnetic driven positioners are not self-locking. Disabling the control-loop removes
        # any holding force from the positioner. Make sure not to damage any equipment
        # when the positioner unintentionally changes its position!

        # The present load level may be read in percent with the motor load property. This may be useful
        # to estimate the motor load while performing movements before the overload protection trips and
        # disables the control-loop. In case the motor load reaches a level close to 100 % the number of
        # movements per time, the movement acceleration and/or the mechanical load attached to the
        # positioner should be reduced.
        load = ctl.GetProperty_i32(d_handle, channel, ctl.Property.MOTOR_LOAD)
        print("MCS2 short-term motor over load: {} %".format(load))

    # Disable the amplifier again.
    ctl.SetProperty_i32(d_handle, channel, ctl.Property.AMPLIFIER_ENABLED, ctl.FALSE)

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
