def read_speed():
    data = ser.read(4)
    if len(data) < 4:
        speed = 0
    if data[0] == 0xFC and data[1] == 0xFA and data[3] == 0x00:
        speed = data[2]
    return speed
    time.sleep(0.1)