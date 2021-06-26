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
        seePortList()
        #portx = "/dev/ttyACM0"
        portx = "/dev/ttyUSB0"
        bps = 115200
        mySerial = serial.Serial(portx,bps)
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
    return 0

def sendMsg(mySerial,id,arrowCarCoord):
    if id == 1:
        mySerial.write(b'#')
        mySerial.write(b'P')
        mySerial.write(b'O')
        for i in range(len(arrowCarCoord)):
            Msg = [str((int)(arrowCarCoord[i][0][0])),str((int)(arrowCarCoord[i][0][1])),str((int)(arrowCarCoord[i][1][0])),str((int)(arrowCarCoord[i][1][1]))]
            print(Msg)
            for j in range(4):
                Msg[j] = bytes(Msg[j], encoding='utf-8')
                mySerial.write(Msg[j])
                if i != len(arrowCarCoord) and j != 3:
                    mySerial.write(b',')
        mySerial.write(chr(0x0a).encode("utf-8"))
    if id == 2:
        mySerial.write(b'#ZJ')
        mySerial.write(0x0a) 
    if id == 0:
        mySerial.write(0)




