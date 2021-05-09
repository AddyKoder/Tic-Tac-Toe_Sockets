# IMPORTING STUFF
import socket
from threading import Thread
from tkinter import *

# ----------------- VARIABLES ----------------- #

board = ['-', '-', '-',
         '-', '-', '-',
         '-', '-', '-']

buttons = []
conn = socket.socket()


# ----------------- METHODS ----------------- #


# change the board string to a python list
def decrypt(b):
    board_list = []
    for i in b:
        board_list.append(i)

    return board_list


# Initializes the sockets for use to communicate with the server
def initialize_sockets():
    global conn
    port = 8080

    ip = socket.gethostbyname(socket.gethostname())

    address = (ip, port)

    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect(address)


def receive_board():
    global board

    b = conn.recv(64).decode('utf-8').split('___')
    board = decrypt(b[0])
    my_gui.update_gui()
    my_gui.show_result(b[1])


# the main method which take cares of the connections with the server
# and sends and receives data
def main():
    initialize_sockets()
    my_gui.window.title(f'Playing as :{conn.recv(64).decode("utf-8")}')

    while True:
        # receives the board from server and updates the local
        # board variable and the gui
        receive_board()

        # Enables the gui buttons so the user can make the chance
        # are automatically disabled after made the chance
        my_gui.enable_buttons()

        # again receive the board which includes the chance made by
        # us in the previous chance
        receive_board()


# ----------------- GUI CLASS ----------------- #

class gui:

    def __init__(self):
        self.buttons = []
        self.methods = []
        self.window = Tk()
        self.f1, self.f2, self.f3 = Frame(self.window), Frame(self.window), Frame(self.window)

    def start(self):

        self.window.geometry('500x500')

        self.setup_gui()
        self.window.mainloop()

    def setup_gui(self):

        def get_methods(n):
            def on_click():
                if board[n] == '-':
                    conn.send(str(n + 1).encode('utf-8'))
                    self.disable_buttons()

            return on_click

        start, end = 0, 3
        for frame in (self.f1, self.f2, self.f3):
            for i in range(start, end):
                self.buttons.append(
                    Button(frame, text=board[i], font='arial 50', state=DISABLED, command=get_methods(i)))
            start += 3
            end += 3

        for button in self.buttons:
            button.pack(side=LEFT, fill=BOTH, expand=1)
        for frame in (self.f1, self.f2, self.f3):
            frame.pack(side=TOP, fill=BOTH, expand=1)

    def update_gui(self):
        for ind, button in enumerate(self.buttons):
            button.configure(text=board[ind])
            button.update()

    def enable_buttons(self):
        for button in self.buttons:
            button.configure(state=NORMAL)
            button.update()

    def disable_buttons(self):
        for button in self.buttons:
            button.configure(state=DISABLED)
            button.update()

    def show_result(self, result):
        if result != '.':
            self.buttons[4].configure(text=result)
            self.buttons[4].update()


my_gui = gui()
Thread(target=main).start()
my_gui.start()
