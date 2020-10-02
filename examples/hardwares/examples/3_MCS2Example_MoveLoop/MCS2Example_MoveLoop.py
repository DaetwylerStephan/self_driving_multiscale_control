#!/usr/bin/python3
import sys
import smaract.ctl as ctl

# SmarAct MCS2 programming example: MoveLoop
#
# This programming example performs
# positioner movement in a loop and polls
# the channel state to determine the end
# of the movement.
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
print("*  SmarAct MCS2 Programming Example (MoveLoop)        *")
print("*******************************************************")

# Read the version of the library
# Note: this is the only function that does not require the library to be initialized.
version = ctl.GetFullVersionString()
print("SmarActCTL library version: '{}'.".format(version))
assert_lib_compatibility()

# Find available MCS2 devices
try:
    buffer = ctl.FindDevices("")
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

    # We assume that there is a linear positioner with integrated sensor connected to channel 0.
    channel = 0
    # Set move mode to relative movement.
    ctl.SetProperty_i32(d_handle, channel, ctl.Property.MOVE_MODE, ctl.MoveMode.CL_RELATIVE)
    # Set move velocity to 2 mm/s.
    ctl.SetProperty_i64(d_handle, channel, ctl.Property.MOVE_VELOCITY, 2000000000)
    # Set move acceleration to 20 mm/s2.
    ctl.SetProperty_i64(d_handle, channel, ctl.Property.MOVE_ACCELERATION, 20000000000)
    # Enable the amplifier.
    ctl.SetProperty_i32(d_handle, channel, ctl.Property.AMPLIFIER_ENABLED, ctl.TRUE)
    # Read the channel type to determine if additional configuration is required for this type of channel.
    type = ctl.GetProperty_i32(d_handle, channel, ctl.Property.CHANNEL_TYPE)

    # The following code performs one or two sequences of closed loop movement in a loop.
    # The channel state is polled to trigger the direction reverse.
    # Observe the different state flags used to determine the end of the movement.

    no_of_sequences = 2
    if type == ctl.ChannelModuleType.STICK_SLIP_PIEZO_DRIVER:
        # The hold time specifies how long the position is actively held after reaching the target.
        # This can be useful to guarantee that a position is held precisely including
        # compensation of drift effects, etc.
        # We set the hold time to 1000 ms to notice the effect of the hold time (in the second sequence).
        ctl.SetProperty_i32(d_handle, channel, ctl.Property.HOLD_TIME, 1000)

    elif type == ctl.ChannelModuleType.MAGNETIC_DRIVER:
        # Magnetic driven positioners are always in the holding state when stopped. Therefore
        # there is no hold time property for this type of channel and we dont run the second sequence.
        no_of_sequences = 1

    # FIRST SEQUENCE
    print("*******************************************************")
    print("First sequence:")
    print("Reverse direction instantly after reaching the target position")
    print("-> Press return to start the move loop.")
    input()

    position = 1000000000  # 1 mm
    for sequ in range(no_of_sequences):
        for i in range(4):
            # Command alternating positive and negative movement in a loop.
            ctl.Move(d_handle, channel, position)
            print("MCS2 move...")
            # Poll the channel state to wait for the movement to finish.
            while (True):
                if sequ == 0:
                    # The first sequence waits for the "ChannelState.ACTIVELY_MOVING" state flag to be read as zero
                    # and reverses the movement direction instantly.
                    # The "ChannelState.ACTIVELY_MOVING" flag remains set until the target position was reached.
                    # (or an endstop was detected)
                    mask = ctl.ChannelState.ACTIVELY_MOVING
                else:
                    # The second sequence additionally checks the "ChannelState.CLOSED_LOOP_ACTIVE" flag to wait
                    # for the hold time to elapse.
                    mask = (ctl.ChannelState.ACTIVELY_MOVING | ctl.ChannelState.CLOSED_LOOP_ACTIVE)
                # Check if the movement was successful.
                state = ctl.GetProperty_i32(d_handle, channel, ctl.Property.CHANNEL_STATE)
                # The ChannelState.MOVEMENT_FAILED channel state flag indicates a failed movement.
                if (state & ctl.ChannelState.MOVEMENT_FAILED) != 0:
                    # The channel error property may then be read to determine the reason of the error.
                    error = ctl.GetProperty_i32(d_handle, channel, ctl.Property.CHANNEL_ERROR)
                    print("MCS2 movement failed: {} (error: 0x{:04X}), abort.".format(ctl.GetResultInfo(error), error))
                    break
                    # Alternatively, the following channel state flags may be tested to determine the reason
                    # of a failed movement:
                    # - ChannelState.END_STOP_REACHED
                    # - ChannelState.RANGE_LIMIT_REACHED
                    # - ChannelState.FOLLOWING_LIMIT_REACHED
                    # See the MCS2 Programmers Guide for more information on the specific channel state flags.
                if (state & mask) == 0:
                    if i < 3:
                        print("MCS2 reverse direction [{}].".format(i+1))
                    else:
                        print("MCS2 move loop done.")
                    position = -position
                    break
        if no_of_sequences == 2 and sequ == 0:
            # SECOND SEQUENCE (optional)
            print("*******************************************************")
            print("Second sequence:")
            print("Reverse direction after reaching the target position")
            print("AND hold time elapsed")
            print("-> Press return to start the move loop.")
            input()

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
