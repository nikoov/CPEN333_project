# Group#: 12
# Student Names: Sara Hematy

#Content of server.py; To complete/implement

from tkinter import *
import socket
import threading

class ChatServer:
    """
    This class implements the chat server.
    It uses the socket module to create a TCP socket and act as the chat server.
    Each chat client connects to the server and sends chat messages to it. When 
    the server receives a message, it displays it in its own GUI and also sents 
    the message to the other client.  
    It uses the tkinter module to create the GUI for the server client.
    See the project info/video for the specs.
    """
    # To implement 
    def __init__(self, window: Tk):
        self.window = window
        self.window.title("Chat Server")

        Label(self.window, text = "Chat History:").grid(row=0,column=0)
        
        self.chat_frame = Frame(self.window)
        self.chat_history = Text(self.chat_frame, wrap="word", height=20, width=50, state="disabled")
        self.chat_history.pack(side="left", fill="both", expand=True)

        #scrollbar = Scrollbar(self.chat_frame, command=self.chat_history.yview)
        #scrollbar.pack(side="right", fill="y")

        #self.chat_history.config(yscrollcommand=scrollbar.set)

        self.chat_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.serverSocket.bind(('127.0.0.1',12345)) 
        self.serverSocket.listen(3) #why 3

        self.clients_list = {}
        self.client_counter = 0  # Counter for unique client IDs

        threading.Thread(target=self.accept_client_connection, daemon=True).start() 

    def accept_client_connection(self):
        while True:
            client_socket, addr = self.serverSocket.accept()
            # Assign a unique client ID
            self.client_counter += 1
            client_id = f"Client {self.client_counter}"
            self.clients_list[client_socket] = client_id

            threading.Thread(target=self.receive_message, args=(client_socket,), daemon=True).start()


    def receive_message(self, client_socket):
         client_id = self.clients_list[client_socket]
         while True:
            try:
                client_message = client_socket.recv(1024).decode()
                if client_message:

                    full_message = f"{client_id}: {client_message}"
                    
                    self.chat_history.config(state = "normal")
                    self.chat_history.insert(END, f"{full_message}\n" )
                    self.chat_history.config(state = "disabled")
                    self.chat_history.see(END)

                    self.broadcast(client_message, client_socket)
            
            except (ConnectionResetError, BrokenPipeError): #check
                client_id = self.clients_list.pop(client_socket, "Unknown")
                

    def broadcast(self, message, sender_socket=None):
        for client_socket in self.clients_list:
            if client_socket != sender_socket:  # Skip the sender
                try:
                    client_socket.send(message.encode())
                except (ConnectionResetError, BrokenPipeError):
                    client_id = self.clients_list.pop(client_socket, "Unknown") #check

def main(): #Note that the main function is outside the ChatServer class
    window = Tk()
    ChatServer(window)
    window.mainloop()
    #May add more or modify, if needed

if __name__ == '__main__': # May be used ONLY for debugging
    main()
