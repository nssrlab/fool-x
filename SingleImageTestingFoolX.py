
import torchvision.transforms as transforms
import numpy as np
import matplotlib.pyplot as plt
import torch
import torchvision.models as models
from PIL import Image
from foolx import foolx
import os
import time

torch.device('cpu')

net = models.resnet34(pretrained=True)
#net = models.alexnet(pretrained=True)
# Switch to evaluation mode
net.eval()

im_orig = Image.open('new/ILSVRC2017_test_00004324.JPEG').convert('RGB')

mean = [ 0.485, 0.456, 0.406 ]
std = [ 0.229, 0.224, 0.225 ]

# Remove the mean
im = transforms.Compose([
    transforms.Scale(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean = mean,
                         std = std)])(im_orig)

start_time = time.time()
r, loop_i, label_orig, label_pert, pert_image, pert, newf_k = foolx(im, net, 0.005)
end_time = time.time()
execution_time = end_time - start_time
print("execution time = " + str(execution_time))

labels = open(os.path.join('synset_words.txt'), 'r').read().split('\n')

str_label_orig = labels[np.int(label_orig)].split(',')[0]
str_label_pert = labels[np.int(label_pert)].split(',')[0]

print("Original label = ", str_label_orig)
print("Perturbed label = ", str_label_pert)

def clip_tensor(A, minv, maxv):
    A = torch.max(A, minv*torch.ones(A.shape))
    A = torch.min(A, maxv*torch.ones(A.shape))
    return A

clip = lambda x: clip_tensor(x, 0, 255)


tf = transforms.Compose([transforms.Normalize(mean=[0, 0, 0], std=list(map(lambda x: 1 / x, std))),
                        transforms.Normalize(list(map(lambda x: -x, mean)), std=[1, 1, 1]),
                        transforms.Lambda(clip),
                        transforms.ToPILImage(),
                        transforms.CenterCrop(224)])

imagetransform = transforms.Compose([transforms.Normalize(mean=[0, 0, 0], std=list(map(lambda x: 1 / x, std))),
                        transforms.Normalize(list(map(lambda x: -x, mean)), std=[1, 1, 1]),
                        transforms.Lambda(clip)])

tensortransform = transforms.Compose([transforms.Scale(256),
                        transforms.CenterCrop(224),
                        transforms.ToTensor(),
                        transforms.Normalize(mean=[0, 0, 0], std=list(map(lambda x: 1 / x, std))),
                        transforms.Normalize(list(map(lambda x: -x, mean)), std=[1, 1, 1]),
                        transforms.Lambda(clip)])
plt.figure()
plt.imshow(tf(im.cpu()))
plt.title(str_label_orig)
plt.show()

plt.figure()
plt.imshow(tf(pert_image.cpu()[0]))
plt.title(str_label_pert)
plt.show()
print(loop_i)

plt.figure()
plt.imshow(tf(pert.cpu()[0]))
plt.show()
print(imagetransform(pert_image.cpu()[0]))
print("im orig")
print(tensortransform(im_orig))
print("difference:")
diff = imagetransform(pert_image.cpu()[0]) - tensortransform(im_orig)
print(diff)
fro = np.linalg.norm(diff.numpy())
print(fro)
print(torch.mean(torch.abs(diff)))