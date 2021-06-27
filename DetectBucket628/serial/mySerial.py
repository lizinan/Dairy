import serial
import serial.tools.list_ports
import struct
import binascii
import time


# def seePortList():
#     port_list = list(serial.tools.list_ports.comports())
#     if len(port_list) == 0:
#         print('无可用串口')
#     else:
#         print(port_list)
#         for i in range(0,len(port_list)):
#             print(port_list[i])
#     return port_list[0]

def openSerial():
    # portName = seePortList()
    portx = "/dev/ttyACM0"
    bps = 115200
    mySerial = serial.Serial(portx,bps,timeout = 0.1)
    return mySerial

def recMsg(mySerial):
    num = mySerial.in_waiting
    if num:
        rxMsg = mySerial.readline()
        if rxMsg == b'#PO\n':
            return 1
        if rxMsg == b'#ZJ\n':
            return 2
    return 0

def sendMsg(mySerial,id,centerPoint,slope):
    if id == 1:
        Msg = [(int)(centerPoint[0]),(int)(centerPoint[1]),(int)(100*slope)]
        # txMsg = []
        # for i in range(3):
        #     Msg[i] = bin(Msg[i]& 0b1111111111111111)
        mySerial.write(b'#')
        mySerial.write(10)
        mySerial.write("Msg[0]".encode("utf-8"))
        mySerial.write(0x0a)
    if id == 2:
        mySerial.write(b'Z')
        mySerial.write(b'J')
        mySerial.write(0x0a) 
        over = 1
    if id == 0:
        mySerial.write(0)
        over = 1

# def sendMsg(mySerial,id):
#     if id == 1:
#         txMsg = b'POo'
#         mySerial.write(txMsg)
#         # txMsg = 0x40
#         # mySerial.write(txMsg)



# def sendMsg(world_coordinate):
#     mySerial = openSerial()
#     while True:
#         if sendCount:
#             mySerial.write(b'#')
#             for i in range(4):
#                 txMsg = world_coordinate[i][0]
#                 mySerial.write(txMsg)
#                 txMsg = world_coordinate[i][1]
#                 mySerial.write(txMsg)
#             txMsg = 0x0a
#             mySerial.write(txMsg)
#             sendCount = sendCount - 1
#             time.sleep(1)
#     mySerial.close()

# def sendMsg():
#     while True:
#         num = mySerial.in_waiting
#         if num:
#             rxMsg = mySerial.read_all()
#             if rxMsg[0:4] == b'#PO\n':
#                 txMsg = b'#'
#                 mySerial.write(txMsg)
#                 for i in range(8):
#                     txMsg = world_coordinate[i]
#                     mySerial.write(txMsg)
#                 mySerial.write(0x0a)
#     mySerial.close()


# test file
# if __name__ == '__main__':
#     point = ([0,2]*4)
#     seePortList()

#     try:
#         portx = "/dev/ttyUSB0"
#         bps = 115200
#         mySerial = serial.Serial(portx,bps)
#         print("set successful")
#         while True:
#             if mySerial.in_waiting:
#                 txMsg = mySerial.write(point)#TODO: 还没写
#                 data = mySerial.read_all()
#                 if data[0:3] == b'\x00@\x0c':
#                     print("ok")
#                 print("txMsg",txMsg,"point",point)
#                 print("data",data)
#                 print("test",data[0:3])
#             else:
#                 continue

#         mySerial.close()#关闭串口
#     except Exception as e:
#         print("--error--:",e)
