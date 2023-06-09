"""Optimization module"""
import needle as ndl
import numpy as np


class Optimizer:
    def __init__(self, params):
        self.params = params

    def step(self):
        raise NotImplementedError()

    def reset_grad(self):
        for p in self.params:
            p.grad = None


class SGD(Optimizer):
    def __init__(self, params, lr=0.01, momentum=0.0, weight_decay=0.0):
        super().__init__(params)
        self.lr = lr
        self.momentum = momentum
        self.u = {}
        self.weight_decay = weight_decay

    def step(self):
        ### BEGIN YOUR SOLUTION
        for i,param in  enumerate(self.params):
            if i not in self.u:
                self.u[i] = 0.0
            if param.grad is None:
                continue
            grad_data = ndl.Tensor(param.grad+self.weight_decay*param.data, dtype='float32').data
            self.u[i] =self.momentum * self.u[i] \
                +(1-self.momentum)*grad_data
            print(self.u[i].dtype)
            param.data =param.data - self.lr*self.u[i]
            ## not understand why can't pass
            ## code  is equal to below
            # grad_data = ndl.Tensor(param.grad, dtype='float32').data
            # self.u[i] =self.momentum * self.u[i] \
            #     +(1-self.momentum)*grad_data
            # print(self.u[i].dtype)
            # param.data =(1-self.weight_decay*self.lr)*param.data - self.lr*self.u[i]


class Adam(Optimizer):
    def __init__(
        self,
        params,
        lr=0.01,
        beta1=0.9,
        beta2=0.999,
        eps=1e-8,
        weight_decay=0.0,
    ):
        super().__init__(params)
        self.lr = lr
        self.beta1 = beta1
        self.beta2 = beta2
        self.eps = eps
        self.weight_decay = weight_decay
        self.t = 0

        self.m = {}
        self.v = {}

    def step(self):
        ### BEGIN YOUR SOLUTION
        raise NotImplementedError()
        ### END YOUR SOLUTION
