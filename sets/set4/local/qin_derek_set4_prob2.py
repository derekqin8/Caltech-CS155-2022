# -*- coding: utf-8 -*-
"""qin_derek_set4_prob2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1X0ubndLxRFhZ5_vloQmLcP0539Q6jQqB

# Problem 2 Sample Code

This sample code is meant as a guide on how to use PyTorch and how to use the relevant model layers. This not a guide on how to design a network and the network in this example is intentionally designed to have poor performace.
"""

# Commented out IPython magic to ensure Python compatibility.
import numpy as np
import matplotlib.pyplot as plt
# %matplotlib inline

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import datasets, transforms

# !pip list | grep torch

"""## Loading MNIST
The `torchvision` module contains links to many standard datasets. We can load the MNIST dataset into a `Dataset` object as follows:
"""

train_dataset = datasets.MNIST('./data', train=True, download=True,  # Downloads into a directory ../data
                               transform=transforms.ToTensor())
test_dataset = datasets.MNIST('./data', train=False, download=False,  # No need to download again
                              transform=transforms.ToTensor())

"""The `Dataset` object is an iterable where each element is a tuple of (input `Tensor`, target):"""

print(len(train_dataset), type(train_dataset[0][0]), type(train_dataset[0][1]))

"""We can convert images to numpy arrays and plot them with matplotlib:"""

plt.imshow(train_dataset[0][0][0].numpy(), cmap='gray')

print(train_dataset[0][0].shape)
print(len(train_dataset))
print(len(test_dataset))

"""## Network Definition
Let's instantiate a model and take a look at the layers.
"""

from torch.nn.modules.activation import Softmax
model = nn.Sequential(
    # In problem 2, we don't use the 2D structure of an image at all. Our network
    # takes in a flat vector of the pixel values as input.
    nn.Flatten(),  
    nn.Linear(784, 60),
    nn.ReLU(),
    nn.Dropout(0.1),
    nn.Linear(60, 40),
    nn.ReLU(),
    nn.Linear(40, 10)
)
model = model.cuda()
print(model)

"""## Training
We also choose an optimizer and a loss function.
"""

optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
loss_fn = nn.CrossEntropyLoss()

"""We could write our training procedure manually and directly index the `Dataset` objects, but the `DataLoader` object conveniently creates an iterable for automatically creating random minibatches:"""

train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=32, shuffle=True)
test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=32, shuffle=True)

"""We now write our backpropagation loop, training for 10 epochs."""

# Some layers, such as Dropout, behave differently during training
model.train()

for epoch in range(20):
    tot_loss = 0
    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.cuda(), target.cuda()
        # Erase accumulated gradients
        optimizer.zero_grad()

        # Forward pass
        output = model(data)

        # Calculate loss
        loss = loss_fn(output, target)

        tot_loss += loss.item()

        # Backward pass
        loss.backward()
        
        # Weight update
        optimizer.step()

    # Track loss each epoch
    print('Train Epoch: %d  Loss: %.4f' % (epoch + 1,  tot_loss / len(train_dataset)))

"""## Testing
We can perform forward passes through the network without saving gradients.
"""

# Putting layers like Dropout into evaluation mode
model.eval()

test_loss = 0
correct = 0

# Turning off automatic differentiation
with torch.no_grad():
    for data, target in test_loader:
        data, target = data.cuda(), target.cuda()
        output = model(data)
        test_loss += loss_fn(output, target).item()  # Sum up batch loss
        pred = output.argmax(dim=1, keepdim=True)  # Get the index of the max class score
        correct += pred.eq(target.view_as(pred)).sum().item()

test_loss /= len(test_loader.dataset)

print('Test set: Average loss: %.4f, Accuracy: %d/%d (%.4f)' %
      (test_loss, correct, len(test_loader.dataset),
       100. * correct / len(test_loader.dataset)))

