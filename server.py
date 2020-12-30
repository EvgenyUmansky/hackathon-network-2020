import socket
import time
import scapy.all as scapy
import struct
import random
import _thread
import select

threads_counter = 0
welcome_message = ''

# network ip
partly_ip = '127.0.0.' # localhost
server_ip = '127.0.0.1'

# partly_ip = '172.1.0.'
# server_ip = scapy.get_if_addr('eth1') # dev
# server_ip = scapy.get_if_addr('eth2') # test

# ports
udp_port = 8081 # udp port on my localhost
tcp_port = 9091 # tcp port on my localhost
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

# data about players
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
                    address = ('127.0.0.1', udp_port) # define new address, one of 172.1.0.0-255 (or 127.0.0.0-255 if local)
                    udp_server_socket.sendto(packed_message, address) # send the offer to defined address
                except:
                    pass
            time.sleep(1) # broadcasting every 1 second
    except:
        pass

    # close udp stream
    udp_server_socket.close()
    threads_counter -=1
    return


def create_teams_tcp():
    global group_1, group_2, threads_counter, welcome_message, group_1_score, group_2_score
    time_end_broadcast = time.time() + 10 # when to finish the sending of offers (10 secs)
    while time.time() <= time_end_broadcast: # check if passed 10 seconds
        # Wait for a connection
        readable, writable, exceptional = select.select([tcp_server_socket], [], [], 0)
        for s in readable:
            if isinstance(s, socket.socket):
                # create tcp connection with players
                client_connection, client_address = tcp_server_socket.accept()
                team_name = client_connection.recv(1024).decode("utf-8")
                players[team_name] = (client_address, client_connection)

                # organaze random teams in 2 groups
                teams_list=list(players.keys())
                random.shuffle(teams_list)

                half = len(teams_list) // 2
                group_1_list = teams_list[:half] 
                group_2_list = teams_list[half:]

                # count spamming by team 
                group_1 = { i : 0 for i in group_1_list }
                group_2 = { i : 0 for i in group_2_list }

    group_1_names = '\n'.join(group_1.keys())
    group_2_names = '\n'.join(group_2.keys())
    welcome_message = f"Welcome to Keyboard Spamming Battle Royale.\nGroup 1:\n==\n{group_1_names}\nGroup 2:\n==\n{group_2_names}\nStart pressing keys on your keyboard as fast as you can!!"
    
    try:
        # start the game with thread for each game
        for key, client_data in players.items():
            threads_counter += 1
            _thread.start_new_thread(game(key, client_data), ())
    except Exception as e:
        pass


    # get the winner
    winner = 0
    winners_names = ""
    if group_1_score > group_2_score:
        winners_names = winners_names.join(list(group_1.keys()))
        winner = 1
    else:
        winners_names = winners_names.join(list(group_2.keys()))
        winner = 2

    # create summer message and send it to clients
    summary = 'Game over!\nGroup 1 typed in {} characters. Group 2 typed in {} characters.\nGroup {} wins!\n\nCongratulations to the winners: {}'.format(
        group_1_score, group_2_score, winner, winners_names)

    for key, client_data in players.items():
        client_data[1].sendall(summary.encode())

    threads_counter -= 1
    return
    


def game(team_name, client_data):
    # start game for client
    global threads_counter, group_1_score, group_2_score
    # tcp_server_socket.sendall(welcome_message.encode())
    socket_game = client_data[1]
    socket_game.sendall(welcome_message.encode())
    start_game_time = time.time()
    while time.time() - start_game_time <= 10:
        readable, writable, exceptional = select.select([socket_game], [], [], 0)
        for s in readable:
            if isinstance(s, socket.socket):
                try:
                    # client_connection, client_address = socket_game.accept()
                    key_pressed = socket_game.recv(1024).decode("utf-8")

                    # count scores for two teams
                    if team_name in group_1:
                        group_1_score += len(key_pressed)
                    elif team_name in group_2:
                        group_2_score += len(key_pressed)
                except Exception as e:
                    pass

    threads_counter -= 1
    return

while True:
    # clear the lists 
    players = {}
    group_1 = {}
    group_2 = {}
    group_1_score = 0
    group_2_score = 0
    try:
        # start the server
        _thread.start_new_thread(create_udp_connection_server, ())
        threads_counter += 1
        _thread.start_new_thread(create_teams_tcp, ())
        threads_counter += 1
        # _thread.start_new_thread(game(), ())
        # threads_counter += 1
    except Exception as e:
        pass

    while threads_counter > 0:
        time.sleep(0.2)

