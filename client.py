import socket
import time
import scapy.all as scapy
import struct

# network ip
ip = '127.0.0.1' # localhost
# ip = scapy.get_if_addr('eth1') # dev
# ip = scapy.get_if_addr('eth2') # test

# ports
udp_port = 8081 # udp port on my localhost
tcp_port = 9090 # tcp port on my localhost
# udp_port = 13117 # udp port for sending offers
# tcp_port = 2063 # tcp port we get from the course



def create_udp_connection_client():
    # Create a UDP socket
    udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_server_socket.bind(('localhost', udp_port))

    while True:
        try:
            data, server_address = udp_server_socket.recvfrom(1024)
            
            print('received {} bytes from {}'.format(
                len(data), server_address))

            print(data)
            server_data = struct.unpack('4s 1s 2s', data)
            print(server_data)

            magic_cookie = server_data[0].hex()
            msg_type = server_data[1].hex()
            server_port = server_data[2].hex()

            if magic_cookie == 'feedbeef' and msg_type == '02':
                sent = udp_server_socket.sendto(b'Pink fluffy unicorn dancing', server_address)
                print('sent {} bytes back to {}'.format(
                    sent, server_address))
        except Exception as err:
            print(err)

    udp_server_socket.close()
    return

create_udp_connection_client()