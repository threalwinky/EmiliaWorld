import json
import nltk
from nltk.stem.porter import PorterStemmer
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
stemmer = PorterStemmer()

def tokenize(sentence):
    return nltk.word_tokenize(sentence)
def stem(words):
    return stemmer.stem(words.lower())
def bag_of_words(tokenized_sentence, all_words):
    tokenized_sentence = [stem(w) for w in tokenized_sentence]
    bag = np.zeros(len(all_words), dtype=np.float32)
    for (idx, w) in enumerate(all_words):
        if w in tokenized_sentence:
            bag[idx] = 1.0
    return bag
class ChatDataSet(Dataset):
    def __init__(self):
        self.n_samples = len(X_Train)
        self.x_data = X_Train
        self.y_data = Y_Train
    def __getitem__(self, idx):
        return self.x_data[idx], self.y_data[idx]
    def __len__(self):
        return self.n_samples
class NeuralNet(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super(NeuralNet, self).__init__()
        self.l1 = nn.Linear(input_size, hidden_size)
        self.l2 = nn.Linear(hidden_size, hidden_size)
        self.l3 = nn.Linear(hidden_size, num_classes)
        self.relu = nn.ReLU()
    def forward(self, x):
        out = self.l1(x)
        out = self.relu(out)
        out = self.l2(out)
        out = self.relu(out)
        out = self.l3(out)
        return out
    
f = open('intents.json', 'r', encoding="utf8")
intents = json.load(f)
all_words, tags, xy = [], [], []
for intent in intents['intents']:
    tag = intent['tag']
    tags.append(tag)
    for pattern in intent['patterns']:
        w = tokenize(pattern)
        all_words.extend(w)
        xy.append((w, tag))

ignore_words = ['?', '!', '.', ',', '*', '(', ')']
all_words = [stem(w) for w in all_words if w not in ignore_words]
all_words = sorted(set(all_words))
tags = sorted(set(tags))

X_Train = []
Y_Train = []

for (pattern_sentence, tag) in xy:
    bag = bag_of_words(pattern_sentence, all_words)
    X_Train.append(bag)
    label = tags.index(tag)
    Y_Train.append(label)

X_Train = np.array(X_Train)
Y_Train = np.array(Y_Train)

# sentence = ['hello', 'how', 'are', 'you']
# words = ['hi', 'hello', 'I', 'you', 'thank', 'bye']
# print(bag_of_words(sentence, words))

batch_size = 8
hidden_size = 8
output_size = len(tags)
input_size = len(X_Train[0])
learning_rate = 0.001
num_epochs = 1000

dataset = ChatDataSet()
train_loader = DataLoader(dataset=dataset, batch_size=batch_size, shuffle=True, num_workers=0)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = NeuralNet(input_size, hidden_size, output_size).to(device)
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
for epoch in range(num_epochs):
    for (words, labels) in train_loader:
        words = words.to(device)
        labels = labels.to(dtype=torch.long).to(device)
        #forward
        outputs = model(words)
        loss = criterion(outputs, labels)
        #backward and optimizer step
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

data = {
    "model_state": model.state_dict(),
    "input_size": input_size,
    "hidden_size": hidden_size,
    "output_size": output_size,
    "all_words": all_words,
    "tags": tags
}

FILE = "data.pth"
torch.save(data, FILE)
print('Training complete')