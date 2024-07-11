# from .vavanilla_resnet_cifar import vanilla_resnet20
from .vanilla_models.vanilla_resnet_imagenet import resnet18
from .quan_resnet_imagenet import resnet18_quan, resnet34_quan
from .quan_alexnet_imagenet import alexnet_quan


############## ResNet for CIFAR-10 ###########
from .vanilla_models.vanilla_resnet_cifar import vanilla_resnet20
from .quan_resnet_cifar import resnet18_quan
from .bin_resnet_cifar import resnet18_bin

############## VGG for CIFAR #############

from .vanilla_models.vanilla_vgg8_cifar import vgg8_bn, vgg8
from .quan_vgg8_cifar import vgg8_bn_quan, vgg8_quan
from .bin_vgg8_cifar import vgg8_bn_bin


############# Mobilenet for ImageNet #######
from .vanilla_models.vanilla_mobilenet_imagenet import mobilenet_v2

from .quan_mobilenet_imagenet import mobilenet_v2_quan