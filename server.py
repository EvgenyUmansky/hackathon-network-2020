import socket
import time
import scapy.all as scapy
import struct


# network ip
ip = '127.0.0.1' # localhost
# dev_network_ip = scapy.get_if_addr('eth1')
# test_network_ip = scapy.get_if_addr('eth2')

# ports
tcp_port = 8080 # tcp port on my localhost
udp_port = 8081 # udp port on my localhost
# tcp_port = 2008 # tcp port we get from the course
# udp_port = 13117 # udp port for sending offers

# create udp and tcp sockets
udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# config udp
udp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) # enable broadcasting mode for the udp socket
udp_server_socket.bind(('', udp_port)) # bind the udp socket to all available interfaces and our udp_port

# create udp message
str_message = 'feedbeef02'+ str(tcp_port)
byte_message = bytes.fromhex(str_message) # to hex byte string
packed_message = struct.pack('7s', byte_message) # to pack with 7 bytes

# config tcp
tcp_server_socket.bind((ip, tcp_port)) # bind the tcp socket to ip of the machine and our tcp port
tcp_server_socket.listen(1) # listen for incoming connections, only 1 allowed to be unaccepted


def create_udp_connection(ip):
    time_end_broadcast = time.time() + 10 # when to finish the sending of offers (10 secs)
    address = (ip, udp_port)
    while time.time() < time_end_broadcast:
        try:
            udp_server_socket.sendto(packed_message, address)
        except Exception as err:
            print(err)

    return





udp_server_socket.close()
tcp_server_socket.close()