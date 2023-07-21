import numpy as np

def sigmoid(x):
    s = 1 / (1 + np.exp(-x))
    return s

class Network(object):
    # 手写神经网络捏
    # 一个输入层，三个全连接层，两个隐藏层，一个输出层
    # 输入层 : 6
    # 隐藏层1 : 6 * 20
    # 全连接层 : 20
    # 隐藏层2 : 20 * 4
    # 输出层 : 4

    def __init__(self):
        self.input = np.zeros(6)
        self.linear_1 = np.zeros(6, 20)
        self.hidden_1 = np.zeros(20)
        self.linear_2 = np.zeros(20, 20)
        self.hidden_2 = np.zeros(20)
        self.linear_3 = np.zeros(20, 4)
        self.output = np.zeros(4)

    def load_parameter(self, parameters):
        self.linear_1 = np.matrix(parameters[0])
        self.linear_2 = np.matrix(parameters[1])
        self.linear_3 = np.matrix(parameters[2])

    def load_input(self, inpt):
        self.input = np.array(inpt)

    def calc(self):
        self.hidden_1 = sigmoid(np.dot(self.input, self.linear_1))
        self.hidden_2 = sigmoid(np.dot(self.hidden_1, self.linear_2))
        self.output = sigmoid(np.dot(self.hidden_2, self.linear_3))

    def decision(self):
        maxid = maxnum = -1
        for i in range(4):
            if self.output[i] > maxnum:
                maxnum = self.output[i]
                maxid = i
        return maxid