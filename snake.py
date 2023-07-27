import pygame
from random import *
import sys
from math import *
from pygame.locals import *

TPS = 15
window_width = window_height = 400
cellsize = 20
cell_width = cell_height = 20

BGcolor = (255, 255, 255)
Headcolor = (0, 0, 0)
Bordercolor = (200, 200, 200)
Applecolor = (0, 255, 0)

def angle_to_point(x1, x2, y1, y2):
        return atan2(y2 - y1, x2 - x1)


dir = [[1, 0], [0, 1], [-1, 0], [0, -1]] #rdlu

class Board(object):

    # The Data Structure of the board and the game

    def __init__(self):     # Initialization
        self.grid = [[0 for col in range(22)] for row in range(22)]
        self.food = [0, 0]
        self.eat = False
        self.dir_head = randint(0, 3)
        while self.dir_head == 2:
            self.dir_head = randint(0, 3)
        self.head = [11, 10]
        self.grid[11][10] = 1
        self.grid[10][10] = 2
        self.grid[9][10] = 3
        self.grid[8][10] = 4
        self.len = 4
        self.score = 0
        for i in range(22):
            self.grid[i][0] = self.grid[0][i] = self.grid[i][21] = self.grid[21][i] = -2       # Set Walls

    def find_body_dir(self, x, y):  # Find the direction of the next body part of given position
        for i in range(4):
            d = dir[i]
            tag = self.grid[x+d[0]][y+d[1]]
            if tag == self.grid[x][y] + 1:
                return i
            
    def generate_food(self, xx, yy):    # Randomly Generate a new food
        self.tar_x = randint(1, 20)
        self.tar_y = randint(1, 20)
        if self.grid[self.tar_x][self.tar_y] != 0:
            try:
                self.generate_food(0, 0)
            except RuntimeError:
                return
            return
        self.grid[self.tar_x][self.tar_y] = -1     # Set Food Position
        self.food = [self.tar_x, self.tar_y]

    def turn(self, ndir):   # Check and do a turn for rdlu method
        cdir = self.dir_head
        if (cdir & 1) != (ndir & 1):
            self.dir_head = ndir

    def turn_dir(self, t):      # Turning function for left / right / forward method
        ndir = (self.dir_head + 4 + t) % 4
        self.dir_head = ndir
    
    def get_tag(self, adir):    # Get tag for the given position in 3 directions
        if adir == 0:
            ndir = self.dir_head
        elif adir == 1:
            ndir = (self.dir_head + 3) % 4
        else:
            ndir = (self.dir_head + 5) % 4
        return self.grid[self.head[0]+dir[ndir][0]][self.head[1]+dir[ndir][1]]
    
    def old_get_sensor(self):   # Get sensing data for the input of the neural networks
        sensor = [[]]
        ft = self.get_tag(0)
        lt = self.get_tag(1)
        rt = self.get_tag(2)
        sensor[0].append(float(ft == -1))
        sensor[0].append(float(lt == -1))
        sensor[0].append(float(rt == -1))
        sensor[0].append(float(ft != 0 and ft != -1))
        sensor[0].append(float(lt != 0 and lt != -1))
        sensor[0].append(float(rt != 0 and rt != -1))
        for i in range(6):
            sensor[0][i] = 0.1 if sensor[0][i] == 0 else 0.9
        return sensor
    
    def get_sensor_second(self):
        sensor = [[]]
        food = []
        obstacle = []
        for i in range(3, 6):
            ndir = (self.dir_head + i) % 4
            xx = self.head[0]
            yy = self.head[1]
            dis = 0
            foundOb = False
            foundFo = False
            while xx >= 0 and xx <= 21 and yy <= 21 and yy >= 0:
                if (self.grid[xx][yy] >= 2 or self.grid[xx][yy] == -2) and foundOb == False:
                    obstacle.append(dis)
                    foundOb = True
                if self.grid[xx][yy] == -1:
                    food.append(dis)
                dis += 1
                xx += dir[ndir][0]
                yy += dir[ndir][1]
            if not foundFo:
                food.append(21)
        for i in range(3):
            sensor[0].append(float(1 / (food[i] + 1)))
            sensor[0].append(float(1 / (obstacle[i] + 1)))
#        print(sensor)
        return sensor
    
    
    def get_sensor(self):

        sensor = [[]]

        a = angle_to_point(self.head[0], self.head[1], self.food[0], self.food[1])
        d = degrees(a)

        theta = d + self.dir_head * 90
        theta = (theta - 360) if theta > 180 else theta
        theta /= 180

        if theta > -.25 and theta < .25:
            sensor[0] = [0.3, 0.7, 0.3]
        elif theta <= -.25:
            sensor[0] = [0.7, 0.3, 0.3]
        else:
            sensor[0] = [0.3, 0.3, 0.7]
        
        obstacle = []
        for i in range(3, 6):
            ndir = (self.dir_head + i) % 4
            xx = self.head[0]
            yy = self.head[1]
            dis = 0
            foundOb = False
            while xx >= 0 and xx <= 21 and yy <= 21 and yy >= 0:
                if (self.grid[xx][yy] >= 2 or self.grid[xx][yy] == -2) and foundOb == False:
                    obstacle.append(dis)
                    foundOb = True
                dis += 1
                xx += dir[ndir][0]
                yy += dir[ndir][1]
        for i in range(3):
            sensor[0].append(float(1 / (obstacle[i] + 1)))
#        print(sensor)
        return sensor


    
    def is_valid(self):     # Check if the next move is valid
        nx = self.head[0] + dir[self.dir_head][0]
        ny = self.head[1] + dir[self.dir_head][1]
        if self.grid[nx][ny] != 0 and self.grid[nx][ny] != -1:
            return False
        return True
    
    def update_grid(self, nx, ny):      # Update the grid after a move
        self.grid[nx][ny] = 1
        ix = self.head[0]
        iy = self.head[1]
        self.head = [nx, ny]
        for i in range(self.len - 1):
            idir = self.find_body_dir(ix, iy)
            self.grid[ix][iy] += 1
            ix += dir[idir][0]
            iy += dir[idir][1]
        self.grid[ix][iy] = self.grid[ix][iy] + 1 if self.eat else 0
        self.len = self.len + 1 if self.eat else self.len
        
    
    def move(self):     # Do a step of move and update the grid
        cdis = abs(self.head[0] - self.food[0]) + abs(self.head[1] - self.food[1])
        self.eat = False
        nx = self.head[0] + dir[self.dir_head][0]
        ny = self.head[1] + dir[self.dir_head][1]
        ndis = abs(nx - self.food[0]) + abs(ny - self.food[1])
        if ndis < cdis:
            self.score += 1
        else:
            self.score -= 1.5
        if self.grid[nx][ny] == -1:
            self.eat = True
            self.score += 10
#        else:
#            self.score -= 0.1
        self.update_grid(nx, ny)


class Game(object):
    # A packed class for game control
    # Easy to use from training controller


    def __init__(self, is_Human_Player, xx, yy):
        self.steps = 1
        self.score = 0
        self.game_over = 0
        self.is_Human_Player = is_Human_Player
        self.board = Board()
        self.board.generate_food(xx, yy)
        
    def set_game_over(self):    # 好家伙我写这个干什么
        self.game_over = 1
#        self.score -= 20

    def get_body_color(self, color_shift, part):    # 做了一个蛇身颜色渐变效果，好看好看
#        print(tuple(int((Headcolor[i] + color_shift * (part - 1))) for i in range(3)))
        return tuple(int((Headcolor[i] + color_shift * (part - 1))) for i in range(3))

    def draw(self):     # 画一帧
        window.fill(BGcolor)    # 清屏

        # 画格子
        for x in range(0, window_width, cellsize):
            pygame.draw.line(window, Bordercolor, (x, 0), (x, window_height))
        for y in range(0, window_height, cellsize):
            pygame.draw.line(window, Bordercolor, (0, y), (window_width, y))

        # 画蛇和事物
        color_shift = float(128 / self.board.len)
        for i in range(1, 21):
            for j in range (1, 21):
                x = (i - 1) * cellsize
                y = (j - 1) * cellsize
                if self.board.grid[i][j] >= 1:
                    snakeSegmentRect = pygame.Rect(x, y, cellsize, cellsize)
                    pygame.draw.rect(window, tuple(self.get_body_color(color_shift, self.board.grid[i][j])), snakeSegmentRect)
                elif self.board.grid[i][j] == -1:
                    appleRect = pygame.Rect(x, y, cellsize, cellsize)
                    pygame.draw.rect(window, Applecolor, appleRect)

        pygame.display.update()

    
    def ai_run_tick(self, xx, yy):

        # 只是把 run_tick 里面按键部分去掉了

        # 一堆游戏机制的检测与游戏内容的运行
        if not self.board.is_valid():
            self.set_game_over()
            return
        self.steps += 1
        self.board.move()
        self.score = self.board.score
        if self.board.eat == True:
            self.board.generate_food(0, 0)
#        self.draw()     # 画出来    
        if self.is_Human_Player:
            FPSclock.tick(TPS)      # 停顿（不过跑 AI 的时候大概率会去掉）
        return
                    
    
    def run_tick(self):     # 跑一帧

        # 先侦测按键，不然不跟手
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_RIGHT:
                    self.board.turn(0)
                elif event.key == K_DOWN:
                    self.board.turn(1)
                elif event.key == K_LEFT:
                    self.board.turn(2)
                elif event.key == K_UP:
                    self.board.turn(3)
                elif event.key == K_ESCAPE:
                    sys.exit()

        # 一堆游戏机制的检测与游戏内容的运行
        if not self.board.is_valid():
            self.set_game_over()
            return
        self.board.move()
        self.score = self.board.score
        if self.board.eat == True:
            self.board.generate_food()
        self.draw()     # 画出来    
        if self.is_Human_Player:
            FPSclock.tick(TPS)      # 停顿（不过跑 AI 的时候大概率会去掉）
        return


def main():

    # 主函数
    global FPSclock, window, BASICFONT
    pygame.init()
    FPSclock = pygame.time.Clock()
    window = pygame.display.set_mode((window_width, window_height))

    pygame.display.set_caption('Snake-AI')
    
    while True:
        game = Game(1)
        while True:
            game.run_tick()
            if game.game_over == 1:
                sys.exit()
            

#main()