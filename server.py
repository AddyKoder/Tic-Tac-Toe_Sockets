import socket
from threading import Thread
from random import choice

# ----------------- VARIABLES ----------------- #

rooms = {}
random_rooms = []

# ----------------- METHODS ----------------- #


# change the board list to a single string
def encrypt(b):
    stringed = ''
    for i in b:
        stringed = stringed + i

    return stringed


# return True if game is drawn and False if is going on
def check_draw(b):
    if '-' not in b:
        return 1


# return 1/2 for the player who won X/O and None if no one has won
def check_win(b):
    winning_pos = [
        [1, 2, 3], [4, 5, 6], [7, 8, 9],
        [1, 4, 7], [2, 5, 8], [3, 6, 9],
        [1, 5, 9], [3, 5, 7]
    ]

    for i in winning_pos:
        v1, v2, v3 = i[0] - 1, i[1] - 1, i[2] - 1

        if b[v1] == 'X' and b[v2] == 'X' and b[v3] == 'X':
            return 'X'
        if b[v1] == 'O' and b[v2] == 'O' and b[v3] == 'O':
            return 'O'


# returns the position of the game
# '.' : game is going on
# '-' : game has drawn
# 'X' : X has won the game
# 'O' : O has won the game
def check_game_pos(b):
    if check_win(b):
        return check_win(b)

    elif check_draw(b):
        return '-'

    return '.'

    # ----------------- SERVER CLASS ----------------- #


# it continuously listens for client connection requests and adds them to
# a room with another client

# it pairs client based on the connection sequence
# c1, c2 will be in room 1 and c3, c4 will be in room 2

# it instantiates the ROOM class to create a room
# which has a separate board and other variables

class Server:

    # Initializes the sockets for use in the server
    def __init__(self):
        # ---------- SOCKET VARIABLES -----------#

        self.PORT = 8080

        self.IP = socket.gethostbyname(socket.gethostname())
        self.ADDRESS = (self.IP, self.PORT)

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.ADDRESS)

        self.server.listen()

    # listens for connection requests and add clients to the
    # room by pairing them with another client
    def listen(self):
        # this method is used to send a message to the client
        # specifically designed to send error messages

        def return_error(c, e):
            try:
                c.send(e.encode('utf-8'))
            except ConnectionResetError or ConnectionAbortedError or ConnectionRefusedError:
                return False

        random_rooms.append(room())

        while True:
            client, address = self.server.accept()

            # client.send('___'.join(rooms.keys()).encode('utf-8'))

            # receives a join request from the client
            # client either sends the create or join command for the room

            message = client.recv(64).decode('utf-8').split('___')
            command = message[0]
            name = message[1]

            # making the client join or create a room based on the command sent
            if command == 'c':
                if name not in rooms:
                    rooms[name] = room()
                    if rooms[name].get_cond():
                        client.send('s'.encode('utf-8'))
                        rooms[name].get_clients(client)

                    else:
                        return_error(client, 'Room full')
                else:
                    return_error(client, 'Room already existed')


            elif command == 'j':
                if name in rooms:
                    if rooms[name].get_cond():
                        client.send('s'.encode('utf-8'))
                        rooms[name].get_clients(client)

                    else:
                        return_error(client, 'Room Full')
                else:
                    return_error(client, 'Room not found')

            elif command == 'r':

                if random_rooms[-1].get_cond():
                    client.send('s'.encode('utf-8'))
                    random_rooms[-1].get_clients(client)

                else:
                    random_rooms.append(room())
                    client.send('s'.encode('utf-8'))
                    random_rooms[-1].get_clients(client)


    # ----------------- ROOM MAIN CLASS ----------------- #


# This is th main class which creates a tic-tac-toe room for 2 clients
# to play on
# this can be instantiated multiple times to create multiple rooms
# which is done by the server class
class room:

    # initializes the room variables
    def __init__(self):

        self.board = ['-', '-', '-',
                      '-', '-', '-',
                      '-', '-', '-']
        self.position = '.'
        self.chance, self.next_chance = 'X', 'O'
        self.connections = []
        self.players = []

    # takes 2 client objects and creates a room for them
    # player pieces are assigned as first come first chance
    # starts the handle_client method to handle each
    # client separately
    def get_clients(self, c1):
        if len(self.players) < 2:

            player = self.get_playerTag()

            c1.send(player.encode('utf-8'))

            Thread(target=self.handle_client, args=(c1, player)).start()
            self.players.append(player)

            return True
        else:
            return False

    def get_cond(self):
        if len(self.players) < 2:
            return True
        return False

    # return the piece(X,O) that a player will be assigned to.
    def get_playerTag(self):
        if len(self.players) < 2:
            if 'X' in self.players:
                return 'O'
            elif 'O' in self.players:
                return 'X'
            else:
                return choice(['X', 'O'])

    # updates the game_situ variable which holds the position of
    # a particular player in the game
    # this variable is then sent to the client to tell them their
    # position
    def update_game_situ(self, player):
        if self.position == player:
            return 'WON'
        elif self.position == '-':
            return 'DRAW'
        elif self.position != '.':
            return 'LOST'

        return '.'

    # resets the board variable of a room to default
    def reset_board(self):

        self.board = ['-', '-', '-',
                      '-', '-', '-',
                      '-', '-', '-']

    # start listening for connections
    # def listen_connections(self):
    #     while True:
    #         if len(connections) < 2:
    #             player = self.get_playerTag()
    #
    #             client, address = self.server.accept()
    #             client.send(player.encode('utf-8'))
    #             Thread(target=self.handle_client, args=(client, player)).start()
    #
    #             connections.append(client)
    #             players.append(player)

    # handles a single client at a time, always used with 2 clients only to
    # create a room, this is the main method for the full server script
    # it handles the clients, sends receives data and analyzes games
    def handle_client(self, client, player):

        # used to disconnect a client from the server
        def disconnect():
            if client in self.connections and player in self.players:
                self.connections.remove(client)
                self.players.remove(player)
            self.reset_board()
            self.chance, self.next_chance = 'X', 'O'

        # takes a message argument
        # it sends the message string to the client and handles
        # the exceptions and closes the connection if the client is offline
        def send_message(message):
            try:
                client.send(message.encode('utf-8'))
                return True
            except ConnectionResetError:
                disconnect()
                return False

        connected = True
        game_situ = '.'
        # the main game loop. this is ran while the game is being
        # played actively from both the 2 clients and sends-receives
        # data iteratively to keep a connection between the two clients
        # and maintain the room

        while connected and game_situ == '.':

            # updating the games situation if is already default
            if self.position == '.':
                self.position = check_game_pos(self.board)
                game_situ = self.update_game_situ(player)

            # performed only if the chance is of the current player
            # performs a 3 cycle information exchange to make a chance
            if self.chance == player:

                # 1 - sends the board and game situation to the client
                send_message(f'{encrypt(self.board)}___{game_situ}')

                # 2 - after the client has observed the board and made their
                #     chance. it expects an reply by the client for their
                #     chance. Received it updates the board variable of the room
                try:
                    n = int(client.recv(4).decode('utf-8'))
                except ConnectionResetError or ConnectionAbortedError or ValueError:
                    disconnect()
                    break
                # updating the board
                self.board[n - 1] = player

                # 3 - again updates the game situation and player situation
                #     and sends the board and game situation of the player to the player
                #     finally swaps the chance, next_chance variable to continue the game
                if self.position == '.':
                    self.position = check_game_pos(self.board)
                    game_situ = self.update_game_situ(player)
                connected = send_message(f'{encrypt(self.board)}___{game_situ}')

                self.chance, self.next_chance = self.next_chance, self.chance

        # done after the main loop has done execution either by completing the
        # game or by disconnection of a client
        # it then returns the final board and game position to the player
        self.position = check_game_pos(self.board)
        game_situ = self.update_game_situ(player)
        send_message(f'{encrypt(self.board)}___{game_situ}')


if __name__ == '__main__':
    # calls the listen function of the Server class which
    # starts the listening to the client connections and start
    # making rooms

    Server().listen()
