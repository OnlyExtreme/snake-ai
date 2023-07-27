from io import *
from snake import *
from network import *
from random import *
import pygame

# 定义与初始化啊吧啊吧

games = []
networks = []

TPS = 15
window_width = window_height = 1600
cellsize = 8
cell_width = cell_height = 2

BGcolor = (255, 255, 255)
Headcolor = (0, 0, 0)
Bordercolor = (200, 200, 200)
Applecolor = (0, 255, 0)

with open('configuration.dat', 'r') as f:
    population = int(f.readline())
    generation = int(f.readline())
#    print(population, generation)
    f.close()


# 判断本轮是否结束
# 全部 死亡或者分数小于零 即本轮结束
def finished(it):
    if it <= 10:
        return False
    for agame in games:
        if (not agame.game_over) and (agame.score >= 0):
            return False
    return True

def generate_parameters():      # Generate parameters randomly for the initial generation
    l1 = l2 = l3 = []
    l1 = [[uniform(0, 1) for i in range(20)] for j in range(6)]
    l2 = [[uniform(0, 1) for i in range(20)] for j in range(20)]
    l3 = [[uniform(0, 1) for i in range(3)] for j in range(20)]
    return [l1, l2, l3]

def read_parameters(file_name):     # Load saved parameters from previous generation
    individuals = []
    layers = []
    parameters = []
    with open(file_name, 'r') as f:
        # Indivial parameter seperation: 'c'
        # Layer parameter seperation: 'b'
        # Single data seperation: 'a'
        raw = f.read()
        individuals = raw.split('c')
        layers += list(x.split('b') for x in individuals)
#        print(layers)
        for i in layers:
            tt = []
            for j in i:
                tmp = []
                tmp += list(float(x) for x in list(j.split('a')))
                tt.append(tmp)
            parameters.append(tt)
        f.close()
    return parameters

def get_body_color(color_shift, part):    # 做了一个蛇身颜色渐变效果，好看好看
#        print(tuple(int((Headcolor[i] + color_shift * (part - 1))) for i in range(3)))
    return tuple(int((Headcolor[i] + color_shift * (part - 1))) for i in range(3))

# Pygame visualization
def visualize():
    window.fill(BGcolor)

    for x in range(0, 1600, 160):
        pygame.draw.line(window, Bordercolor, (x, 0), (x, window_height))
    for y in range(0, 1600, 160):
        pygame.draw.line(window, Bordercolor, (0, y), (window_width, y))

    for i in range(10):
        for j in range(10):
            id = i * 10 + j
            color_shift = float(128 / games[id].board.len)
            for p in range(1, 21):
                for q in range(1, 21):
                    x = i * 160 + (p - 1) * cellsize
                    y = j * 160 + (q - 1) * cellsize
                    if games[id].board.grid[p][q] >= 1:
                        snakeSegmentRect = pygame.Rect(x, y, cellsize, cellsize)
                        pygame.draw.rect(window, tuple(get_body_color(color_shift, games[id].board.grid[p][q])), snakeSegmentRect)
                    elif games[id].board.grid[p][q] == -1:
                        appleRect = pygame.Rect(x, y, cellsize, cellsize)
                        pygame.draw.rect(window, Applecolor, appleRect)

                    if games[id].board.eat == True:
                        RedRect = pygame.Rect(i * 160, j * 160, 20, 20)
                        pygame.draw.rect(window, pygame.Color(255, 0, 0, a=0), RedRect)
    pygame.display.update()
    return

# Visualization Initialization
pygame.init()
FPSclock = pygame.time.Clock()
window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption('Snake-AI')

seed()

# Main Loop
while True:



    # Initialize the generation
    games.clear()
    networks.clear()
    xx = randint(1, 20)
    yy = randint(1, 20)
    for i in range(population):
        games.append(Game(0, xx, yy))
        networks.append(Network())

    # Load network parameters
    if generation == 0:
        for i in range(population):
            parameters = generate_parameters()
            networks[i].load_parameter(parameters)
    else:
        for i in range(population):
            file_name = "./data/"
            file_name += str(i)
            file_name += ".dat"
            parameters = read_parameters(file_name)
            networks[i].load_parameter(parameters)

    iteration = 0

    # Run the game process
    while True:
        iteration += 1
        xx = randint(1, 20)
        yy = randint(1, 20)
        for i in range(population):
            if games[i].game_over == True:
                continue
            #print(i)
            games[i].ai_run_tick(xx, yy)
            sensor_data = games[i].board.get_sensor()
            networks[i].load_input(sensor_data)
            #print(sensor_data)
            #print(networks[i].linear_1)
            networks[i].calc()
            ai_decision = networks[i].decision()
            games[i].board.turn_dir(ai_decision)
#           FPSclock.tick(120)
        visualize()
        if finished(iteration):
            break
    
    # 这一轮跑完力，开始遗传计算下一轮参数

    # 首先先把分数处理一下，用于交配取样
    scores = [(games[i].score) for i in range(population)]    # 提取分数
    score_copy = scores
    id = list(np.argsort(scores))     # 分数排序后的 id
    scores = sorted(scores)   # 排序
#    print(scores)
    target = 0
    for i in scores:
        if i >= 0:
            target = i
            break
    smallest = scores[0]    # 找最小值来映射到整数
    biggest = scores[population - 1]
    mapped = [((x - smallest) / (biggest - smallest)) for x in scores]   # 映射到正数
    ssum = sum(mapped)      
    gradience = float(1 / ssum)
    posibility = [(x * gradience) for x in mapped]
    target = 0
    for i in range(population):
        if i >= 1:
            posibility[i] += posibility[i-1]
    posibility[population - 1] = float(1.0)     # 计算取到每个个体的概率
#    print(posibility)
#    print(posibility[int(0.90 * population)])

    print(generation, scores[0], scores[int(population / 2)], scores[population - 1])

    # 开始生成新一轮种群
    for i in range(population):


        son = []

        if i >= int(0.9 * population):
            son = [networks[id[i]].linear_1, networks[id[i]].linear_2, networks[id[i]].linear_3]

        else:
        
            # 先把父母选出来
            father_id = mother_id = -1
            father = uniform(posibility[int(0.90 * population)], 1.0)
            mother = uniform(posibility[int(0.90 * population)], 1.0)
            for j in range(population - 1):
                if posibility[j] < father and posibility[j+1] >= father:
                    father_id = id[j+1]
                if posibility[j] < mother and posibility[j+1] >= mother:
                    mother_id = id[j+1]

#            print(father, mother, father_id, mother_id, games[father_id].score, games[mother_id].score)

            # 进行一波染色体操作
            pointer = randint(2, 4)
            son.append(list(networks[father_id].linear_1[:pointer]) + list(networks[mother_id].linear_1[pointer:]))
            pointer = randint(2, 18)
            son.append(list(networks[father_id].linear_2[:pointer]) + list(networks[mother_id].linear_2[pointer:]))
            pointer = randint(2, 18)
            son.append(list(networks[father_id].linear_3[:pointer]) + list(networks[mother_id].linear_3[pointer:]))

            # 随机来点变异
            for t in range(20):
                if random() <= 0.3:
                    son[0][randint(0, 5)][randint(0, 19)] = uniform(0, 1)
            for t in range(60):
                if random() <= 0.3:
                    son[1][randint(0, 19)][randint(0, 19)] = uniform(0, 1)
            for t in range(10):
                if random() <= 0.3:
                    son[2][randint(0, 19)][randint(0, 2)] = uniform(0, 1)
            
        # 保存当前个体
        raw = ""
        for x in son:
            for y in x:
                for z in y:
                    raw += str(z)
                    raw += 'a'
                raw = raw.rstrip('a')
                raw += 'b'
            raw = raw.rstrip('b')
            raw += 'c'
        raw = raw.rstrip('c')

        file_name = "./data/"
        file_name += str(i)
        file_name += ".dat"
        with open(file_name, 'w') as f:
            f.write(raw)
            f.close()
    
    generation += 1
    with open('configuration.dat', 'w') as f:
        f.write(str(population) + '\n' + str(generation))
        f.close()
    
        