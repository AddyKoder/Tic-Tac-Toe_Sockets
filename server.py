import socket
from threading import Thread

# ----------------- VARIABLES ----------------- #

rooms = []


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


# returns the position of the particular player in the game
def check_game_pos(b):
    if check_win(b):
        return check_win(b)

    elif check_draw(b):
        return '-'

    return '.'

    # ----------------- ROOM class ----------------- #


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

    def listen(self):
        while True:
            client, address = self.server.accept()

            client2, address2 = self.server.accept()

            rooms.append(room())
            rooms[-1].get_clients(client, client2)

    # ----------------- SERVER main ----------------- #


class room:

    def __init__(self):

        self.board = ['-', '-', '-',
                      '-', '-', '-',
                      '-', '-', '-']
        self.position = '.'
        self.chance, self.next_chance = 'X', 'O'
        self.connections = []
        self.players = []

    # return the piece(X,O) that a player will be assigned to.
    # def get_playerTag(self):
    #     if 'X' in self.players:
    #         return 'O'
    #     elif 'O' in self.players:
    #         return 'X'
    #     else:
    #         return choice(['X', 'O'])

    # used to update a local variable in the handle client method
    def update_game_situ(self, player):
        if self.position == player:
            return 'WON'
        elif self.position == '-':
            return 'DRAW'
        elif self.position != '.':
            return 'LOST'

        return '.'

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

    def get_clients(self, c1, c2):

        c1.send('X'.encode('utf-8'))
        Thread(target=self.handle_client, args=(c1, 'X')).start()

        c2.send('O'.encode('utf-8'))
        Thread(target=self.handle_client, args=(c2, 'O')).start()

    # handles a single time, ran on a separate thread
    def handle_client(self, client, player):

        # used to disconnect a client from the server
        def disconnect():

            if client in self.connections and player in self.players:
                self.connections.remove(client)
                self.players.remove(player)
            self.reset_board()
            self.chance, self.next_chance = 'X', 'O'

        def send_message(message):
            try:
                client.send(message.encode('utf-8'))
                return True
            except ConnectionResetError:
                disconnect()
                return False

        connected = True
        game_situ = '.'
        # the main game loop
        while connected and game_situ == '.':
            if self.position == '.':
                self.position = check_game_pos(self.board)
                game_situ = self.update_game_situ(player)

            if self.chance == player:

                send_message(f'{encrypt(self.board)}___{game_situ}')

                try:
                    n = int(client.recv(4).decode('utf-8'))
                except ConnectionResetError or ConnectionAbortedError or ValueError:
                    disconnect()
                    break

                self.board[n - 1] = player

                if self.position == '.':
                    self.position = check_game_pos(self.board)
                    game_situ = self.update_game_situ(player)

                connected = send_message(f'{encrypt(self.board)}___{game_situ}')

                self.chance, self.next_chance = self.next_chance, self.chance
        self.position = check_game_pos(self.board)
        game_situ = self.update_game_situ(player)
        send_message(f'{encrypt(self.board)}___{game_situ}')


Server().listen()
