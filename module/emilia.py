import random
import json
import nltk
from nltk.stem.porter import PorterStemmer
import numpy as np
import torch
import torch.nn as nn
import unidecode
from datetime import *
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

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

with open('intents.json', 'r', encoding="utf8") as json_data:
    intents = json.load(json_data)

FILE = "data.pth"
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()


def calendar():
	time_1 = datetime.now()
	time_2 = datetime.strptime('2024:7:8:7:00:00',"%Y:%m:%d:%H:%M:%S")

	time_interval = time_2 - time_1
	time_interval_list = (str(time_interval)).split()
	# print(time_interval_list)
	return "Còn " + time_interval_list[0] + " ngày, " + time_interval_list[2][:-13] + " giờ, " + time_interval_list[2][-12:-10] + " phút, " + time_interval_list[2][-9:-7] + " giây nữa là thi THPT quốc gia rồi đó."

template_format = {
    'ttm' : 'Joe Biden',
    'hour' : datetime.now().strftime("%H"),
    'minute' : datetime.now().strftime("%M"),
    'second' : datetime.now().strftime("%S"),
    'time_interval' : calendar()
}

print("Let's chat! (type 'quit' to exit)")
def get_emilia_response(message):
    message = tokenize(message)
    reply = ''
    X = bag_of_words(message, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)
    output = model(X)
    _, predicted = torch.max(output, dim=1)
    tag = tags[predicted.item()]
    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]
    if prob.item() > 0.75:
        for intent in intents['intents']:
            if tag == intent["tag"]:
                result = random.choice(intent['responses'])
                reply = result.format(**template_format)
    else:
        reply_don_know = ['Hong hiểu nói gì luôn á', 'Gì vậy bạn', 'Hả', 'Hong hiểu']
        reply = random.choice(reply_don_know)
    return reply