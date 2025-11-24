from model import DigitClassifier
import torchvision
import torchvision.transforms as transforms
from torch.utils.data import DataLoader
import torch
from tqdm import tqdm
import torch.nn as nn
import matplotlib.pyplot as plt
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
mnist_trainset = torchvision.datasets.MNIST(root='./dataset', train=True, download=True, transform=transforms.ToTensor())
mnist_testset = torchvision.datasets.MNIST(root='./dataset', train=False, download=True, transform=transforms.ToTensor())
device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
print(f"Using device: {device}")
BATCH_SIZE = 64
LEARNING_RATE = 0.001
EPOCHS = 5

def train(loader, device) -> nn.Module:
    

    train_dataset = DataLoader(loader,batch_size=BATCH_SIZE, shuffle=True)

    model = DigitClassifier().to(device)
    criterion = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters())


    loss_list = []
    print(f"\nStarting training for {EPOCHS} epochs...")
    for epoch in range(EPOCHS):
        with tqdm(train_dataset, unit="batch", ncols=100) as tepoch:
            tepoch.set_description(f"Epoch {epoch+1}/{EPOCHS}")
            for data, targets in tepoch:
                data = data.to(device)
                targets = targets.to(device)

                # forward
                scores = model(data)
                loss = criterion(scores, targets)

                #backword
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

                tepoch.set_postfix(loss=loss.item())
                loss_list.append(loss.item())
            acc = check_accuracy(mnist_testset, model, device, toPrint = False)
            print(f'Acc after epoch {epoch}: {acc}')
    return model, loss_list

def check_accuracy(loader, model, device, toPrint = True):
    train_dataset = DataLoader(loader,batch_size=BATCH_SIZE, shuffle=True)
    num_correct = 0
    num_samples = 0
    model.eval() 
    
    with torch.no_grad():
        for x, y in train_dataset:
            x = x.to(device)
            y = y.to(device)
            
            scores = model(x)
            _, predictions = scores.max(1)
            num_correct += (predictions == y).sum()
            num_samples += predictions.size(0)
        
        acc = float(num_correct)/float(num_samples)*100
        if toPrint:
            print(f'Got {num_correct} / {num_samples} with accuracy {acc:.2f}%')
    model.train()
    return acc

model , loss_list = train(mnist_trainset, device)
print("\nTraining Complete.")
plt.plot(range(len(loss_list)), loss_list)
plt.show()
final_acc = check_accuracy(mnist_testset, model, device, toPrint = False)
print(f"Final Model Accuracy: {final_acc:.2f}%")
torch.save(model.state_dict(), "mnist_cnn_final.pth")
print("Model saved to 'mnist_cnn_final.pth'")