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
tcp_port = 8080 # tcp port on my localhost
# tcp_port = 2008 # tcp port we get from the course
# udp_port = 13117 # udp port for sending offers



# create udp message
magic_cookie = bytes.fromhex('feedbeef') # to hex byte string
msg_type = bytes.fromhex('02') # to hex byte string
server_port = bytes.fromhex(str(tcp_port)) # to hex byte string
packed_message = struct.pack('4s 1s 2s', magic_cookie, msg_type, server_port) # 7 bytes for all

# config tcp
tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_server_socket.bind((ip, tcp_port)) # bind the tcp socket to ip of the machine and our tcp port
tcp_server_socket.listen(1) # listen for incoming connections, only 1 allowed to be unaccepted


def create_udp_connection_server():
    players = {}
    # create udp socket
    udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # config udp
    udp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) # enable broadcasting mode for the udp socket
    udp_server_socket.bind(('', udp_port)) # bind the udp socket to all available interfaces and our udp_port

    time_end_broadcast = time.time() + 10 # when to finish the sending of offers (10 secs)
    address = (ip, udp_port)
    while time.time() < time_end_broadcast:
        try:
            udp_server_socket.sendto(packed_message, address)
        except Exception as err:
            print(err)

        
        data, client_address = udp_server_socket.recvfrom(1024)
        print(data, client_address)
    udp_server_socket.close()
    return



print("Server started, listening on IP address " + str(ip))
create_udp_connection_server()

tcp_server_socket.close()