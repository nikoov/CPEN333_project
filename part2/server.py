# Group#: 12
# Student Names: Sara Hematy, Nikoo Ghasemkhanvali Vali, Julia Wadey

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
        """It initialzes the server GUI recreating client chat history between clients.
           It also starts the server socket to listen for connections"""
        
        self.window = window
        self.window.title("Chat Server")

        #creates label for chat history section
        Label(self.window, text = "Chat History:").grid(row=0,column=0)
        
        #creates frame and text widget for chat history display
        self.chat_frame = Frame(self.window)
        self.chat_history = Text(self.chat_frame, wrap="word", height=20, width=50, state="disabled")
        self.chat_history.pack(side="left", fill="both", expand=True)

        #creates scrollbar for chat history
        scrollbar = Scrollbar(self.chat_frame, command=self.chat_history.yview)
        scrollbar.pack(side="right", fill="y")
        self.chat_history.config(yscrollcommand=scrollbar.set)

        self.chat_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        #create a scoket
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #binds socket to address
        self.serverSocket.bind(('127.0.0.1',12345)) 
        #enables server to accept connection
        self.serverSocket.listen() 

        
        self.clients_list = {} #list of total clients chatting
        self.client_counter = 0  #keeps track of number of unique clients variable

        #starts thread to accept connections
        threading.Thread(target=self.accept_client_connection, daemon=True).start() 

    def accept_client_connection(self):
        """ It creates the connection between a client and server to start sending and receiving messages.
            It assigns each client a unique id and starts thread to handle their messages."""
        while True:
            client_socket, addr = self.serverSocket.accept() #accepts connection
     
            self.client_counter += 1 #adds a new client to the number of clients
            client_id = f"Client {self.client_counter}" #assigns number to client for id purposes
            
            client_socket.send(client_id.encode()) # Send client their unique ID 

            self.clients_list[client_socket] = client_id #add client to list of active connections

            threading.Thread(target=self.receive_message, args=(client_socket,), daemon=True).start() #start new thread to handle messages from this client


    def receive_message(self, client_socket):
         """It handles messages received from client and broadcasts message to all other clients.
            It also deals with client disconnections"""
         client_id = self.clients_list[client_socket]
         while True:
            try:
                #receive and decode message
                client_message = client_socket.recv(1024).decode()
                if client_message:
                    #format message and dispaly it in the chat history
                    full_message = f"{client_id}: {client_message}"
                    self.chat_history.config(state = "normal")
                    self.chat_history.insert(END, f"{full_message}\n" )
                    self.chat_history.config(state = "disabled")
                    self.chat_history.see(END)

                    self.broadcast(full_message, client_socket) #broadcasts message to the other clients
            
            #Handles any client disconnections
            except (ConnectionResetError, BrokenPipeError): 
                disconnected_client = self.clients_list.pop(client_socket, "Unknown")
                disconnect_message = f"{disconnected_client} has left the chat."
            
                # Display disconnection message on server
                self.chat_history.config(state="normal")
                self.chat_history.insert(END, f"{disconnect_message}\n")
                self.chat_history.config(state="disabled")
                self.chat_history.see(END)

                # Notifies other clients about disconnection
                self.broadcast(disconnect_message, client_socket)
                break

    def broadcast(self, message, sender_socket=None):
        """ server broadcasts message to the other clients excluding the sender """
        for client_socket in self.clients_list:
            if client_socket != sender_socket:  #makes sure the sender does not receive the message again
                try:
                    client_socket.send(message.encode())
                except (ConnectionResetError, BrokenPipeError):
                    # Handles disconnection during broadcasting
                    disconnected_client = self.clients_list.pop(client_socket, "Unknown")
                    disconnect_message = f"{disconnected_client} has left the chat."
                    self.broadcast(disconnect_message)
                    self.remove_client(client_socket)

def main(): #Note that the main function is outside the ChatServer class
    window = Tk()
    ChatServer(window)
    window.mainloop()
    #May add more or modify, if needed

if __name__ == '__main__': # May be used ONLY for debugging
    main()
