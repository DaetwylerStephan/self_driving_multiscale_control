#!/usr/bin/python3
import sys
import smaract.ctl as ctl

# SmarAct MCS2 programming example: Movement
#
# This programming example shows you how to
# find available MCS2 devices to connect to
# and how to perform different movement commands.
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

def printMenu():
    print("*******************************************************")
    print("WARNING: make sure the positioner can move freely\n \
            without damaging other equipment!")
    print("*******************************************************")
    print("Enter command and return:")
    print("[?] print this menu")
    print("[c] calibrate")
    print("[f] find reference")
    print("[+] perform movement in positive direction")
    print("[-] perform movement in negative direction")
    print("[s] stop")
    print("[p] get current position")
    print("[0] set move mode: closed loop absolute move")
    print("[1] set move mode: closed loop relative move")
    print("[2] set move mode: open loop scan absolute*")
    print("[3] set move mode: open loop scan relative*")
    print("[4] set move mode: open loop step*")
    print("[5] set control mode: standard mode*")
    print("[6] set control mode: quiet mode*")
    print("  * not available for Magnetic Driver channels")
    print("[q] quit")

# CALIBRATION
# The calibration sequence is used to increase the precision of the position calculation. This function
# should be called once for each channel if the mechanical setup changes.
# (e.g. a different positioner was connected to the channel, the positioner type was set to a different type)
# The calibration data will be saved to non-volatile memory, thus it is not necessary to perform the calibration sequence
# on each initialization.
# Note: the "ChannelState.IS_CALIBRATED" in the channel state can be used to determine
# if valid calibration data is stored for the specific channel.

# During the calibration sequence the positioner performs a movement of up to several mm, make sure to not start
# the calibration near a mechanical endstop in order to ensure proper operation.
# See the MCS2 Programmers Guide for more information on the calibration.
def calibrate(channel):
    print("MCS2 start calibration on channel: {}.".format(channel))
    # Set calibration options (start direction: forward)
    ctl.SetProperty_i32(d_handle, channel, ctl.Property.CALIBRATION_OPTIONS, 0)
    # Start calibration sequence
    ctl.Calibrate(d_handle, channel)
    # Note that the function call returns immediately, without waiting for the movement to complete.
    # The "ChannelState.CALIBRATING" flag in the channel state can be monitored to determine
    # the end of the calibration sequence.

# FIND REFERENCE
# Since the position sensors work on an incremental base, the referencing sequence is used to
# establish an absolute positioner reference for the positioner after system startup.
# Note: the "ChannelState.IS_REFERENCED" in the channel state can be used to to decide
# whether it is necessary to perform the referencing sequence.
def findReference(channel):
    print("MCS2 find reference on channel: {}.".format(channel))
    # Set find reference options.
    # The reference options specify the behavior of the find reference sequence.
    # The reference flags can be ORed to build the reference options.
    # By default (options = 0) the positioner returns to the position of the reference mark.
    # Note: In contrast to previous controller systems this is not mandatory.
    # The MCS2 controller is able to find the reference position "on-the-fly".
    # See the MCS2 Programmer Guide for a description of the different modes.
    ctl.SetProperty_i32(d_handle, channel, ctl.Property.REFERENCING_OPTIONS, 0)
    # Set velocity to 1mm/s
    ctl.SetProperty_i64(d_handle, channel, ctl.Property.MOVE_VELOCITY, 1000000000)
    # Set acceleration to 10mm/s2.
    ctl.SetProperty_i64(d_handle, channel, ctl.Property.MOVE_ACCELERATION, 10000000000)
    # Start referencing sequence
    ctl.Reference(d_handle, channel)
    # Note that the function call returns immediately, without waiting for the movement to complete.
    # The "ChannelState.REFERENCING" flag in the channel state can be monitored to determine
    # the end of the referencing sequence.

# MOVE
# The move command instructs a positioner to perform a movement.
# The given "move_value" parameter is interpreted according to the previously configured move mode.
# It can be a position value (in case of closed loop movement mode), a scan value (in case of scan move mode)
# or a number of steps (in case of step move mode).
def move(channel, move_mode, direction):
    # Set move mode depending properties for the next movement.
    if move_mode == ctl.MoveMode.CL_ABSOLUTE:
        # Set move velocity [in pm/s].
        ctl.SetProperty_i64(d_handle, channel, ctl.Property.MOVE_VELOCITY, 1000000000)
        # Set move acceleration [in pm/s2].
        ctl.SetProperty_i64(d_handle, channel, ctl.Property.MOVE_ACCELERATION, 1000000000)
        # Specify absolute position [in pm].
        move_value = 1000000000
        if direction:
            move_value = -2000000000
        print("MCS2 move channel {} to absolute position: {} pm.".format(channel, move_value))
    elif move_mode == ctl.MoveMode.CL_RELATIVE:
        # Set move velocity [in pm/s].
        ctl.SetProperty_i64(d_handle, channel, ctl.Property.MOVE_VELOCITY, 500000000)
        # Set move acceleration [in pm/s2].
        ctl.SetProperty_i64(d_handle, channel, ctl.Property.MOVE_ACCELERATION, 10000000000)
        # Specify relative position distance [in pm] and direction.
        move_value = 500000000
        if direction:
            move_value = -move_value
        print("MCS2 move channel {} relative: {} pm.".format(channel, move_value))
    elif move_mode == ctl.MoveMode.SCAN_ABSOLUTE:
        # Set scan velocity [in dac increments/s].
        # Valid range: 1 to 65535000000
        ctl.SetProperty_i64(d_handle, channel, ctl.Property.SCAN_VELOCITY, (65535*2))
        # Specify absolute scan target to which to scan to [in dac increments].
        # Valid range: 0 to 65535 corresponding to 0 to 100V piezo voltage
        move_value = 65535
        if direction:
            move_value = 0
        print("MCS2 scan channel {} absolute to: {}.".format(channel, move_value))
    elif move_mode == ctl.MoveMode.SCAN_RELATIVE:
        # Set scan velocity [in dac increments/s].
        ctl.SetProperty_i64(d_handle, channel, ctl.Property.SCAN_VELOCITY, 65535)
        # Specify relative scan target and direction to which to scan to [in dac increments].
        # Valid range: -65535 to 65535 corresponding to 0 to 100V piezo voltage
        # If the resulting absolute scan target exceeds the valid range the scan movement will stop at the boundary.
        move_value = 65535
        if direction:
            move_value = -move_value
        print("MCS2 scan channel {} relative: {}.".format(channel, move_value))
    elif move_mode == ctl.MoveMode.STEP:
        # Set step frequency [in Hz].
        # Valid range: 1 to 20000 Hz
        ctl.SetProperty_i32(d_handle, channel, ctl.Property.STEP_FREQUENCY, 1000)
        # Set maximum step amplitude [in dac increments].
        # valid range: 0 to 65535 corresponding to 0 to 100V piezo voltage
        # Lower amplitude values result in smaller step width.
        ctl.SetProperty_i32(d_handle, channel, ctl.Property.STEP_AMPLITUDE, 65535)
        # Specify the number of steps to perform and the direction.
        move_value = 500
        if direction:
            move_value = -move_value
        print("MCS2 open loop step move, channel {}, steps: {}.".format(channel, move_value))
    # Start actual movement.
    ctl.Move(d_handle, channel, move_value, 0)
    # Note that the function call returns immediately, without waiting for the movement to complete.
    # The "ChannelState.ACTIVELY_MOVING" (and "ChannelState.CLOSED_LOOP_ACTIVE") flag in the channel state
    # can be monitored to determine the end of the movement.

# STOP
# This command stops any ongoing movement. It also stops the hold position feature of a closed loop command.
# Note for closed loop movements with acceleration control enabled:
# The first "stop" command sent while moving triggers the positioner to come to a halt by decelerating to zero.
# A second "stop" command triggers a hard stop ("emergency stop").
def stop(channel):
    print("MCS2 stop channel: {}.".format(channel))
    ctl.Stop(d_handle, channel)

print("*******************************************************")
print("*  SmarAct MCS2 Programming Example (Movement)        *")
print("*******************************************************")

# Read the version of the library
# Note: this is the only function that does not require the library to be initialized.
version = ctl.GetFullVersionString()
print("SmarActCTL library version: '{}'.".format(version))
assert_lib_compatibility()

# MCS2 devices are identified with locator strings.
# The "FindDevices" function lists all available devices.
# The returned device list contains the locators of all found MCS2 devices separated by newlines.

# Find available MCS2 devices
try:
    buffer = ctl.FindDevices()
    if len(buffer) == 0:
        print("MCS2 no devices found.")
        exit(1)
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

    # There are three commands which trigger a movement of the positioner:
    # "Calibrate", "Reference" and "Move".
    # The command "Stop" aborts any ongoing movement.

    # Note that movement commands are always non-blocking. This means that the function call
    # returns immediately without waiting for the actual movement to complete. In addition,
    # they do not return an error in case the movement can not be processed for some reason,
    # e.g. if there is no positioner connected for the given channel.
    # The channel state can be polled to determine the moment when the movement finished.
    # Alternatively, channel events can be used to receive "commandFinished" events.
    # Both methods are not show in this example. Instead, refer to the further programming examples.

    # Generally the appropriate movement properties (like mode, velocity, acceleration, etc.)
    # should be set before starting the actual movement.

    # The following code shows the calibration sequence, the find reference function, closed loop
    # movement and open loop movement.
    # See the corresponding functions "calibrate","findReference" and "move" at the
    # end of this file for more information on the specific properties.

    # We assume that there is a linear positioner with integrated sensor connected to channel 0.
    channel = 0
    # We start by setting some general channel properties.
    type = ctl.GetProperty_i32(d_handle, channel, ctl.Property.CHANNEL_TYPE)
    if type == ctl.ChannelModuleType.STICK_SLIP_PIEZO_DRIVER:
        # Set max closed loop frequency (maxCLF) to 6 kHz. This properties sets a limit for the maximum actuator driving frequency.
        # The maxCLF is not persistent thus set to a default value at startup.
        ctl.SetProperty_i32(d_handle, channel, ctl.Property.MAX_CL_FREQUENCY, 6000)
        # The hold time specifies how long the position is actively held after reaching the target.
        # This property is also not persistent and set to zero by default.
        # A value of 0 deactivates the hold time feature, the constant ctl.HOLD_TIME_INFINITE sets the time to infinite.
        # (Until manually stopped by "Stop") Here we set the hold time to 1000 ms.
        ctl.SetProperty_i32(d_handle, channel, ctl.Property.HOLD_TIME, 1000)
    elif type == ctl.ChannelModuleType.MAGNETIC_DRIVER:
        # Enable the amplifier (and start the phasing sequence).
        ctl.SetProperty_i32(d_handle, channel, ctl.Property.AMPLIFIER_ENABLED, ctl.TRUE)

    # The move mode states the type of movement performed when sending the "Move" command.
    move_mode = ctl.MoveMode.CL_ABSOLUTE
    printMenu()
    while True:
        key = input()
        if key == 'c':
            calibrate(channel)
        elif key == 'f':
            findReference(channel)
        elif key == '+':
            move(channel, move_mode, 0)
        elif key == '-':
            move(channel, move_mode, 1)
        elif key == 's':
            stop(channel)
        elif key == 'p':
            position = ctl.GetProperty_i64(d_handle, channel, ctl.Property.POSITION)
            print("MCS2 position: {} pm.".format(position))
        elif key == '0':
            move_mode = ctl.MoveMode.CL_ABSOLUTE
            ctl.SetProperty_i32(d_handle, channel, ctl.Property.MOVE_MODE, move_mode)
            print("MCS2 set closed-loop absolute move mode.")
        elif key == '1':
            move_mode = ctl.MoveMode.CL_RELATIVE
            ctl.SetProperty_i32(d_handle, channel, ctl.Property.MOVE_MODE, move_mode)
            print("MCS2 set closed-loop relative move mode.")
        elif key == '2':
            move_mode = ctl.MoveMode.SCAN_ABSOLUTE
            ctl.SetProperty_i32(d_handle, channel, ctl.Property.MOVE_MODE, move_mode)
            print("MCS2 set open-loop scan absolute move mode.")
        elif key == '3':
            move_mode = ctl.MoveMode.SCAN_RELATIVE
            ctl.SetProperty_i32(d_handle, channel, ctl.Property.MOVE_MODE, move_mode)
            print("MCS2 set open-loop scan relative move mode.")
        elif key == '4':
            move_mode = ctl.MoveMode.STEP
            ctl.SetProperty_i32(d_handle, channel, ctl.Property.MOVE_MODE, move_mode)
            print("MCS2 set open-loop step move mode.")
        elif key == '5':
            # In the "normal" actuator mode the control loop generates actuator driving signals
            # with a maximum frequency limited by the max closed loop frequency (maxCLF).
            ctl.SetProperty_i32(d_handle, channel, ctl.Property.ACTUATOR_MODE, ctl.ActuatorMode.NORMAL)
            print("MCS2 set normal actuator mode.")
        elif key == '6':
            # The "quiet" actuator mode allows positioner movement with minimal noise emission.
            ctl.SetProperty_i32(d_handle, channel, ctl.Property.ACTUATOR_MODE, ctl.ActuatorMode.QUIET)
            print("MCS2 set quiet actuator mode.")
        elif key == 'q':
            break
        elif key == '?':
            printMenu()

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
