import serial
import serial.tools.list_ports

def seePortList():
    port_list = list(serial.tools.list_ports.comports())
    if len(port_list) == 0:
        print('无可用串口')
    else:
        print(port_list)
        for i in range(0,len(port_list)):
            print(port_list[i])
    return port_list[0]

def openSerial():
    try:
        portx = "/dev/ttyACM0"
        bps = 115200
        mySerial = serial.Serial(portx,bps)
        #seePortList()
        return mySerial
    except Exception as e:
        print("---no device connected---")
        return None

def recMsg(mySerial):
    num = mySerial.in_waiting
    if num:
        rxMsg = mySerial.readline()
        if rxMsg == b'#PO\n':
            return 1
        if rxMsg == b'#ZJ\n':
            return 2
        if rxMsg == b'#LO\n':
            return 3
    return 0

def sendMsg(mySerial,id,bucketInfo):
    if id == 1:
        mySerial.write(b'#')
        mySerial.write(b'P')
        mySerial.write(b'O')
        Msg = [str((int)(900 + 10*bucketInfo[0][0])),str((int)(bucketInfo[0][1])),str((int)(900 + 10*bucketInfo[1][0])),str((int)(bucketInfo[1][1]))]
        for i in range(4):
            Msg[i] = bytes(Msg[i], encoding='utf-8')
            mySerial.write(Msg[i])
            mySerial.write(b',')
        mySerial.write(chr(0x0a).encode("utf-8"))
        print(Msg)
    if id == 2:
        mySerial.write(b'#ZJ')
        mySerial.write(0x0a) 
    if id == 0:
        mySerial.write(0)

def getCarPos(mySerial):
    carX = mySerial.readline()
    carY = mySerial.readline()
    return carX,carY

