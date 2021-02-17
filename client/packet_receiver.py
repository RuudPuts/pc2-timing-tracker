import socket
from io import BytesIO

from pcars import Packet


class PacketReceiver:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("0.0.0.0", 5606))

        print("Server started, waiting for data...")

    def read_packet(self):
        data, address = self.sock.recvfrom(1500)

        return Packet.read_from(BytesIO(data))
