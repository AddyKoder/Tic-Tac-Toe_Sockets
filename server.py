import socket
from random import choice
from threading import Thread

# ----------------- VARIABLES ----------------- #

chance = 'X'
next_chance = 'O'

# game position  '.' : going     '-' : Draw     'X'/'O' : winner x/o
position = '.'

board = ['-', '-', '-',
         '-', '-', '-',
         '-', '-', '-']

connections = []
players = []


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


# return the piece(X,O) that a player will be assigned to.
def get_playerTag():
    if 'X' in players:
        return 'O'
    elif 'O' in players:
        return 'X'
    else:
        return choice(['X', 'O'])


# used to update a local variable in the handle client method
def update_game_situ(player):
    if position == player:
        return 'WON'
    elif position == '-':
        return 'DRAW'
    elif position != '.':
        return 'LOST'

    return '.'


def reset_board():
    global board
    board = ['-', '-', '-',
             '-', '-', '-',
             '-', '-', '-']

    # ----------------- SERVER main ----------------- #


class Server:

    # Initializes the sockets for use in the server
    def __init__(self):
        self.PORT = 8080

        self.IP = socket.gethostbyname(socket.gethostname())
        self.ADDRESS = (self.IP, self.PORT)

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.ADDRESS)

        self.server.listen()

    # start listening for connections
    def listen_connections(self):
        while True:
            if len(connections) < 2:
                player = get_playerTag()

                client, address = self.server.accept()
                client.send(player.encode('utf-8'))
                Thread(target=self.handle_client, args=(client, player)).start()

                connections.append(client)
                players.append(player)

    # handles a single time, ran on a separate thread
    @staticmethod
    def handle_client(client, player):
        global position, chance, next_chance

        # used to disconnect a client from the server
        def disconnect():
            global chance, next_chance

            if client in connections and player in players:
                connections.remove(client)
                players.remove(player)
            reset_board()
            chance, next_chance = 'X', 'O'

        def send_message(message):
            try:
                client.send(message.encode('utf-8'))
                return True
            except ConnectionResetError:
                disconnect()
                return False


        connected = True
        # the main game loop
        while connected:
            position = check_game_pos(board)
            game_situ = update_game_situ(player)

            if chance == player:

                send_message(f'{encrypt(board)}___{game_situ}')


                try:
                    n = int(client.recv(4).decode('utf-8'))
                except ConnectionResetError or ConnectionAbortedError or ValueError:
                    disconnect()
                    break

                board[n-1] = player

                position = check_game_pos(board)
                game_situ = update_game_situ(player)

                connected = send_message(f'{encrypt(board)}___{game_situ}')

                chance, next_chance = next_chance, chance


Server().listen_connections()
