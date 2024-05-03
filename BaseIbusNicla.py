from pyb import UART, LED
import sensor
import time
import math
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.ioctl(sensor.IOCTL_SET_FOV_WIDE, True)
sensor.set_framesize(sensor.HQVGA)
sensor.skip_frames(time=2000)
sensor.set_vflip(True)
sensor.set_hmirror(True)
thresholdsRedBall = (22, 92, 86, 27, -32, 127)
thresholdsYellowBall = (35, 100, -128, -2, 21, 127)
def calculate_duck_position(u, s_b):
        m_u = 0.136
        c_u = -20.4
        m_sb = 150880
        c_sb = 12.3
        theta = m_u * u + c_u
        d = m_sb * (1/s_b) + c_sb
        theta_rad = math.radians(theta)
        x = d * math.cos(theta_rad)
        y = d * math.sin(theta_rad)
        return x, y
r_LED = LED(1)
g_LED = LED(2)
b_LED = LED(3)
g_LED.on()
r_LED.off()
b_LED.off()
clock = time.clock()
uart = UART("LP1", 115200, timeout_char=2000)
def checksum(arr, initial= 0):
    sum = initial
    for a in arr:
        sum += a
    checksum = 0xFFFF - sum
    chA = checksum >> 8
    chB = checksum & 0xFF
    return chA, chB
def IBus_message(message_arr_to_send):
    msg = bytearray(32)
    msg[0] = 0x20
    msg[1] = 0x40
    for i in range(len(message_arr_to_send)):
        msg_byte_tuple = bytearray(message_arr_to_send[i].to_bytes(2, 'little'))
        msg[int(2*i + 2)] = msg_byte_tuple[0]
        msg[int(2*i + 3)] = msg_byte_tuple[1]
    chA, chB = checksum(msg[:-2], 0)
    msg[-1] = chA
    msg[-2] = chB
    uart.write(msg)
def refreshIbusConnection():
    if uart.any():
        uart_input = uart.read()
x = 0
y = 0
height = 0
w = 0
while True:
    clock.tick()
    img = sensor.snapshot()
    print(clock.fps())
    blobs = img.find_blobs([thresholdsRedBall, thresholdsYellowBall], area_threshold=200, merge=True)
    color_is_detected = False
    max_blob = None
    max_pixels = 0
    for blob in blobs:
       if blob.pixels() > max_pixels:
           max_blob = blob
           max_pixels = blob.pixels()


    if max_blob:
        color_is_detected = True
        img.draw_rectangle(blob.rect(), color=(0,255,0))
        img.draw_cross(blob.cx(), blob.cy(), color=(0,255,0))
        print("Center (x, y): ({}, {})  Size: {}".format(blob.cx(), blob.cy(), blob.area()))
        x = blob.cx()
        y = blob.cy()
        height = blob.h()
        w = blob.w()
    flag = 0
    if (color_is_detected):
        print("look!!!!")
        g_LED.off()
        r_LED.off()
        b_LED.on()
        flag = 1
    else:
        g_LED.on()
        r_LED.off()
        b_LED.off()
    pixels_x = x
    pixels_y = y
    pixels_w = w
    pixels_h = height
    #print("Here is Pixels X", pixels_x)
    #print("Here is Pixels Y", pixels_y)

    messageToSend = [flag, pixels_x, pixels_y, pixels_w, pixels_h]
    print(messageToSend)
    IBus_message(messageToSend)
    refreshIbusConnection()
