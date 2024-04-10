"""
The turtle_adventure module maintains all classes related to the Turtle's
adventure game.
"""
from math import cos, sin, radians, degrees, atan2
from random import randint
from turtle import RawTurtle
from gamelib import Game, GameElement


class TurtleGameElement(GameElement):
    """
    An abstract class representing all game elemnets related to the Turtle's
    Adventure game
    """

    def __init__(self, game: "TurtleAdventureGame"):
        super().__init__(game)
        self.__game: "TurtleAdventureGame" = game

    @property
    def game(self) -> "TurtleAdventureGame":
        """
        Get reference to the associated TurtleAnvengerGame instance
        """
        return self.__game


class Waypoint(TurtleGameElement):
    """
    Represent the waypoint to which the player will move.
    """

    def __init__(self, game: "TurtleAdventureGame"):
        super().__init__(game)
        self.__id1: int
        self.__id2: int
        self.__active: bool = False

    def create(self) -> None:
        self.__id1 = self.canvas.create_line(0, 0, 0, 0, width=2, fill="green")
        self.__id2 = self.canvas.create_line(0, 0, 0, 0, width=2, fill="green")

    def delete(self) -> None:
        self.canvas.delete(self.__id1)
        self.canvas.delete(self.__id2)

    def update(self) -> None:
        # there is nothing to update because a waypoint is fixed
        pass

    def render(self) -> None:
        if self.is_active:
            self.canvas.itemconfigure(self.__id1, state="normal")
            self.canvas.itemconfigure(self.__id2, state="normal")
            self.canvas.tag_raise(self.__id1)
            self.canvas.tag_raise(self.__id2)
            self.canvas.coords(self.__id1, self.x-10, self.y-10, self.x+10, self.y+10)
            self.canvas.coords(self.__id2, self.x-10, self.y+10, self.x+10, self.y-10)
        else:
            self.canvas.itemconfigure(self.__id1, state="hidden")
            self.canvas.itemconfigure(self.__id2, state="hidden")

    def activate(self, x: float, y: float) -> None:
        """
        Activate this waypoint with the specified location.
        """
        self.__active = True
        self.x = x
        self.y = y

    def deactivate(self) -> None:
        """
        Mark this waypoint as inactive.
        """
        self.__active = False

    @property
    def is_active(self) -> bool:
        """
        Get the flag indicating whether this waypoint is active.
        """
        return self.__active


class Home(TurtleGameElement):
    """
    Represent the player's home.
    """

    def __init__(self, game: "TurtleAdventureGame", pos: tuple[int, int], size: int):
        super().__init__(game)
        self.__id: int
        self.__size: int = size
        x, y = pos
        self.x = x
        self.y = y

    @property
    def size(self) -> int:
        """
        Get or set the size of Home
        """
        return self.__size

    @size.setter
    def size(self, val: int) -> None:
        self.__size = val

    def create(self) -> None:
        self.__id = self.canvas.create_rectangle(0, 0, 0, 0, outline="brown", width=2)

    def delete(self) -> None:
        self.canvas.delete(self.__id)

    def update(self) -> None:
        # there is nothing to update, unless home is allowed to moved
        pass

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size/2,
                           self.y - self.size/2,
                           self.x + self.size/2,
                           self.y + self.size/2)

    def contains(self, x: float, y: float):
        """
        Check whether home contains the point (x, y).
        """
        x1, x2 = self.x-self.size/2, self.x+self.size/2
        y1, y2 = self.y-self.size/2, self.y+self.size/2
        return x1 <= x <= x2 and y1 <= y <= y2


class Player(TurtleGameElement):
    """
    Represent the main player, implemented using Python's turtle.
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 turtle: RawTurtle,
                 speed: float = 5):
        super().__init__(game)
        self.__speed: float = speed
        self.__turtle: RawTurtle = turtle

    def create(self) -> None:
        turtle = RawTurtle(self.canvas)
        turtle.getscreen().tracer(False) # disable turtle's built-in animation
        turtle.shape("turtle")
        turtle.color("green")
        turtle.penup()

        self.__turtle = turtle

    @property
    def speed(self) -> float:
        """
        Give the player's current speed.
        """
        return self.__speed

    @speed.setter
    def speed(self, val: float) -> None:
        self.__speed = val

    def delete(self) -> None:
        pass

    def update(self) -> None:
        # check if player has arrived home
        if self.game.home.contains(self.x, self.y):
            self.game.game_over_win()
        turtle = self.__turtle
        waypoint = self.game.waypoint
        if self.game.waypoint.is_active:
            turtle.setheading(turtle.towards(waypoint.x, waypoint.y))
            turtle.forward(self.speed)
            if turtle.distance(waypoint.x, waypoint.y) < self.speed:
                waypoint.deactivate()

    def render(self) -> None:
        self.__turtle.goto(self.x, self.y)
        self.__turtle.getscreen().update()

    # override original property x's getter/setter to use turtle's methods
    # instead
    @property
    def x(self) -> float:
        return self.__turtle.xcor()

    @x.setter
    def x(self, val: float) -> None:
        self.__turtle.setx(val)

    # override original property y's getter/setter to use turtle's methods
    # instead
    @property
    def y(self) -> float:
        return self.__turtle.ycor()

    @y.setter
    def y(self, val: float) -> None:
        self.__turtle.sety(val)


class Enemy(TurtleGameElement):
    """
    Define an abstract enemy for the Turtle's adventure game
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game)
        self.__size = size
        self.__color = color

    @property
    def size(self) -> float:
        """
        Get the size of the enemy
        """
        return self.__size

    @property
    def color(self) -> str:
        """
        Get the color of the enemy
        """
        return self.__color

    def hits_player(self):
        """
        Check whether the enemy is hitting the player
        """
        return (
            (self.x - self.size/2 < self.game.player.x < self.x + self.size/2)
            and
            (self.y - self.size/2 < self.game.player.y < self.y + self.size/2)
        )


# TODO
# * Define your enemy classes
# * Implement all methods required by the GameElement abstract class
# * Define enemy's update logic in the update() method
# * Check whether the player hits this enemy, then call the
#   self.game.game_over_lose() method in the TurtleAdventureGame class.
class RandomWalkEnemy(Enemy):
    """
    Enemy that walks randomly.
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game, size, color)
        self.angle = randint(0, 360)  # Random direction in degrees
        self.counter = 0  # Counter for updates

    def create(self) -> None:
        self.__id = self.canvas.create_oval(0, 0, 0, 0, fill="red")

    def update(self) -> None:
        speed = 7
        self.x += speed * cos(radians(self.angle))
        self.y += speed * sin(radians(self.angle))
        self.x = max(0, min(self.x, 800))
        self.y = max(0, min(self.y, 500))
        if self.hits_player():
            self.game.game_over_lose()

        self.counter += 1
        if self.counter >= 60 * 0.25:
            self.angle = randint(0, 360)
            self.counter = 0

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size/2,
                           self.y - self.size/2,
                           self.x + self.size/2,
                           self.y + self.size/2)

    def delete(self) -> None:
        pass


class ChasingEnemy(Enemy):
    """
    Enemy that chases the player.
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game, size, color)

    def create(self) -> None:
        self.__id = self.canvas.create_oval(0, 0, 0, 0, fill="blue")

    def update(self) -> None:
        speed = 3
        player = self.game.player
        angle = self.angle_to(player.x, player.y)
        self.x += speed * cos(radians(angle))
        self.y += speed * sin(radians(angle))
        if self.hits_player():
            self.game.game_over_lose()

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size/2,
                           self.y - self.size/2,
                           self.x + self.size/2,
                           self.y + self.size/2)

    def delete(self) -> None:
        pass

    def angle_to(self, x: float, y: float) -> float:
        """
        Calculate the angle from the enemy to the given point (x, y)
        """
        dx = x - self.x
        dy = y - self.y
        return (360 + degrees(atan2(dy, dx))) % 360


class FencingEnemy(Enemy):
    """
    Enemy that moves around the player's home.
    """
    
    def __init__(self, game: "TurtleAdventureGame", size: int, color: str):
        super().__init__(game, size, color)
        self.__game = game
        self.angle = 0 
        self.counter = 0
        self.home_x, self.home_y = game.home.x, game.home.y
        self.radius = 50
        self.x = self.home_x - self.radius
        self.y = self.home_y - self.radius

    def create(self) -> None:
        self.__id = self.canvas.create_oval(0, 0, 0, 0, fill="yellow")

    def update(self) -> None:
        speed = 3

        if self.hits_player():
            self.__game.game_over_lose()

        # Update x and y coordinates based on current angle
        if self.angle == 0:
            self.x += speed
            if self.x > self.home_x + self.radius:
                self.angle = 90
                self.y += speed
        elif self.angle == 90:
            self.y += speed
            if self.y > self.home_y + self.radius:
                self.angle = 180
                self.x -= speed
        elif self.angle == 180:
            self.x -= speed
            if self.x < self.home_x - self.radius:
                self.angle = 270
                self.y -= speed
        elif self.angle == 270:
            self.y -= speed
            if self.y < self.home_y - self.radius:
                self.angle = 0
                self.x += speed

    def render(self) -> None:
        self.canvas.coords(self.__id,
                        self.x - self.size/2,
                        self.y - self.size/2,
                        self.x + self.size/2,
                        self.y + self.size/2)

    def delete(self) -> None:
        pass


# TODO
# Complete the EnemyGenerator class by inserting code to generate enemies
# based on the given game level; call TurtleAdventureGame's add_enemy() method
# to add enemies to the game at certain points in time.
#
# Hint: the 'game' parameter is a tkinter's frame, so it's after()
# method can be used to schedule some future events.

class EnemyGenerator:
    """
    An EnemyGenerator instance is responsible for creating enemies of various
    kinds and scheduling them to appear at certain points in time.
    """

    def __init__(self, game: "TurtleAdventureGame", level: int):
        self.__game: TurtleAdventureGame = game
        self.__level: int = level

        # example
        self.__game.after(100, self.create_enemy)

    @property
    def game(self) -> "TurtleAdventureGame":
        """
        Get reference to the associated TurtleAnvengerGame instance
        """
        return self.__game

    @property
    def level(self) -> int:
        """
        Get the game level
        """
        return self.__level

    def create_enemy(self) -> None:
        """
        Create a new enemy, possibly based on the game level
        """
        rw = RandomWalkEnemy(self.__game, 20, "red")
        cs = ChasingEnemy(self.__game, 20, "blue")
        fc = FencingEnemy(self.__game, 20, "yellow")
        rw.x = randint(100, 700)
        rw.y = randint(100, 400)
        cs.x = randint(100, 700)
        cs.y = randint(100, 400)
        fc.x = self.__game.home.x - 50
        fc.y = self.__game.home.y - 50
        self.game.add_element(rw)
        self.game.add_element(cs)
        self.game.add_element(fc)


class TurtleAdventureGame(Game): # pylint: disable=too-many-ancestors
    """
    The main class for Turtle's Adventure.
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(self, parent, screen_width: int, screen_height: int, level: int = 1):
        self.level: int = level
        self.screen_width: int = screen_width
        self.screen_height: int = screen_height
        self.waypoint: Waypoint
        self.player: Player
        self.home: Home
        self.enemies: list[Enemy] = []
        self.enemy_generator: EnemyGenerator
        super().__init__(parent)

    def init_game(self):
        self.canvas.config(width=self.screen_width, height=self.screen_height)
        turtle = RawTurtle(self.canvas)
        # set turtle screen's origin to the top-left corner
        turtle.screen.setworldcoordinates(0, self.screen_height-1, self.screen_width-1, 0)

        self.waypoint = Waypoint(self)
        self.add_element(self.waypoint)
        self.home = Home(self, (self.screen_width-100, self.screen_height//2), 20)
        self.add_element(self.home)
        self.player = Player(self, turtle)
        self.add_element(self.player)
        self.canvas.bind("<Button-1>", lambda e: self.waypoint.activate(e.x, e.y))

        self.enemy_generator = EnemyGenerator(self, level=self.level)

        self.player.x = 50
        self.player.y = self.screen_height//2

    def add_enemy(self, enemy: Enemy) -> None:
        """
        Add a new enemy into the current game
        """
        self.enemies.append(enemy)
        self.add_element(enemy)

    def game_over_win(self) -> None:
        """
        Called when the player wins the game and stop the game
        """
        self.stop()
        font = ("Arial", 36, "bold")
        self.canvas.create_text(self.screen_width/2,
                                self.screen_height/2,
                                text="You Win",
                                font=font,
                                fill="green")

    def game_over_lose(self) -> None:
        """
        Called when the player loses the game and stop the game
        """
        self.stop()
        font = ("Arial", 36, "bold")
        self.canvas.create_text(self.screen_width/2,
                                self.screen_height/2,
                                text="You Lose",
                                font=font,
                                fill="red")
