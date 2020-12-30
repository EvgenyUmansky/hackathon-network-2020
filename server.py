import socket
import time
import scapy.all as scapy
import struct
import random
import _thread
import select

threads_counter = 0
game_is_on = True

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
# tcp_server_socket.settimeout(1)

players = {}
group_1 = {}
group_2 = {}
group_1_score = 0
group_2_score = 0


def create_udp_connection_server():
    global threads_counter 
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
        while time.time() <= time_end_broadcast: # check if passed 10 seconds
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
    print('FINISHED THE UDP')
    threads_counter -=1
    return


def create_teams_tcp():
    global group_1, group_2, threads_counter
    time_end_broadcast = time.time() + 10 # when to finish the sending of offers (10 secs)
    while time.time() <= time_end_broadcast: # check if passed 10 seconds
        # Wait for a connection
        
        readable, writable, exceptional = select.select([tcp_server_socket], [], [], 0)
        for s in readable:
            if isinstance(s, socket.socket):
                client_connection, client_address = tcp_server_socket.accept()
                print('connection from', client_address)
                team_name = client_connection.recv(1024).decode("utf-8")
                players[client_address[0]] = team_name
                print(players)

                teams_list=list(players.keys())
                random.shuffle(teams_list)

                half = len(teams_list) // 2
                group_1_list = teams_list[:half] 
                group_2_list = teams_list[half:]

                group_1 = { i : 0 for i in group_1_list }
                group_2 = { i : 0 for i in group_2_list }

    print('FINISHED THE TCP')
    threads_counter -= 1
    return

def game():
    global game_is_on, group_1_score, group_2_score, threads_counter

    welcome_message = f"Welcome to Keyboard Spamming Battle Royale.\nGroup 1:\n==\n{group_1}Group 2:\n==\n{group_2}\nStart pressing keys on your keyboard as fast as you can!!"
    game_is_on = True

    start_game_time = time.time()
    while time.time() - start_game_time <= 10:
        readable, writable, exceptional = select.select([tcp_server_socket], [], [], 0)
        for s in readable:
            if isinstance(s, socket.socket):
                client_connection, client_address = tcp_server_socket.accept()
                tcp_server_socket.sendall(welcome_message.encode())
                key_pressed = client_connection.recv(1024).decode("utf-8")

                team = players[client_address[0]]
                if team in group_1:
                    group_1_score += len(key_pressed.encode())
                elif team in group_2:
                    group_2_score += len(key_pressed.encode())

    threads_counter -= 1
    return

while True:
    try:
        _thread.start_new_thread(create_udp_connection_server, ())
        threads_counter += 1
        _thread.start_new_thread(create_teams_tcp, ())
        threads_counter += 1
        _thread.start_new_thread(game(), ())
        threads_counter += 1
    except Exception as e:
        # pass
        print(e)
    while threads_counter > 0:
        pass

