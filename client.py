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

playing = True


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


# def get_met(i, win):
#     def main():
#         conn.send(f'j___{i}'.encode('utf-8'))
#         win.destroy()
#
#     return main
#
#
# def create(win):
#     def temp():
#         conn.send(f'c___{enter.get()}'.encode('utf-8'))
#         win.destroy()
#
#     return temp


# the main method which take cares of the connections with the server
# and sends and receives data
def main():
    initialize_sockets()

    # rooms = conn.receive(1024).decode('utf-8').split('___')
    # print(rooms)
    # join_window = Tk()
    #
    # enter = Entry(join_window)
    # enter.pack()
    # create = Button(join_window, text='Create', command=create(join_window))
    # create.pack(fill=BOTH, expand=1)
    #
    # for i in rooms:
    #     Button(join_window, text=i, command=get_met(i, join_window)).pack()
    #
    # join_window.mainloop()

    # Sending a connections request to the server
    # 'r___<anything>' : join a random room
    # 'c___<room_name> : creates a room with name <room_name>
    # 'j___<room_name> : sears for a room with name <room_name> and joins if is present
    conn.send('j___new_room'.encode('utf-8'))

    # receiving the reply of the server
    # if can either be a 's' means successfully created/joined a room
    # or an error message like ['room not found', 'room already existed', 'room full']
    reply = conn.recv(64).decode('utf-8')

    if reply != 's':
        print(reply)
        exit()

    # setting the title of the window as the piece of the playing player
    my_gui.window.title(f'Playing as :{conn.recv(64).decode("utf-8")}')

    while playing:
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

    # initializing the variables
    def __init__(self):
        self.buttons = []
        self.methods = []
        self.window = Tk()
        self.f1, self.f2, self.f3 = Frame(self.window), Frame(self.window), Frame(self.window)

    # starts the event loop / main loop
    def start(self):

        self.window.geometry('500x500')
        self.setup_gui()
        self.window.mainloop()

    # setups the complete gui by placing buttons on the window
    def setup_gui(self):

        # this method returns a method based on the argument passed
        # used for the command which we have to give to the button
        # widget. n is the number of the button(0-8)
        def get_methods(n):
            def on_click():
                if board[n] == '-':
                    conn.send(str(n + 1).encode('utf-8'))
                    self.disable_buttons()

            return on_click

        # the button placing loop.
        # in this loop we plot the 9x9 matrix of buttons
        # using this loop. we create a button and assign a text equal
        # to the loop variable +1 and a command by using the above
        # get_methods function
        start, end = 0, 3
        for frame in (self.f1, self.f2, self.f3):
            for i in range(start, end):
                self.buttons.append(
                    Button(frame, text=board[i], font='arial 50', state=DISABLED, command=get_methods(i)))
            start += 3
            end += 3

        # packing all the buttons in the window
        for button in self.buttons:
            button.pack(side=LEFT, fill=BOTH, expand=1)
        # packing all the frames in the window
        for frame in (self.f1, self.f2, self.f3):
            frame.pack(side=TOP, fill=BOTH, expand=1)

    # this method is called after some changes are made to the board
    # it updates the text of the buttons
    def update_gui(self):
        for ind, button in enumerate(self.buttons):
            button.configure(text=board[ind])
            button.update()

    # enables the buttons for the user on the server request
    def enable_buttons(self):
        for button in self.buttons:
            button.configure(state=NORMAL)
            button.update()

    # after the user had made their chance this method is called to
    # disable the buttons
    def disable_buttons(self):
        for button in self.buttons:
            button.configure(state=DISABLED)
            button.update()

    # given an argument result
    # if result is other than '.'(game going on)
    # it prints the result on the button 5 of the 9x9 matrix
    # if the game is still going on it not does anything
    def show_result(self, result):
        global playing
        if result != '.':
            self.buttons[4].configure(text=result)
            self.buttons[4].update()
            playing = False


if __name__ == '__main__':
    # instantiating the gui class to call the constructor
    my_gui = gui()

    # starting the main method thread so it can run concurrently
    Thread(target=main).start()

    # starting the gui to come into the even loop with the main
    # method running concurrently
    my_gui.start()
