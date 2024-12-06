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
PREY_ICON_WIDTH = 15  # Match snake width for simpler collision detection
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

    def gameOver(self) -> None:
        gameOverButton = Button(self.canvas, text="Game Over!", 
                                height=3, width=10, font=("Helvetica", "14", "bold"), 
                                command=self.root.destroy)
        self.canvas.create_window(200, 100, anchor="nw", window=gameOverButton)


class QueueHandler:
    def __init__(self) -> None:
        self.queue = gameQueue
        self.gui = gui
        self.queueHandler()
    
    def queueHandler(self) -> None:
        try:
            while True:
                task = self.queue.get_nowait()
                if "game_over" in task:
                    self.gui.gameOver()
                elif "move" in task:
                    points = [x for point in task["move"] for x in point]
                    self.gui.canvas.coords(self.gui.snakeIcon, *points)
                elif "prey" in task:
                    self.gui.canvas.coords(self.gui.preyIcon, *task["prey"])
                elif "score" in task:
                    self.gui.canvas.itemconfigure(self.gui.score, text=f"Your Score: {task['score']}")
                self.queue.task_done()
        except queue.Empty:
            self.gui.root.after(100, self.queueHandler)


class Game:
    def __init__(self) -> None:
        self.queue: queue.Queue = gameQueue
        self.score: int = 0
        # Starting snake coordinates (treat these as centers of each segment)
        self.snakeCoordinates: List[Tuple[int,int]] = [(495, 55), (480, 55), (465, 55), (450, 55), (435, 55)]
        self.direction: str = "Left"
        self.gameNotOver: bool = True
        self.preyCoordinates: Tuple[int,int,int,int] = (0,0,0,0)
        self.createNewPrey()

    def superloop(self) -> None:
        SPEED = 0.15
        while self.gameNotOver:
            self.move()
            time.sleep(SPEED)

    def whenAnArrowKeyIsPressed(self, e: Event) -> None:
        currentDirection = self.direction
        # Prevent reverse direction
        if (currentDirection == "Left" and e.keysym == "Right" or 
            currentDirection == "Right" and e.keysym == "Left" or
            currentDirection == "Up" and e.keysym == "Down" or
            currentDirection == "Down" and e.keysym == "Up"):
            return
        self.direction = e.keysym

    def move(self) -> None:
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
        # Prey and snake are the same size now
        half_prey = PREY_ICON_WIDTH // 2
        THRESHOLD = 15
        while True:
            px = random.randint(THRESHOLD + half_prey, WINDOW_WIDTH - THRESHOLD - half_prey)
            py = random.randint(THRESHOLD + half_prey, WINDOW_HEIGHT - THRESHOLD - half_prey)

            # Ensure no overlap with snake
            # Since both snake and prey are the same size and we treat them as centers,
            # just check if any snake segment center is too close to (px, py).
            # We can require exact non-overlap by checking distance or bounding boxes.
            overlap = any(
                abs(segmentX - px) < PREY_ICON_WIDTH and abs(segmentY - py) < PREY_ICON_WIDTH 
                for segmentX, segmentY in self.snakeCoordinates
            )
            if not overlap:
                # Prey coordinates as a box
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
        if sx1 < px2 and sx2 > px1 and sy1 < py2 and sy2 > py1:
            return True
        return False


if __name__ == "__main__":
    gameQueue = queue.Queue()
    game = Game()
    gui = Gui()
    QueueHandler()

    # Start game loop in separate thread
    threading.Thread(target=game.superloop, daemon=True).start()

    # Start GUI loop
    gui.root.mainloop()

