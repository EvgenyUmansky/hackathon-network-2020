import socket
import time
import scapy.all as scapy
import struct

# network ip
client_ip = '127.0.0.1' # localhost
# client_ip = scapy.get_if_addr('eth1') # dev
# client_ip = scapy.get_if_addr('eth2') # test

# ports
udp_port = 8081 # udp port on my localhost
client_tcp_port = 9090 # tcp port on my localhost
# udp_port = 13117 # udp port for sending offers
# client_tcp_port = 2063 # tcp port we get from the course
server_tcp_ip = None
server_tcp_port = None

# our team name
team_name = "Pink fluffy unicorns dancing on rainbow\n"


def create_udp_connection_client():
    # Create a UDP socket
    try:
        udp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # enable port reusage
        udp_client_socket.bind((client_ip, udp_port))
    except:
        return

    print("Client started, listening for offer requests...")
    while True:
        try:
            # recieve data and address of the server
            data, server_address = udp_client_socket.recvfrom(1024)

            # TODO: for debug, delete it
            print('received {} bytes from {}'.format(
                len(data), server_address))
            print(data)

            # get data from server in hex format
            server_data = struct.unpack('4s 1s 2s', data)
 
            magic_cookie = server_data[0].hex() # get magic cookie
            msg_type = int(server_data[1].hex()) # get type of the message
            
            # validate the offer from the server
            if magic_cookie == 'feedbeef' and msg_type == 2:
                # get ip and port for tcp
                global server_tcp_ip, server_tcp_port
                server_tcp_ip = server_address[0] # get server's ip for tcp
                server_tcp_port = int(server_data[2].hex()) # get server's port for tcp
                break
            
        except:
            pass

    # close the udp stream
    udp_client_socket.close()
    return

def create_tcp_connection_client():
    if server_tcp_port is None or server_tcp_port is None:
        return
    
    print("Received offer from {}, attempting to connect...".format(server_tcp_ip))

    try:
        # config tcp
        tcp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create tcp socket
        tcp_client_socket.connect((server_tcp_ip, server_tcp_port)) # connect the tcp socket to the server

        # send the team name to the server
        tcp_client_socket.sendall(team_name)

        while True:
            data = tcp_client_socket.recv(1024)
            print('received {!r}'.format(data))

    except Exception as e: 
        print(e)
    
    finally:
        # close the tcp udp stream
        tcp_client_socket.close()
    
    global is_connected
    is_connected = False
    return


create_udp_connection_client()
create_tcp_connection_client()