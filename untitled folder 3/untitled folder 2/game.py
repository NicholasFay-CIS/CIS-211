#Nicholas Fay
#Practice

#imports needed modules
import random
import turtle
import math

image = "rocketship.png"
#sets up screen
wn = turtle.Screen() #screen method
wn.bgcolor("black") #background color is this
wn.title("python game") #title
wn.bgpic("kbgame-bg.gif")
wn.register_shape("ball2.gif")

class Terminator(turtle.Turtle):
    def __init__(self):
        turtle.Turtle.__init__(self)
        self.penup()
        self.shape("triangle")
        self.speed = 5
        self.color("blue")
        self.goto(random.randint(-250, 250), random.randint(-250, 250))  # starts at a random location
        self.setheading(random.randint(0, 360))

    def move(self):
        self.forward(self.speed)
        #checks the border
        if self.xcor() > 290 or self.xcor() < -290:
            self.left(60)
        if self.ycor() > 290 or self.ycor() < -290:
            self.left(60)

    def turnleft(self):
        self.left(30)

    def turnright(self):
        self.right(30)

    def increasespeed(self):
        self.speed += 1
    def decrease_speed(self):
        self.speed -= 1

class Bullet(turtle.Turtle):
    def __init__(self):
        turtle.Turtle.__init__(self)
        self.penup()
        self.hideturtle()
        self.speed = 10
        self.shape("circle")
        self.color("green")
        self.goto(0, 0)

    def movement(self):
        self.showturtle()
        self.forward(self.speed)
        if self.xcor() > 290 or self.xcor() < -290:
            self.hideturtle()
            self.goto(player.xcor(), player.ycor())
        if self.ycor() > 290 or self.ycor() < -290:
            self.hideturtle()
            self.goto(player.xcor(), player.ycor())


class Game2(turtle.Turtle):
    def __init__(self):
        turtle.Turtle.__init__(self)
        self.penup()
        self.hideturtle()
        self.speed(0)
        self.color("red")
        self.goto(-200, 310)
        self.score = 0

    def update_score_2(self):
        self.clear()
        self.write("Score: {}".format(self.score), False, align="left", font = ("Arial", 14, "normal"))

    def change_score_2(self, oints):
        self.score += oints
        self.update_score_2()
    def decrease_score(self, oints):
        self.score -= oints
        self.update_score_2()


class Game(turtle.Turtle):
    def __init__(self):
        turtle.Turtle.__init__(self)
        self.penup()
        self.hideturtle()
        self.speed(0)
        self.color("white")
        self.goto(-290, 310) #just outside the border
        self.score = 0

    def update_score(self):
        self.clear() #so it doesnt draw on top
        self.write("Score: {}".format(self.score), False, align="left", font = ("Arial", 14, "normal"))

    def change_score(self, points):
        self.score += points
        self.update_score() #calls to update the score to display it


class Goal(turtle.Turtle):

    def __init__(self):
        turtle.Turtle.__init__(self) #initilize its parent which is turtle.Turtle
        self.penup()
        self.speed(0)
        self.color("green")
        self.shape("turtle")
        self.speed = 3
        self.goto(random.randint(-250, 250), random.randint(-250, 250)) #starts at a random location
        self.setheading(random.randint(0,360))


    def move(self):
        self.forward(self.speed)
        #checks the border
        if self.xcor() > 290 or self.xcor() < -290:
            self.left(60)
        if self.ycor() > 290 or self.ycor() < -290:
            self.left(60)

    def jump(self):
        self.goto(random.randint(-250, 250), random.randint(-250, 250))
        self.setheading(random.randint(0, 360))

class Border(turtle.Turtle):
    def __init__(self):
        turtle.Turtle.__init__(self)
        self.penup() #dont draw
        self.hideturtle() #dont need to see the turtle to draw border
        self.speed(0) #animation speed
        self.color("white")
        self.pensize(6) #widtch of the border in pixels

    def draw_border(self):
        self.penup()
        self.goto(-300, -300)
        self.pendown()
        self.goto(-300, 300)
        self.goto(300, 300)
        self.goto(300, -300)
        self.goto(-300, -300)

class Enemy(turtle.Turtle):
    #constructor
    def __init__(self):
        turtle.Turtle.__init__(self)
        self.penup()
        self.shape("triangle")
        self.color("red")
        self.speed = 4
        self.score = 0
        self.goto(random.randint(-250, 250), random.randint(-250, 250))  # starts at a random location
        self.setheading(random.randint(0, 360))

    def move(self):
        self.forward(self.speed)
        if self.xcor() > 290 or self.xcor() < -290:
            self.left(60)
        if self.ycor() > 290 or self.ycor() < -290:
            self.left(60)


class Player(turtle.Turtle):
    #constructor
    def __init__(self):
        turtle.Turtle.__init__(self)
        self.penup()
        self.shape("triangle")
        self.color("white")
        self.speed = 1
        self.score = 0
        self.max = 100

    def move(self):
        self.forward(self.speed)
        #checks the border
        if self.xcor() > 290 or self.xcor() < -290:
            self.left(60)
        if self.ycor() > 290 or self.ycor() < -290:
            self.left(60)

    def turnleft(self):
        self.left(30)

    def turnright(self):
        self.right(30)

    def increasespeed(self):
        self.speed += 1
    def decrease_speed(self):
        self.speed -= 1


#Tests for collison
def isCollision(t1, t2):
    a = t1.xcor() - t2.xcor()
    b = t1.ycor() - t2.ycor()
    distance = math.sqrt((a ** 2) + b ** 2)

    if distance < 20:
        return True
    else:
        return False

#class instance (player object)
player = Player()
border = Border()
bullet = Bullet()
game = Game()
enemy = Enemy()
game2 = Game2()
terminator = Terminator()
border.draw_border() #draws the border

goals = []
for count in range(10):
    goals.append(Goal())

#Sets up the keyboard for the sprite
turtle.listen()
turtle.onkey(player.turnleft, "Left")
turtle.onkey(player.turnright, "Right")
turtle.onkey(player.increasespeed, "Up")
turtle.onkey(player.decrease_speed, "Down")
turtle.onkey(bullet.movement, "l")

#speed up the game
wn.tracer(0) #0 means do not update screen

#Main loop
def main():
    while True:
        wn.update() #update the screen in the loop
        player.move()
        enemy.move()
        terminator.hideturtle()
        for goal in goals:
            goal.move()
            #checks for collison
            if isCollision(player, goal):
                goal.jump()
                game.change_score(10) #changes the score by ten points for each collision
            if isCollision(enemy, goal):
                goal.jump()
                game2.change_score_2(10)
            if isCollision(terminator, goal):
                goal.jump()
                game2.change_score_2(20)

            if isCollision(bullet, enemy):
                goal.jump()
                game2.decrease_score(10)

            if isCollision(bullet, terminator):
                goal.jump()
                game2.decrease_score(10)

        if game.score >= 210:
            game.clear()
            game2.clear()
            game.write("Game is over. Your score is {}".format(game.score), False, align="left",
                       font=("Arial", 14, "normal"))
        if game2.score >= 90:
            terminator.showturtle()
            terminator.move()

        if game2.score >= 210:
            game.clear()
            game2.clear()
            game.write("Game is over.The Enemy beat you! Your score is {}".format(game.score), False, align="left",
                       font=("Arial", 14, "normal"))

        if game.score == 220:
            break

        if game2.score == 220:
            break
main()
