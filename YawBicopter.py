from comm.Serial import SerialController, DataType_Int, DataType_Float, DataType_Boolean
from joystick.JoystickManager import JoystickManager
from gui.simpleGUI import SimpleGUI
from user_parameters import ROBOT_MAC, SERIAL_PORT, PRINT_JOYSTICK
import math

import time

BaseStationAddress = ""  # you do not need this, just make sure your DroneMacAddress is not your base station mac address
current_height = 0
current_orientation = 0
PRINT_JOYSTICK = True

if __name__ == "__main__":
    # Communication
    serial = SerialController(SERIAL_PORT, timeout=.5)  # .5-second timeout
    serial.manage_peer("A", ROBOT_MAC)
    serial.manage_peer("G", ROBOT_MAC)
    time.sleep(.05)
    serial.send_preference(ROBOT_MAC, DataType_Boolean, "zEn", True)
    serial.send_preference(ROBOT_MAC, DataType_Boolean, "yawEn", True)

    # // PID terms
    serial.send_preference(ROBOT_MAC, DataType_Float, "kpyaw", 0.1)  # 1.5
    serial.send_preference(ROBOT_MAC, DataType_Float, "kdyaw", -0.4)  # -.1
    serial.send_preference(ROBOT_MAC, DataType_Float, "kiyaw", 0)

    serial.send_preference(ROBOT_MAC, DataType_Float, "kpz", 0.3)  # 0.3
    serial.send_preference(ROBOT_MAC, DataType_Float, "kdz", 0.6)  # 0.6
    serial.send_preference(ROBOT_MAC, DataType_Float, "kiz", 0.1)  # 0.1

    # // Range terms for the integral
    serial.send_preference(ROBOT_MAC, DataType_Float, "z_int_low", 0.05)
    serial.send_preference(ROBOT_MAC, DataType_Float, "z_int_high", 0.15)

    # Allows the robot to read the parameters from flash memory to be used.
    serial.send_control_params(ROBOT_MAC, (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0))

    time.sleep(.2)

    # Joystick
    joystick = JoystickManager()
    # mygui = SimpleGUI()

    ready = 1
    old_b = 0
    old_x = 0
    dt = .1
    height = 0
    servos = 75
    tz = 0
    fx = 0.0
    try:
        while True:
            # Axis input: [left_vert, left_horz, right_vert, right_horz, left_trigger, right_trigger]
            # Button inputs: [A, B, X, Y]
            axis, buttons = joystick.getJoystickInputs()

            if buttons[3] == 1:  # y stops the program
                break

            # b button is a toggle which changes the ready state
            if buttons[1] == 1 and old_b == 0:  # b pauses the control
                if ready != 0:
                    ready = 0
                else:
                    ready = 1
            old_b = buttons[1]

            if PRINT_JOYSTICK:
                print("Joystick: ", ["{:.1f}".format(num) for num in axis], "Buttons: ", buttons)

            #### CONTROL INPUTS to the robot here #########
            # print("Axis[5]: ", axis[5])
            # print("Axis[4]: ", axis[4])

            ### Original Data
            fx = (axis[5] + 1) / 2 - (axis[2] + 1) / 2  # Forward with the triggers
            # if axis[5] > 0.98:
            #     fx -= 0.05
            # if axis[2] > 0.98:
            #     fx += 0.05

            print("Axis[2]: ", axis[2])

            print("Axis[5]: ", axis[5])
            # print("Axis[4]: ", axis[4])
            # print("!!!!!!!!!!!!!!!!!!!!!!",fx)

            #  axis[2] is the right-handler,

            # print("!!!!!!!!!!!!!!!!!!",axis[2])

            #fz = -axis[0]  # Vertical left joystick
            tx = 0  # No roll control
            #tz = axis[4]  # Horizontal right joystick
            led = -buttons[2]  # Button X

            # Updated the current height  (fz)
            if axis[0] != 0:
                fz = current_height + axis[0] * -0.3
                current_height += axis[0] * -0.3
            else:
                fz = current_height

            print("The current height is : \n", current_height)

            # Updated the orientation tz
            # if axis[4] != 0:
            #
            #     current_orientation = current_orientation + axis[4] * 1.1
            #     if current_orientation >= 360:
            #         current_orientation -= 360
            #     elif current_orientation <= -360:
            #         current_orientation += 360
            #     # if current_orientation < 0:
            #     #     current_orientation = 360 + current_orientation
            #     tz = current_orientation * (math.pi / 180)
            # else:
            #     tz = current_orientation * (math.pi / 180)
            # print("The current orientation is : \n", current_orientation)
            rightAngle = math.pi
            leftAngle = -math.pi
            # if axis[4] > -0.1 and axis[4] < 0.1:
            #     tz = 0
            if abs(axis[4]) > 0.1:
                if tz < rightAngle and tz > leftAngle:
                    #if current_orientation < 180 and current_orientation > -180:
                        current_orientation -= axis[4] * 4
                        # tz = current_orientation * (math.pi / 180)
                elif current_orientation >= 180:
                    current_orientation = 179
                elif current_orientation <= -180:
                    current_orientation = -179
                tz = current_orientation * (math.pi / 180)
            print("angle---in radians", tz)

            # if axis[4] != 0:
            #     current_orientation += axis[4] * 1.1
            #     # Normalize the orientation to be within [0, 360) degrees
            #     current_orientation = current_orientation % 360
            #     # The above line replaces the need for if-elif conditions for overflow handling
            #     # and handles negative values correctly due to how Python's modulo operates.
            #
            # # Convert the orientation to radians outside the if-else structure
            # # to avoid duplication and ensure it's always performed regardless of axis[4]'s value.
            # tz = current_orientation * (math.pi / 180)

            # print("The current orientation is : ", current_orientation)
            # print("Orientation in radians (tz): ", tz)
            # Updated the fx value

            print("fx={:.2f} fz={:.2f} tz={:.2f} LED={:.2f} ".format(fx, fz, tz, led), end=' ')
            ############# End CONTROL INPUTS ###############
            sensors = serial.getSensorData()
            #
            # if sensors:
            #     print("Sensors:", ["{:.2f}".format(val) for val in sensors])
            #     mygui.update(
            #         cur_yaw=sensors[1],
            #         des_yaw=tz,
            #         cur_height=sensors[0],
            #         des_height=height,
            #         battery=sensors[2],
            #         distance=sensors[3],
            #         connection_status=True,
            #     )
            # else:
            #     print("No sensors")

            # Send through serial port
            # fx movement
            # fz height
            # tz torque
            serial.send_control_params(ROBOT_MAC, (ready, fx, fz, tx, tz, led, 0, 0, 0, 0, 0, 0, 0))
            time.sleep(dt)

    except KeyboardInterrupt:
        print("Stopping!")
        # Send zero input
serial.send_control_params(ROBOT_MAC, (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
