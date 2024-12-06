# Group#: GP-12
# Student Names: Nikoo Vali , Sara Hematy , Julia Wadey

import threading
import queue
from tkinter import Tk, Canvas, Button, Event
import random, time
from typing import Tuple, List

# Global constants
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 300
SNAKE_ICON_WIDTH = 15
PREY_ICON_WIDTH = 15  
BACKGROUND_COLOUR = "green"
ICON_COLOUR = "yellow"

class Gui:
    def __init__(self) -> None:
        scoreTextXLocation = 60
        scoreTextYLocation = 15
        textColour = "white"

        self.root = Tk()
        self.canvas = Canvas(self.root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg=BACKGROUND_COLOUR)
        self.canvas.pack()

        # Create snake and prey icons
        self.snakeIcon = self.canvas.create_line((0,0), (0,0), fill=ICON_COLOUR, width=SNAKE_ICON_WIDTH)
        self.preyIcon = self.canvas.create_rectangle(0,0,0,0, fill=ICON_COLOUR, outline=ICON_COLOUR)

        # Initial score display
        self.score = self.canvas.create_text(
            scoreTextXLocation, scoreTextYLocation, fill=textColour, 
            text='Your Score: 0', font=("Helvetica", "11", "bold")
        )

        # Bind arrow keys
        for key in ("Left", "Right", "Up", "Down"):
            self.root.bind(f"<Key-{key}>", game.whenAnArrowKeyIsPressed)

    #Game over button, by clicking it you exit the game
    def gameOver(self) -> None:
        gameOverButton = Button(self.canvas, text="Game Over!", 
                                height=3, width=10, font=("Helvetica", "14", "bold"), 
                                command=self.root.destroy)
        self.canvas.create_window(200, 100, anchor="nw", window=gameOverButton)


class QueueHandler:
    """
        This class implements the queue handler for the game.
    """
    def __init__(self) -> None:
        self.queue = gameQueue
        self.gui = gui
        self.queueHandler()
        
        '''
            This method handles the queue by constantly retrieving
            tasks from it and accordingly taking the corresponding
            action.
            A task could be: game_over, move, prey, score.
            Each item in the queue is a dictionary whose key is
            the task type (for example, "move") and its value is
            the corresponding task value.
            If the queue.empty exception happens, it schedules 
            to call itself after a short delay.
        '''
    
    def queueHandler(self) -> None:
        """
        Continuously processes tasks from the game's shared queue.
        This method attempts to retrieve and handle pending tasks such as:
        - game_over: Signal that the game has ended and display the Game Over button.
        - move: Update the snake's position on the canvas based on the latest snake coordinates.
        - prey: Move the prey icon to its new coordinates.
        - score: Update the displayed score when the snake has eaten a prey.

        If the queue is empty, it schedules itself to run again after a short delay.
        This ensures that tasks are handled asynchronously as they are produced by 
        other threads (e.g., the game logic thread).
        """
        try:
            # Process tasks as long as there are items in the queue.
            while True:
                # Attempt to get the next task without waiting.
                task = self.queue.get_nowait()

                # Check the type of the task and handle it accordingly.
                if "game_over" in task:
                    self.gui.gameOver()
                elif "move" in task:
                    points = [x for point in task["move"] for x in point]
                    self.gui.canvas.coords(self.gui.snakeIcon, *points)
                elif "prey" in task:
                    self.gui.canvas.coords(self.gui.preyIcon, *task["prey"])
                elif "score" in task:
                    self.gui.canvas.itemconfigure(self.gui.score, text=f"Your Score: {task['score']}")

                # Mark the current task as completed.
                self.queue.task_done()

        except queue.Empty:
            # No tasks at the moment, re-check after 100ms.
            self.gui.root.after(100, self.queueHandler)


class Game:
    '''
        This class implements most of the game functionalities.
    '''
    def __init__(self) -> None:
        """
           This initializer sets the initial snake coordinate list, movement
           direction, and arranges for the first prey to be created.
        """
        self.queue: queue.Queue = gameQueue
        self.score: int = 0
        # Starting snake coordinates (treat these as centers of each segment)
        self.snakeCoordinates: List[Tuple[int,int]] = [(495, 55), (480, 55), (465, 55), (450, 55), (435, 55)]
        self.direction: str = "Left"
        self.gameNotOver: bool = True
        self.preyCoordinates: Tuple[int,int,int,int] = (0,0,0,0)
        self.createNewPrey()

    def superloop(self) -> None:
        """
            This method implements a main loop
            of the game. It constantly generates "move" 
            tasks to cause the constant movement of the snake.
            Use the SPEED constant to set how often the move tasks
            are generated.
        """
        SPEED = 0.15
        while self.gameNotOver:
            self.move()
            time.sleep(SPEED)

    def whenAnArrowKeyIsPressed(self, e: Event) -> None:
        """ 
            This method is bound to the arrow keys
            and is called when one of those is clicked.
            It sets the movement direction based on 
            the key that was pressed by the gamer.
            Use as is.
        """
        currentDirection = self.direction
        # Prevent reverse direction
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
        newHead = self.calculateNewCoordinates()
        self.snakeCoordinates.append(newHead)

        if self.checkPreyCollision(newHead):
            # Increase score
            self.score += 1
            self.queue.put({"score": self.score})

            # Create a new prey immediately
            self.createNewPrey()

            # Update snake position (so GUI reflects the longer snake)
            self.queue.put({"move": self.snakeCoordinates})
        else:
            # No prey captured, remove tail
            self.snakeCoordinates.pop(0)
            self.isGameOver(newHead)
            self.queue.put({"move": self.snakeCoordinates})

    def calculateNewCoordinates(self) -> Tuple[int,int]:
        """
            This method calculates and returns the new 
            coordinates to be added to the snake
            coordinates list based on the movement
            direction and the current coordinate of 
            head of the snake.
            It is used by the move() method.    
        """
        headX, headY = self.snakeCoordinates[-1]
        if self.direction == "Left":
            headX -= SNAKE_ICON_WIDTH
        elif self.direction == "Right":
            headX += SNAKE_ICON_WIDTH
        elif self.direction == "Up":
            headY -= SNAKE_ICON_WIDTH
        elif self.direction == "Down":
            headY += SNAKE_ICON_WIDTH
        return headX, headY

    def isGameOver(self, snakeCoordinates: Tuple[int,int]) -> None:
        """
            This method checks if the game is over by 
            checking if now the snake has passed any wall
            or if it has bit itself.
            If that is the case, it updates the gameNotOver 
            field and also adds a "game_over" task to the queue. 
        """
        x, y = snakeCoordinates
        # Check wall collision
        if x < 0 or x >= WINDOW_WIDTH or y < 0 or y >= WINDOW_HEIGHT:
            self.gameNotOver = False
            self.queue.put({"game_over": True})
            return
        # Check self collision
        if snakeCoordinates in self.snakeCoordinates[:-1]:
            self.gameNotOver = False
            self.queue.put({"game_over": True})

    def createNewPrey(self) -> None:
        """ 
            This method picks an x and a y randomly as the coordinate 
            of the new prey and uses that to calculate the 
            coordinates (x - 5, y - 5, x + 5, y + 5). [you need to replace 5 with a constant]
            It then adds a "prey" task to the queue with the calculated
            rectangle coordinates as its value. This is used by the 
            queue handler to represent the new prey.                    
            To make playing the game easier, set the x and y to be THRESHOLD
            away from the walls. 
        """
        half_prey = PREY_ICON_WIDTH // 2
        THRESHOLD = 15 
        while True:
            px = random.randint(THRESHOLD + half_prey, WINDOW_WIDTH - THRESHOLD - half_prey)
            py = random.randint(THRESHOLD + half_prey, WINDOW_HEIGHT - THRESHOLD - half_prey)

            overlap = any(
                abs(segmentX - px) < PREY_ICON_WIDTH and abs(segmentY - py) < PREY_ICON_WIDTH 
                for segmentX, segmentY in self.snakeCoordinates
            )
            if not overlap:
                self.preyCoordinates = (px - half_prey, py - half_prey, px + half_prey, py + half_prey)
                self.queue.put({"prey": self.preyCoordinates})
                break

    def checkPreyCollision(self, head: Tuple[int,int]) -> bool:
        headX, headY = head
        half_snake = SNAKE_ICON_WIDTH // 2
        # Snake box
        sx1, sy1 = headX - half_snake, headY - half_snake
        sx2, sy2 = headX + half_snake, headY + half_snake

        # Prey box
        px1, py1, px2, py2 = self.preyCoordinates

        # Check overlap
        return (sx1 < px2 and sx2 > px1 and sy1 < py2 and sy2 > py1)


if __name__ == "__main__":
    gameQueue = queue.Queue()
    game = Game()
    gui = Gui()
    QueueHandler()

    # Start game loop in separate thread
    threading.Thread(target=game.superloop, daemon=True).start()

    # Start GUI loop
    gui.root.mainloop()

