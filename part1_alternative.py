# Group#: G12
# Student Names: Julia Wadey, Nikoo Vali, Sara Hematy

# Global constants
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 300
SNAKE_ICON_WIDTH = 15
PREY_ICON_WIDTH = 10  # Ensure this constant is defined globally

BACKGROUND_COLOUR = "green"
ICON_COLOUR = "yellow"
"""
    This program implements a variety of the snake 
    game (https://en.wikipedia.org/wiki/Snake_(video_game_genre))

    Instead of using queueing like in part 1, part 1 alternative uses an event handler instead. Shared data 
    is stored in a dictionary seperate from the events, each task is an event created by threading.Event()
"""

import threading
#import queue 

from tkinter import Tk, Canvas, Button
import random, time

class Gui():
    """
        This class takes care of the game's graphic user interface (gui)
        creation and termination.
    """
    def __init__(self, event_handler):
        """        
            The initializer instantiates the main window and 
            creates the starting icons for the snake and the prey,
            and displays the initial gamer score.
        """
        #some GUI constants
        scoreTextXLocation = 60
        scoreTextYLocation = 15
        textColour = "white"

        self.event_handler = event_handler

        #instantiate and create gui
        self.root = Tk()
        self.canvas = Canvas(self.root, width = WINDOW_WIDTH, 
            height = WINDOW_HEIGHT, bg = BACKGROUND_COLOUR)
        self.canvas.pack()
        #create starting game icons for snake and the prey
        self.snakeIcon = self.canvas.create_line(
            (0, 0), (0, 0), fill=ICON_COLOUR, width=SNAKE_ICON_WIDTH)
        self.preyIcon = self.canvas.create_rectangle(
            0, 0, 0, 0, fill=ICON_COLOUR, outline=ICON_COLOUR)
        #display starting score of 0
        self.score = self.canvas.create_text(
            scoreTextXLocation, scoreTextYLocation, fill=textColour, 
            text='Your Score: 0', font=("Helvetica","11","bold"))
        #binding the arrow keys to be able to control the snake
        for key in ("Left", "Right", "Up", "Down"):
            self.root.bind(f"<Key-{key}>", game.whenAnArrowKeyIsPressed)

        # Thread for the event handler
        threading.Thread(target=self.event_handler_loop, daemon=True).start()

    # Updates gui according to eventHandler
    def event_handler_loop(self):
        while True:
            if self.event_handler.move_event.is_set():
                data = self.event_handler.get_task_data("move")
                points = [x for point in data for x in point]
                self.canvas.coords(self.snakeIcon, *points)
                self.event_handler.clear_event(self.event_handler.move_event)

            if self.event_handler.prey_event.is_set():
                data = self.event_handler.get_task_data("prey")
                self.canvas.coords(self.preyIcon, *data)
                self.event_handler.clear_event(self.event_handler.prey_event)

            if self.event_handler.score_event.is_set():
                data = self.event_handler.get_task_data("score")
                self.canvas.itemconfigure(self.score, text=f"Your Score: {data}")
                self.event_handler.clear_event(self.event_handler.score_event)

            if self.event_handler.game_over_event.is_set():
                self.gameOver()
                self.event_handler.clear_event(self.event_handler.game_over_event)

            time.sleep(0.05)

    def gameOver(self):
        """
            This method is used at the end to display a
            game over button.
        """
        gameOverButton = Button(self.canvas, text="Game Over!", 
            height = 3, width = 10, font=("Helvetica","14","bold"), 
            command=self.root.destroy)
        self.canvas.create_window(200, 100, anchor="nw", window=gameOverButton)
    

class EventHandler:
    def __init__(self):
        # Define events
        self.move_event = threading.Event()
        self.prey_event = threading.Event()
        self.score_event = threading.Event()
        self.game_over_event = threading.Event()
        
        # Lock for shared data
        self.lock = threading.Lock()
        
        # Shared data
        self.shared_data = {}

    def set_task(self, event_type, data=None):
        with self.lock:
            self.shared_data[event_type] = data
        if event_type == "move":
            self.move_event.set()
        elif event_type == "prey":
            self.prey_event.set()
        elif event_type == "score":
            self.score_event.set()
        elif event_type == "game_over":
            self.game_over_event.set()

    # Gets data for task
    def get_task_data(self, event_type):
        with self.lock:
            return self.shared_data.get(event_type, None)

    # Resets
    def clear_event(self, event):
        event.clear()


class Game():
    '''
        This class implements most of the game functionalities.
    '''
    def __init__(self, event_handler):
        """
           This initializer sets the initial snake coordinate list, movement
           direction, and arranges for the first prey to be created.
        """
        # self.queue = gameQueue
        self.event_handler = event_handler
        self.score = 0
        #starting length and location of the snake
        #note that it is a list of tuples, each being an
        # (x, y) tuple. Initially its size is 5 tuples.       
        self.snakeCoordinates = [(495, 55), (485, 55), (475, 55),
                                 (465, 55), (455, 55)]
        #initial direction of the snake
        self.direction = "Left"
        self.gameNotOver = True
        self.preyCoordinates = None  # Initialize prey coordinates
        self.createNewPrey()
        
    def superloop(self) -> None:
        """
            This method implements a main loop
            of the game. It constantly generates "move" 
            tasks to cause the constant movement of the snake.
            Use the SPEED constant to set how often the move tasks
            are generated.
        """
        SPEED = 0.15     #speed of snake updates (sec)
        while self.gameNotOver:
            self.move()
            time.sleep(SPEED)

    def whenAnArrowKeyIsPressed(self, e) -> None:
        """ 
            This method is bound to the arrow keys
            and is called when one of those is clicked.
            It sets the movement direction based on 
            the key that was pressed by the gamer.
            Use as is.
        """
        currentDirection = self.direction
        #ignore invalid keys
        if (currentDirection == "Left" and e.keysym == "Right" or 
            currentDirection == "Right" and e.keysym == "Left" or
            currentDirection == "Up" and e.keysym == "Down" or
            currentDirection == "Down" and e.keysym == "Up"):
            return
        self.direction = e.keysym

    def move(self) -> None:
        """ 
            This method implements what is needed to be done
            for the movement of the snake.
            It generates a new snake coordinate. 
            If based on this new movement, the prey has been 
            captured, it adds a task to the queue for the updated
            score and also creates a new prey.
            It also calls a corresponding method to check if 
            the game should be over. 
            The snake coordinates list (representing its length 
            and position) should be correctly updated.
        """
        # Calculate the new head coordinates
        NewSnakeCoordinates = self.calculateNewCoordinates()

        # Append the new coordinates to the snake's body
        self.snakeCoordinates.append(NewSnakeCoordinates)

        self.isGameOver(NewSnakeCoordinates)

        # Check if prey is captured
        preyLeft = self.preyCoordinates[0]
        preyTop = self.preyCoordinates[1]
        preyRight = self.preyCoordinates[2]
        preyBottom = self.preyCoordinates[3]

        # Get snake head, snake x and y coordinates are the midpoint of the line
        snakeX = NewSnakeCoordinates[0]
        snakeY = NewSnakeCoordinates[1]
        snakeLeft = snakeX - SNAKE_ICON_WIDTH / 2
        snakeRight = snakeX + SNAKE_ICON_WIDTH / 2
        snakeTop = snakeY - SNAKE_ICON_WIDTH / 2
        snakeBottom = snakeY + SNAKE_ICON_WIDTH / 2

        #if preyCoordinatesX <= NewSnakeCoordinates[0] <= preyCoordinatesX + PREY_ICON_WIDTH and preyCoordinatesY <= NewSnakeCoordinates[1] <= preyCoordinatesY + PREY_ICON_WIDTH:
        if (snakeLeft < preyRight and snakeRight > preyLeft and snakeTop < preyBottom and
           snakeBottom > preyTop):
            self.score += 1
            # Create a new prey
            self.createNewPrey()
            # self.queue.put({"score": self.score}), Sends the task to the event handler
            self.event_handler.set_task("score", self.score)

        else:
            # Remove the tail if no prey is captured
            self.snakeCoordinates.pop(0)

        self.event_handler.set_task("move", self.snakeCoordinates)

    def calculateNewCoordinates(self) -> tuple:
        """
            This method calculates and returns the new 
            coordinates to be added to the snake
            coordinates list based on the movement
            direction and the current coordinate of 
            the head of the snake.
        """
        # Get the current head position
        headX, headY = self.snakeCoordinates[-1]  # Initialize headX and headY from the snake's current head

        # Update the head coordinates based on the direction
        if self.direction == "Left":
            headX -= SNAKE_ICON_WIDTH
        elif self.direction == "Right":
            headX += SNAKE_ICON_WIDTH
        elif self.direction == "Up":
            headY -= SNAKE_ICON_WIDTH
        elif self.direction == "Down":
            headY += SNAKE_ICON_WIDTH
        
        newCoords = (headX, headY)

        # Return the updated head coordinates
        return newCoords

    def isGameOver(self, snakeCoordinates) -> None:
        """
            This method checks if the game is over by 
            checking if now the snake has passed any wall
            or if it has bit itself.
            If that is the case, it updates the gameNotOver 
            field and also adds a "game_over" task to the queue. 
        """
        x, y = snakeCoordinates
        # Check wall collisions
        if x < 0 or x > WINDOW_WIDTH or y < 0 or y > WINDOW_HEIGHT:
            self.gameNotOver = False
            # self.queue.put({"game_over": True})
            self.event_handler.set_task("game_over")
            return

        # Check self-collision
        if snakeCoordinates in self.snakeCoordinates[:-1]:
            self.gameNotOver = False
            self.event_handler.set_task("game_over")

    def createNewPrey(self) -> None:
        """ 
            This methods picks an x and a y randomly as the coordinate 
            of the new prey and uses that to calculate the 
            coordinates (x - 5, y - 5, x + 5, y + 5). [you need to replace 5 with a constant]
            It then adds a "prey" task to the queue with the calculated
            rectangle coordinates as its value. This is used by the 
            queue handler to represent the new prey.                    
            To make playing the game easier, set the x and y to be THRESHOLD
            away from the walls. 
        """
        THRESHOLD = 15   
        x = random.randint(THRESHOLD, WINDOW_WIDTH - THRESHOLD - PREY_ICON_WIDTH)
        y = random.randint(THRESHOLD, WINDOW_HEIGHT - THRESHOLD - PREY_ICON_WIDTH)

        prey_coordinates = (x, y, x + PREY_ICON_WIDTH, y + PREY_ICON_WIDTH)
   
        self.preyCoordinates = prey_coordinates
        # self.queue.put({"prey": prey_coordinates})  
        self.event_handler.set_task("prey", prey_coordinates)

if __name__ == "__main__":
    #some constants for our GUI
    WINDOW_WIDTH = 500           
    WINDOW_HEIGHT = 300 
    SNAKE_ICON_WIDTH = 15
    #add the specified constant PREY_ICON_WIDTH here     
    PREY_ICON_WIDTH = 10

    BACKGROUND_COLOUR = "green"   #you may change this colour if you wish
    ICON_COLOUR = "yellow"        #you may change this colour if you wish

    # gameQueue = queue.Queue()     #instantiate a queue object using python's queue class
    
    event_handler = EventHandler() # Instantiate event handler

    game = Game(event_handler)        #instantiate the game object

    gui = Gui(event_handler)    #instantiate the game user interface
    
    # QueueHandler()  #instantiate the queue handler    
    
    #start a thread with the main loop of the game
    threading.Thread(target = game.superloop, daemon=True).start()

    #start the GUI's own event loop
    gui.root.mainloop()