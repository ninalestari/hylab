import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
import random
import os

# Load data
data_path = "D:/labwork/shakespeare.txt"  # Path to your text file
with open(data_path, 'r') as file:
    text = file.read()

# Create a character-level vocabulary
chars = sorted(list(set(text)))
vocab_size = len(chars)
char_to_idx = {ch: idx for idx, ch in enumerate(chars)}
idx_to_char = {idx: ch for idx, ch in enumerate(chars)}

# Encode the text
encoded_text = np.array([char_to_idx[ch] for ch in text])

class TransformerModel(nn.Module):
    def __init__(self, vocab_size, d_model, nhead, nhid, nlayers, dropout=0.5):
        super(TransformerModel, self).__init__()
        self.model_type = 'Transformer'
        self.src_mask = None
        self.pos_encoder = nn.Embedding(5000, d_model)
        self.encoder = nn.Embedding(vocab_size, d_model)
        self.transformer = nn.Transformer(d_model, nhead, nlayers, nlayers, nhid, dropout)
        self.decoder = nn.Linear(d_model, vocab_size)
        self.d_model = d_model
        self.init_weights()

    def init_weights(self):
        initrange = 0.1
        self.encoder.weight.data.uniform_(-initrange, initrange)
        self.decoder.bias.data.zero_()
        self.decoder.weight.data.uniform_(-initrange, initrange)

    def forward(self, src, src_mask):
        src = self.encoder(src) * np.sqrt(self.d_model)
        src = self.pos_encoder(src)
        output = self.transformer(src, src, src_mask)
        output = self.decoder(output)
        return output

def train(model, dataloader, criterion, optimizer, epochs):
    model.train()
    for epoch in range(epochs):
        total_loss = 0
        for i, batch in enumerate(dataloader):
            data, targets = batch
            optimizer.zero_grad()
            output = model(data, None)
            loss = criterion(output.view(-1, vocab_size), targets.view(-1))
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f'Epoch {epoch + 1}, Loss: {total_loss / len(dataloader)}')

# Create the dataset and dataloader
class TextDataset(Dataset):
    def __init__(self, text, seq_length):
        self.text = text
        self.seq_length = seq_length

    def __len__(self):
        return len(self.text) - self.seq_length

    def __getitem__(self, idx):
        return (
            torch.tensor(self.text[idx:idx + self.seq_length], dtype=torch.long),
            torch.tensor(self.text[idx + 1:idx + self.seq_length + 1], dtype=torch.long)
        )

seq_length = 100  # Sequence length for training
batch_size = 32
dataset = TextDataset(encoded_text, seq_length)
dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

# Initialize the model, criterion, and optimizer
d_model = 256
nhead = 8
nhid = 512
nlayers = 2
model = TransformerModel(vocab_size, d_model, nhead, nhid, nlayers)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Train the model
epochs = 10
train(model, dataloader, criterion, optimizer, epochs)

def train(model, dataloader, criterion, optimizer, epochs):
    model.train()
    for epoch in range(epochs):
        total_loss = 0
        for i, batch in enumerate(dataloader):
            data, targets = batch
            optimizer.zero_grad()
            output = model(data, None)
            loss = criterion(output.view(-1, vocab_size), targets.view(-1))
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f'Epoch {epoch + 1}, Loss: {total_loss / len(dataloader)}')

# Create the dataset and dataloader
class TextDataset(Dataset):
    def __init__(self, text, seq_length):
        self.text = text
        self.seq_length = seq_length

    def __len__(self):
        return len(self.text) - self.seq_length

    def __getitem__(self, idx):
        return (
            torch.tensor(self.text[idx:idx + self.seq_length], dtype=torch.long),
            torch.tensor(self.text[idx + 1:idx + self.seq_length + 1], dtype=torch.long)
        )

seq_length = 100  # Sequence length for training
batch_size = 32
dataset = TextDataset(encoded_text, seq_length)
dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

# Initialize the model, criterion, and optimizer
d_model = 256
nhead = 8
nhid = 512
nlayers = 2
model = TransformerModel(vocab_size, d_model, nhead, nhid, nlayers)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Train the model
epochs = 10
train(model, dataloader, criterion, optimizer, epochs)

def generate_text(model, start_str, gen_length):
    model.eval()
    input_str = start_str
    input_data = torch.tensor([char_to_idx[ch] for ch in input_str], dtype=torch.long).unsqueeze(1)
    generated_text = start_str

    for _ in range(gen_length):
        with torch.no_grad():
            output = model(input_data, None)
            next_char = idx_to_char[output[-1, 0].argmax().item()]
            generated_text += next_char
            next_input = torch.tensor([[char_to_idx[next_char]]], dtype=torch.long)
            input_data = torch.cat((input_data, next_input))

    return generated_text

# Generate text
start_str = "To be, or not to be, that is the question:"
gen_length = 200
generated_text = generate_text(model, start_str, gen_length)
print(generated_text)

