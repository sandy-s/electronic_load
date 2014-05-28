import serial

class Array3700:
    STATUS = 0x91
    FRAME_LENGTH = 26
    PAYLOAD_LENGTH = 22

    def __init__(self, port, baudrate, address):
        self.port = port
        self.baudrate = baudrate
        self.address = address
        self.serial = serial.Serial(self.port, self.baudrate, timeout=1)

    def update_status(self):
        self.data = self.__get_status()

    def get_current_ma(self):
        return self.__bytes2int(self.data[3:5])

    def get_voltage_mv(self):
        return self.__bytes2int(self.data[5:9])

    def get_power_mw(self):
        return self.__bytes2int(self.data[9:11]) * 100
    
    def get_max_current_ma(self):
        return self.__bytes2int(self.data[11:13])
    
    def get_max_power_mw(self):
        return self.__bytes2int(self.data[13:15]) * 100
    
    def get_resistance_mohm(self):
        return self.__bytes2int(self.data[15:17]) * 10

    def get_output_state(self):
        return self.__bytes2int(self.data[17])
    
    def __get_status(self):
        while 1:
            self.__send_message(self.STATUS, self.PAYLOAD_LENGTH * [0])
            data = self.serial.read(self.FRAME_LENGTH)
            if len(data) == self.FRAME_LENGTH:
                return data
            else:
                print 'communication error'

    def __send_message(self, command, payload):
        data = bytearray([0xaa, self.address, command] + payload + [0])
        data[self.FRAME_LENGTH-1] = self.__checksum(data)
        self.serial.write(data)

    def __checksum(self, data):
        checksum = 0
        for byte in data:
            checksum += byte
        return checksum % 256

    def __bytes2int(self, data):
        result = 0;
        for i in range(len(data)):
            result = result * 256 + ord(data[len(data) -1 - i])
        return result
