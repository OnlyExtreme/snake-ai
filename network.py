import numpy as np

# 手写一个 sigmoid 激活函数捏
def sigmoid(x):
    s = 1 / (1 + np.exp(-x))
    return s

def ReLU(x):
    s = np.maximum(0, x)
    return s

class Network(object):
    # 手写神经网络捏
    # 一个输入层，三个全连接层，两个隐藏层，一个输出层
    # 输入是三个方向的面前是否有食物或障碍的六个布尔值
    # 输出是 向前 / 左拐 / 右拐
    # 输入层 : 1 * 6
    # 隐藏层1 : 6 * 20
    # 全连接层 : 1 * 20
    # 隐藏层2 : 20 * 3
    # 输出层 : 1 * 3

    def __init__(self):
        self.input = np.zeros((1, 6), dtype=float)
        self.linear_1 = np.zeros((6, 20), dtype=float)
        self.hidden_1 = np.zeros((1, 20), dtype=float)
        self.linear_2 = np.zeros((20, 20), dtype=float)
        self.hidden_2 = np.zeros((1, 20), dtype=float)
        self.linear_3 = np.zeros((20, 3), dtype=float)
        self.output = np.zeros((1, 3), dtype=float)

    # 加载权重参数
    def load_parameter(self, parameters):
        self.linear_1 = np.array(parameters[0])
        self.linear_2 = np.array(parameters[1])
        self.linear_3 = np.array(parameters[2])

    # 加载输入数据
    def load_input(self, inpt):
        self.input = np.array(inpt, dtype=float)

    # 计算前向过程（虽然没有反向过程）
    def calc(self):
        self.hidden_1 = ReLU(np.dot(self.input, self.linear_1))
        self.hidden_2 = ReLU(np.dot(self.hidden_1, self.linear_2))
        self.output = sigmoid(np.dot(self.hidden_2, self.linear_3))

    # 判断输出是往哪里转
    def decision(self):
        #print(self.output)
        maxid = maxnum = -1
        for i in range(3):
            if self.output[0][i] > maxnum:
                maxnum = self.output[0][i]
                maxid = i
        return (maxid + 1) % 3 - 1