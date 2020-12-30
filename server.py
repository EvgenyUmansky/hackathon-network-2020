import socket
import time
import scapy.all as scapy
import struct


# network ip
partly_ip = '127.0.0.' # localhost
server_ip = '127.0.0.1'

# partly_ip = '172.1.0.'
# server_ip = scapy.get_if_addr('eth1') # dev
# server_ip = scapy.get_if_addr('eth2') # test

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

# config tcp, we need to open the tcp socket before the udp offers 
# because we start to recieve attemptings to connect before 10 seconds of udp offers are finished
tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # open tcp socket
tcp_server_socket.bind((server_ip, tcp_port)) # bind the tcp socket to ip of the machine and our tcp port
tcp_server_socket.listen(1) # listen for incoming connections, only 1 allowed to be unaccepted

players = {}

def create_udp_connection_server():
    # create udp socket
    udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # config udp
    udp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # enable port reusage
    udp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) # enable broadcasting mode for the udp socket
    udp_server_socket.bind(('', udp_port)) # bind the udp socket to all available interfaces and our udp_port
    # udp_server_socket.settimeout(0.1) # next read/write operation call will be in 0.1 second

    time_end_broadcast = time.time() + 10 # when to finish the sending of offers (10 secs)
    
    print("Server started, listening on IP address " + str(server_ip))

    try:
        while time.time() < time_end_broadcast: # check if passed 10 seconds
            for i in range(0, 256):
                try:
                    client_ip = partly_ip + str(i) # to all IPs in the system
                    address = (client_ip, udp_port) # define new address, one of 172.1.0.0-255 (or 127.0.0.0-255 if local)
                    udp_server_socket.sendto(packed_message, address) # send the offer to defined address
                except:
                    pass
            time.sleep(1) # broadcasting every 1 second
    except:
        pass

    # close udp stream
    udp_server_socket.close()
    return


def create_tcp_connection_server():
    try:
        while True:
            # Wait for a connection
            print('waiting for a connection...')
            client_connection, client_address = tcp_server_socket.accept()
            try:
                print('connection from', client_address)

                # Receive the data in small chunks and retransmit it forever...
                while True:
                    data = client_connection.recv(1024)
                    print('received {!r}'.format(data))
                    if data:
                        print('sending data back to the client')
                        client_connection.sendall(data)
                    else:
                        print('no data from', client_address)
                        break
            except:
                pass

    except:
        pass

    finally:
        tcp_server_socket.close()
    return

while True:
    create_udp_connection_server()
    create_tcp_connection_server()
