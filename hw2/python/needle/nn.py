"""The module.
"""
from typing import List, Callable, Any
from needle.autograd import Tensor
from needle import ops
import needle.init as init
import numpy as np


class Parameter(Tensor):
    """A special kind of tensor that represents parameters."""


def _unpack_params(value: object) -> List[Tensor]:
    if isinstance(value, Parameter):
        return [value]
    elif isinstance(value, Module):
        return value.parameters()
    elif isinstance(value, dict):
        params = []
        for k, v in value.items():
            params += _unpack_params(v)
        return params
    elif isinstance(value, (list, tuple)):
        params = []
        for v in value:
            params += _unpack_params(v)
        return params
    else:
        return []


def _child_modules(value: object) -> List["Module"]:
    if isinstance(value, Module):
        modules = [value]
        modules.extend(_child_modules(value.__dict__))
        return modules
    if isinstance(value, dict):
        modules = []
        for k, v in value.items():
            modules += _child_modules(v)
        return modules
    elif isinstance(value, (list, tuple)):
        modules = []
        for v in value:
            modules += _child_modules(v)
        return modules
    else:
        return []




class Module:
    def __init__(self):
        self.training = True

    def parameters(self) -> List[Tensor]:
        """Return the list of parameters in the module."""
        return _unpack_params(self.__dict__)

    def _children(self) -> List["Module"]:
        return _child_modules(self.__dict__)

    def eval(self):
        self.training = False
        for m in self._children():
            m.training = False

    def train(self):
        self.training = True
        for m in self._children():
            m.training = True

    def __call__(self, *args, **kwargs):
        return self.forward(*args, **kwargs)


class Identity(Module):
    def forward(self, x):
        return x


class Linear(Module):
    def __init__(self, in_features, out_features, bias=True, device=None, dtype="float32"):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        ### BEGIN YOUR SOLUTION
        self.weight= Parameter(init.kaiming_uniform(in_features, out_features, requires_grad=True))
        if bias:
            self.bias = Parameter(init.kaiming_uniform(out_features, 1, requires_grad=True).reshape((1, out_features)))
        else:
            self.bias = None
        ### END YOUR SOLUTION

    def forward(self, X: Tensor) -> Tensor:
        ### BEGIN YOUR SOLUTION
        X_mul_weight = X @ self.weight
        if self.bias:
            return X_mul_weight + self.bias.broadcast_to(X_mul_weight.shape)
        else:
            return X_mul_weight
        raise NotImplementedError()
        ### END YOUR SOLUTION



class Flatten(Module):
    def forward(self, X):
        ### BEGIN YOUR SOLUTION
        return X.reshape((X.shape[0], -1))
        raise NotImplementedError()
        ### END YOUR SOLUTION


class ReLU(Module):
    def forward(self, x: Tensor) -> Tensor:
        ### BEGIN YOUR SOLUTION
        return ops.relu(x)
        raise NotImplementedError()
        ### END YOUR SOLUTION


class Sequential(Module):
    def __init__(self, *modules):
        super().__init__()
        self.modules = modules

    def forward(self, x: Tensor) -> Tensor:
        ### BEGIN YOUR SOLUTION
        for module in self.modules:
            x=module(x)
        return x
        #raise NotImplementedError()
        ### END YOUR SOLUTION


class SoftmaxLoss(Module):
    def forward(self, logits: Tensor, y: Tensor):
        ### BEGIN YOUR SOLUTION
        one_hot_y =init.one_hot(logits.shape[1],y)
        zy=(logits*one_hot_y).sum()
        b=ops.logsumexp(logits,axes=(1,)).sum()
        return (b-zy)/logits.shape[0]
        raise NotImplementedError()
        ### END YOUR SOLUTION



class BatchNorm1d(Module):
    def __init__(self, dim, eps=1e-5, momentum=0.1, device=None, dtype="float32"):
        super().__init__()
        self.dim = dim
        self.eps = eps
        self.momentum = momentum
        ### BEGIN YOUR SOLUTION
        self.weight = Parameter(init.ones(self.dim, requires_grad=True))
        self.bias = Parameter(init.zeros(self.dim, requires_grad=True))
        self.running_mean = init.zeros(self.dim)
        self.running_var = init.ones(self.dim)
        #raise NotImplementedError()
        ### END YOUR SOLUTION


    def forward(self, x: Tensor) -> Tensor:
        ### BEGIN YOUR SOLUTION
        mean_x=x.sum(axes=(0,))/x.shape[0]
        x_hat=x-mean_x.broadcast_to(x.shape)
        vars_x=(x_hat**2).sum(axes=(0,))/x.shape[0]
        if self.training:
            self.running_mean=(1-self.momentum)*self.running_mean+self.momentum*mean_x.data
            self.running_var=(1-self.momentum)*self.running_var+self.momentum*vars_x.data
            x_std=((vars_x+self.eps)**0.5).broadcast_to(x.shape)
            return  self.weight.broadcast_to(x.shape)* (x_hat/x_std)+self.bias.broadcast_to(x.shape)
        else:
            x_std=(x-self.running_mean)/(self.running_var+self.eps)**0.5
            return self.weight.broadcast_to(x.shape)*x_std+self.bias.broadcast_to(x.shape)
        raise NotImplementedError()
        ### END YOUR SOLUTION


class LayerNorm1d(Module):
    def __init__(self, dim, eps=1e-5, device=None, dtype="float32"):
        super().__init__()
        self.dim = dim
        self.eps = eps
        self.weight = Parameter(init.ones(self.dim, requires_grad=True))
        # NOTE bias initialized to 0!!!
        self.bias = Parameter(init.zeros(self.dim, requires_grad=True))
        ### BEGIN YOUR SOLUTION
        ### END YOUR SOLUTION

    def forward(self, x: Tensor) -> Tensor:
        ### BEGIN YOUR SOLUTION
        mean_x=x.sum(axes=(1,)).reshape((x.shape[0],1))/x.shape[1]
        mean_x=mean_x.broadcast_to(x.shape)
        print(mean_x.shape)
        x_hat=(x-mean_x)
        vars_x=(x_hat**2).sum(axes=(1,)).reshape((x.shape[0],1))/x.shape[1]
        x_std=((vars_x+self.eps)**0.5).broadcast_to(x.shape)
        return  self.weight.broadcast_to(x.shape)* (x_hat/x_std)+self.bias.broadcast_to(x.shape)
        ### END YOUR SOLUTION


class Dropout(Module):
    def __init__(self, p = 0.5):
        super().__init__()
        self.p = p

    def forward(self, x: Tensor) -> Tensor:
        ### BEGIN YOUR SOLUTION
        if self.training:
            drop=init.randb(*x.shape, p=1-self.p)
            return (x*drop)/(1-self.p)
        else:
            return x
        raise NotImplementedError()
        ### END YOUR SOLUTION


class Residual(Module):
    def __init__(self, fn: Module):
        super().__init__()
        self.fn = fn

    def forward(self, x: Tensor) -> Tensor:
        ### BEGIN YOUR SOLUTION
        return self.fn(x)+x
        raise NotImplementedError()
        ### END YOUR SOLUTION



