# Group#: 12
# Student Names: Sara Hematy, Nikoo Ghasemkhanvali Vali, Julia Wadey

#Content of client.py; to complete/implement

from tkinter import *
import socket
import threading

class ChatClient:

    def __init__(self, window: Tk):
        """It initialzes the client GUI recreating client chat history between clients
           and providing entry point for message to be sent. 
           It also starts server connection."""
        
        self.window = window
        self.window.title("Client Chat")

        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create a socket

        self.client_id = None #initialize client id variable to be received by server

        try:
            self.clientSocket.connect(('127.0.0.1', 12345)) #connects at host on port 12345
            self.client_id = self.clientSocket.recv(1024).decode()  # Receive the client ID from the server
            self.client_port = self.clientSocket.getsockname()[1]  # Get client's port number
        #Handles any connection errors
        except socket.error as e:
            print(f"Connection failed: {e}") 

        Label(self.window, text=f"Client @ port#{self.client_port}").grid(row=0, column=0) # creates label for client port number

        # creates chat message label and entry
        Label(self.window, text="Chat message").grid(row=1, column=0)
        self.client_entry = Entry(self.window)
        self.client_entry.grid(row=1, column=1, padx=5, pady=5)

        # creates chat history label and formats
        Label(self.window, text="Chat History").grid(row=2, column=0)
        self.chat_frame = Frame(self.window)
        self.chat_history = Text(self.chat_frame, wrap="word", height=20, width=50, state="disabled")
        self.chat_history.pack(side="left", fill="both", expand=True)

        # Helps with text alignment (right shift for received messages and left for sent messages)
        self.chat_history.tag_configure("left", justify="left", lmargin1=200, lmargin2=200)
        self.chat_history.tag_configure("right", justify="right", rmargin=200)

        #creates a scrollbar for chat history
        scrollbar = Scrollbar(self.chat_frame, command=self.chat_history.yview)
        scrollbar.pack(side="right", fill="y")
        self.chat_history.config(yscrollcommand=scrollbar.set)

        self.chat_frame.grid(row=3, column=0, columnspan=3, padx=5, pady=5)

        self.client_entry.bind("<Return>", self.send_message)# binds enter key to when message is sent 

        threading.Thread(target=self.receive_message, daemon=True).start() # Start thread handle messages coming in from the server 

    def send_message(self, event=None):
        """ It sends messages to the server and also displayed in the client's chat history if valid."""
        new_message = self.client_entry.get()
        if new_message.strip():
            self.clientSocket.send(new_message.encode()) #sends message to server
            self.update_chat_history(f"{self.client_id}: {new_message}", align="center") #displays the sent message 
            self.client_entry.delete(0, END) #clears box for entries 

    def receive_message(self):
        """Listens for incoming messages from the server and updates chat history if new message is received """
        while True:
            try:
                server_message = self.clientSocket.recv(1024).decode() #receives message from server
                if server_message:
                    self.window.after(0, self.update_chat_history, f"{server_message}", "left") #updates chat 
            #Handles error by exiting loop if server disconnects or another connection error occurs 
            except (ConnectionResetError, BrokenPipeError): 
                break

    def update_chat_history(self, message, align="left"):
        """updates chat history display with a new message"""
        self.chat_history.config(state="normal")
        self.chat_history.insert(END, f"{message}\n", align) #add the new message
        self.chat_history.config(state="disabled")
        self.chat_history.see(END)

def main():
    window = Tk()
    ChatClient(window)
    window.mainloop()

if __name__ == '__main__':
    main()

    
