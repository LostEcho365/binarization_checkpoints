import math
import torch

import torch.nn as nn
import torch.nn.init as init
import math
import torch.nn.functional as F

__all__ = [
    'VGG', 'vgg8', 'vgg8_bn',
]


class _bin_func(torch.autograd.Function):

    @staticmethod
    def forward(ctx, input, mu):
        
        ctx.mu = mu 
        output = input.clone().zero_()
        output[input.ge(0)] = 1
        output[input.lt(0)] = -1

        return output

    @staticmethod
    def backward(ctx, grad_output):
        grad_input = grad_output.clone()/ctx.mu
        return grad_input, None
    
w_bin = _bin_func.apply


class quan_Conv2d(nn.Conv2d):
    def __init__(self,
                 in_channels,
                 out_channels,
                 kernel_size,
                 stride=1,
                 padding=0,
                 dilation=1,
                 groups=1,
                 bias=True):
        super(quan_Conv2d, self).__init__(in_channels,
                                          out_channels,
                                          kernel_size,
                                          stride=stride,
                                          padding=padding,
                                          dilation=dilation,
                                          groups=groups,
                                          bias=bias)

    def forward(self, input):
        if self.training:
            try:
                with torch.no_grad():
                    weight_change = (self.bin_weight - w_bin(self.weight,1)).abs()
                    self.bin_weight_change = weight_change.sum().item()
                    self.bin_weight_change_ratio = self.bin_weight_change / self.weight.numel()
                    # print(self.bin_weight_change, self.bin_weight_change_ratio)
            except:
                pass
        
        with torch.no_grad():
            mu = self.weight.abs().mean()
        
        self.bin_weight = w_bin(self.weight, mu)
        output = F.conv2d(input, self.bin_weight* mu, self.bias, self.stride, self.padding, self.dilation, self.groups)
        
        return output 

class quan_Linear(nn.Linear):
    def __init__(self, in_features, out_features, bias=True):
        super(quan_Linear, self).__init__(in_features, out_features, bias=bias)
        
    def forward(self, input):
        if self.training:
            try:
                with torch.no_grad():
                    weight_change = (self.bin_weight - w_bin(self.weight,1)).abs()
                    self.bin_weight_change = weight_change.sum().item()
                    self.bin_weight_change_ratio = self.bin_weight_change  / self.weight.numel()
                    # print(self.bin_weight_change, self.bin_weight_change_ratio)
            except:
                pass

        with torch.no_grad():
            mu = self.weight.abs().mean()
                    
        self.bin_weight = w_bin(self.weight, mu)
        output = F.linear(input, self.bin_weight * mu, self.bias)

        return output




class VGG(nn.Module):
    '''
    VGG model 
    '''
    def __init__(self, features, num_classes):
        super(VGG, self).__init__()
        self.features = features
        self.classifier = nn.Sequential(
            nn.Dropout(),
            quan_Linear(2048, 512),
            nn.ReLU(True),
            nn.Dropout(),
            quan_Linear(512, 512),
            nn.ReLU(True),
            quan_Linear(512, num_classes),
        )
         # Initialize weights
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                n = m.kernel_size[0] * m.kernel_size[1] * m.out_channels
                m.weight.data.normal_(0, math.sqrt(2. / n))
                m.bias.data.zero_()


    def forward(self, x):
        x = self.features(x)
        x = x.view(x.size(0), -1)
        x = self.classifier(x)
        return x


def make_layers(cfg, batch_norm=False):
    layers = []
    in_channels = 3
    for v in cfg:
        if v == 'M':
            layers += [nn.MaxPool2d(kernel_size=2, stride=2)]
        else:
            conv2d = quan_Conv2d(in_channels, v, kernel_size=3, padding=1)
            if batch_norm:
                layers += [conv2d, nn.BatchNorm2d(v), nn.ReLU(inplace=True)]
            else:
                layers += [conv2d, nn.ReLU(inplace=True)]
            in_channels = v
    return nn.Sequential(*layers)


cfg = {
    'A': [64, 'M', 128, 'M', 256, 'M', 512, 'M'],
}


def vgg8_bin(num_classes=10):
    """VGG 8-layer model (configuration "A")"""
    return VGG(make_layers(cfg['A']), num_classes)


def vgg8_bn_bin(num_classes=10):
    """VGG 8-layer model (configuration "A") with batch normalization"""
    return VGG(make_layers(cfg['A'], batch_norm=True), num_classes)
