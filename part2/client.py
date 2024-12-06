from tkinter import *
import socket
import threading

class ChatClient:

    def __init__(self, window: Tk):
        self.window = window
        self.window.title("Client Chat")

        # Create a socket
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #Initializes client ID
        self.client_id = None

        try:
            self.clientSocket.connect(('127.0.0.1', 12345))
            self.client_port = self.clientSocket.getsockname()[1]  # Get the client's port
            #self.client_name = self.clientSocket.recv(1024).decode()  

            print(f"Connection Successful. Client is using port {self.client_port}")
        except socket.error as e:
            print(f"Connection failed: {e}")
            self.client_port = "N/A"  # Fallback in case of failure

        # Title label for client info
        Label(self.window, text=f"Client @ port#{self.client_port}").grid(row=0, column=1)

        # Chat message label and entry
        Label(self.window, text="Chat message").grid(row=1, column=1)
        self.client_entry = Entry(self.window)
        self.client_entry.grid(row=1, column=2, padx=5, pady=5)

        # Chat history label and text box
        Label(self.window, text="Chat History").grid(row=2, column=1)
        self.chat_frame = Frame(self.window)
        self.chat_history = Text(self.chat_frame, wrap="word", height=20, width=50, state="disabled")
        self.chat_history.pack(side="left", fill="both", expand=True)

        #scrollbar = Scrollbar(self.chat_frame, command=self.chat_history.yview)
        #scrollbar.pack(side="right", fill="y")
        #self.chat_history.config(yscrollcommand=scrollbar.set)
        self.chat_frame.grid(row=2, column=0, columnspan=3, padx=5, pady=5)

        # Bind entry box to send message on Enter key
        self.client_entry.bind("<Return>", self.send_message)

        # Start thread to receive messages
        threading.Thread(target=self.receive_message, daemon=True).start()

    def send_message(self, event=None):
        new_message = self.client_entry.get()
        if new_message.strip():
            self.clientSocket.send(new_message.encode())
            self.update_chat_history(f"{new_message}", align="right")
            self.client_entry.delete(0, END)

    def receive_message(self):
        while True:
            try:
                server_message = self.clientSocket.recv(1024).decode()
                if server_message:
                    self.window.after(0, self.update_chat_history, server_message)
            except (ConnectionResetError, BrokenPipeError): #check if code is necessary
                break

    def update_chat_history(self, message, align="left"):
        self.chat_history.config(state="normal")
        if align == "left":
            self.chat_history.insert(END, f"{message.rjust(25)}\n", "right")
        else:
            self.chat_history.insert(END, f"{message}\n", "left")
            self.chat_history.config(state="disabled")
            self.chat_history.see(END)

def main():
    window = Tk()
    ChatClient(window)
    window.mainloop()

if __name__ == '__main__':
    main()

    

