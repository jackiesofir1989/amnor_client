import asyncio
from typing import List

import serial

from yaml_manager import Yaml


class V209SGateway:

    def __init__(self, yaml_dict: Yaml):
        self.buffer = b''
        self.yaml = yaml_dict
        self.yaml_dict = self.yaml.load_yaml()
        port = self.yaml_dict.get('port', '/dev/ttyUSB0')
        buad_rate = self.yaml_dict.get('buad_rate', 9600)
        self.max_packet_size = self.yaml_dict.get('max_packet_size', 140)
        self.hops = self.yaml_dict.get('hops', 20)
        self.net_id = self.yaml_dict.get('net_id', 0)
        self.time_out = round(((self.hops * self.max_packet_size * (10.5 / buad_rate) + 50) / 100), 1)
        self.serial_number = self.yaml_dict.get('serial_number', '1111.1111')
        self.call_address = self.yaml_dict.get('call_address', 'localhost:8000')
        self.api_path: str = self.yaml_dict.get('api_path', '')
        self.ser = serial.Serial(
            port=port,
            baudrate=buad_rate,
            bytesize=8,
            parity=serial.PARITY_NONE,
            stopbits=1,
            timeout=(self.time_out + 0.1)
        )

    async def read(self) -> List[int]:
        self.buffer += self.ser.read(self.ser.in_waiting)
        if self.buffer.startswith(b'\x02') and self.buffer.endswith(b'\x03'):
            end = self.buffer[2] + 3
            if self.buffer[end] == 3:
                end = end + 1
                response, self.buffer = self.buffer[:end], self.buffer[end:]
                return list(response)
        return []

    async def write(self, data: bytes):
        await asyncio.sleep(0.05)
        self.ser.write(data)
        self.ser.flush()
        await asyncio.sleep(0.05)

    def get_server_api_path(self):
        self.api_path = self.api_path.format(**self.__dict__)
        return self.api_path

    def get_gw_serial_number(self):
        return self.serial_number

    def init_v209s_parameters(self):
        """Initialize the gateway"""
        list_of_settings = [
            '+++AT\r\n',
            "AT+WS50=1\r\n",  # Binary format
            "AT+WS52=0\r\n",  # full duplex
            f"AT+WS15={self.max_packet_size}\r\n",  # MAX PACKET SIZE
            f'AT+WS11={self.net_id}\r\n',  # NETWORK ID !!!
            f'AT+WS10={self.hops}\r\n',  # Hops
            f'AT+GMN\r\n',  # Serial Num
            f'ATO\r\n'  # Exit setting mode
        ]
        serial_number = self.write_a_list_of_settings(list_of_settings)
        if serial_number:
            self.serial_number = serial_number
        self.save_dict('serial_number', self.serial_number)

    def write_a_list_of_settings(self, settings: List[str]):
        serial_number = ''
        for c in settings:
            self.ser.write(c.encode('utf-8'))
            self.ser.flush()
            bytes_data = self.ser.readline()
            print(bytes_data)
            if b'.' in bytes_data:
                b = [chr(v) for v in bytearray(bytes_data)][:-3]
                serial_number = ''
                for v in b:
                    serial_number += v
        return serial_number

    def set_call_address(self, call_address: str):
        self.call_address = call_address
        self.save_dict('call_address', call_address)

    def set_net_id(self, net_id: int):
        self.net_id = int(net_id)
        list_of_settings = [
            '+++AT\r\n',
            f'AT+WS11={self.net_id}\r\n',  # NETWORK ID !!!
            f'ATO\r\n'  # Exit setting mode
        ]
        self.write_a_list_of_settings(list_of_settings)
        self.save_dict('net_id', net_id)

    def set_hops(self, hops: int):
        self.hops = hops
        list_of_settings = [
            '+++AT\r\n',
            f'AT+WS10={self.hops}\r\n',  # Hops
            f'ATO\r\n'  # Exit setting mode
        ]
        self.write_a_list_of_settings(list_of_settings)
        self.save_dict('hops', hops)

    def save_dict(self, key, value):
        self.yaml_dict[key] = value
        self.yaml.save_yaml(self.yaml_dict)
