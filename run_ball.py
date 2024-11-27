from pytest import console_main
import ball
import my_event
import turtle
import random
import heapq
import threading
import numpy as np
import paddle
import time

class BouncingSimulator:
    def __init__(self, num_balls):
        self.num_balls = num_balls
        self.ball_list = []
        self.t = 0.0
        self.pq = []
        self.HZ = 4
        turtle.speed(0)
        turtle.tracer(0)
        turtle.hideturtle()
        turtle.colormode(255)
        self.canvas_width = turtle.screensize()[0]
        self.canvas_height = turtle.screensize()[1]
        print(self.canvas_width, self.canvas_height)

        
        for i in range(self.num_balls):
            ball_radius = random.uniform(0.01, 0.09) * self.canvas_width
            x = -self.canvas_width + (i+1)*(2*self.canvas_width/(self.num_balls+1))
            y = 0.0
            vx = 10*random.uniform(-1.0, 1.0)
            vy = 10*random.uniform(-1.0, 1.0)
            ball_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            self.ball_list.append(ball.Ball(ball_radius, x, y, vx, vy, ball_color, i))

        tom = turtle.Turtle()
        self.my_paddle = paddle.Paddle(50, 50, (255, 0, 0), tom)
        self.my_paddle.set_location([0, -50])

        self.screen = turtle.Screen()

    # updates priority queue with all new events for a_ball
    def __predict(self, a_ball):
        if a_ball is None:
            return
        
        print(a_ball.vy)

        # particle-particle collisions
        if self.ball_list:
            for i in range(len(self.ball_list)):
                dt = a_ball.time_to_hit(self.ball_list[i])
                # insert this event into pq
                heapq.heappush(self.pq, my_event.Event(self.t + dt, a_ball, self.ball_list[i], None))
        
        # particle-wall collisions
        dtX = a_ball.time_to_hit_vertical_wall()
        dtY = a_ball.time_to_hit_horizontal_wall()
        heapq.heappush(self.pq, my_event.Event(self.t + dtX, a_ball, None, None))
        heapq.heappush(self.pq, my_event.Event(self.t + dtY, None, a_ball, None))
    
    def __draw_border(self):
        turtle.penup()
        turtle.goto(-self.canvas_width, -self.canvas_height)
        turtle.pensize(10)
        turtle.pendown()
        turtle.color((0, 0, 0))   
        for i in range(2):
            turtle.forward(2*self.canvas_width)
            turtle.left(90)
            turtle.forward(2*self.canvas_height)
            turtle.left(90)
    
    def __redraw(self):
        turtle.clear()
        self.my_paddle.clear()
        self.__draw_border()
        self.my_paddle.draw()
        for i in range(len(self.ball_list)):
            self.ball_list[i].draw()
        turtle.update()
        heapq.heappush(self.pq, my_event.Event(self.t + 1.0/self.HZ, None, None, None))

    def __paddle_predict(self):
        for i in range(len(self.ball_list)):
            a_ball = self.ball_list[i]
            if (a_ball.vy == 0) and (a_ball.vx == 0):
                continue
            dtP = a_ball.time_to_hit_paddle(self.my_paddle)
            heapq.heappush(self.pq, my_event.Event(self.t + dtP, a_ball, None, self.my_paddle))

    # move_left and move_right handlers update paddle positions
    def move_left(self):
        if (self.my_paddle.location[0] - self.my_paddle.width/2 - 40) >= -self.canvas_width:
            self.my_paddle.set_location([self.my_paddle.location[0] - 40, self.my_paddle.location[1]])

    # move_left and move_right handlers update paddle positions
    def move_right(self):
        if (self.my_paddle.location[0] + self.my_paddle.width/2 + 40) <= self.canvas_width:
            self.my_paddle.set_location([self.my_paddle.location[0] + 40, self.my_paddle.location[1]])
    
    def move_up(self):
        if (self.my_paddle.location[1] + self.my_paddle.height/2 + 40) <= self.canvas_height:
            self.my_paddle.set_location([self.my_paddle.location[0], self.my_paddle.location[1] + 40])
    
    def move_down(self):
        if (self.my_paddle.location[1] - self.my_paddle.height/2 - 40) >= -self.canvas_height:
            self.my_paddle.set_location([self.my_paddle.location[0], self.my_paddle.location[1] - 40])

    def fire(self):
        b = ball.Ball(5, self.my_paddle.location[0], self.my_paddle.location[1], 0, 50, (255,0,0), self.num_balls+1)
        self.ball_list.append(b)
        print(self.ball_list)
        self.__predict(b)
        self.__redraw()


    def run(self):
        # initialize pq with collision events and redraw event
        for i in range(len(self.ball_list)):
            self.__predict(self.ball_list[i])
            self.__paddle_predict()
            continue
        heapq.heappush(self.pq, my_event.Event(0, None, None, None))

        # listen to keyboard events and activate move_left and move_right handlers accordingly
        self.screen.listen()
        self.screen.onkey(self.move_left, "a")
        self.screen.onkey(self.move_right, "d")
        self.screen.onkey(self.move_up, "w")
        self.screen.onkey(self.move_down, "s")
        self.screen.onkey(self.fire, " ")

        t = 0
        frame = 0
        

        while (True):
            start = time.time()
            if not self.ball_list:
                b1 = ball.Ball(1, self.canvas_width+5, self.canvas_height+5, 0, 0, (0,0,0), 999)
                self.ball_list.append(b1)
            elif len(self.ball_list) > 1:
                try:
                    self.ball_list.pop(self.ball_list.index(b1))
                    del b1
                except UnboundLocalError:
                    x = 1
            e = heapq.heappop(self.pq)
            if not e.is_valid():
                continue
            ball_a = e.a
            ball_b = e.b
            paddle_a = e.paddle
            if not self.ball_list:
                continue

            # update positions, and then simulation clock
            for i in range(len(self.ball_list)):
                self.ball_list[i].move(e.time - self.t)
            self.t = e.time

            

            if (ball_a is not None) and (ball_b is not None) and (paddle_a is None):
                ball_a.bounce_off(ball_b)
            elif (ball_a is not None) and (ball_b is None) and (paddle_a is None):
                try:
                    # print("remove", ball_a.id)
                    self.__redraw()
                    self.ball_list.pop(self.ball_list.index(ball_a))
                    del ball_a
                except AttributeError and ValueError:
                    print("nope")
                continue
                # ball_a.bounce_off_vertical_wall()
            elif (ball_a is None) and (ball_b is not None) and (paddle_a is None):
                try:
                    # print("remove", ball_b.id)
                    self.__redraw()
                    self.ball_list.pop(self.ball_list.index(ball_b))
                    del ball_b
                except AttributeError and ValueError :
                    print("nope")
                continue
            elif (ball_a is None) and (ball_b is None) and (paddle_a is None):
                self.__redraw()
            elif (ball_a is not None) and (ball_b is None) and (paddle_a is not None):
                ball_a.bounce_off_paddle()

            pa = threading.Thread(target=self.__predict, args=(ball_a,))
            pb = threading.Thread(target=self.__predict, args=(ball_b,))

            pa.start()
            pb.start()

            pa.join()
            pb.join()

            # self.__predict(ball_a)
            # self.__predict(ball_b)

            # regularly update the prediction for the paddle as its position may always be changing due to keyboard events
            self.__paddle_predict()

            frame += 1

            end = time.time()
            t = t + end-start

            if t >= 1:
                print(t)
                print(frame)
                t = 0
                frame = 0


        # hold the window; close it by clicking the window close 'x' mark
        turtle.done()

# num_balls = int(input("Number of balls to simulate: "))
num_balls = 5
my_simulator = BouncingSimulator(num_balls)
my_simulator.run()
