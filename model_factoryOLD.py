################################################################################
# CSE 253: Programming Assignment 4
# Code snippet by Ajit Kumar, Savyasachi
# Fall 2020
################################################################################
import torch.nn as nn
import torchvision.models as models

################################################################################
# Our imports:
from vocab import *
import torch
################################################################################

# Build and return the model here based on the configuration.
class EncoderCNN(nn.Module):
    def __init__(self, embed_size):
        super(EncoderCNN, self).__init__()
        resnet = models.resnet50(pretrained=True)
        for param in resnet.parameters():
            param.requires_grad_(False)
        
        modules = list(resnet.children())[:-1]
        self.resnet = nn.Sequential(*modules)
        self.embed = nn.Linear(resnet.fc.in_features, embed_size)

    def forward(self, images):
        features = self.resnet(images)
        features = features.view(features.size(0), -1)
        features = self.embed(features)
        return features

class DecoderLSTM(nn.Module):
    def __init__(self, embed_size, hidden_size, vocab_size, num_layers=1):
        super().__init__()
        self.embedding_layer = nn.Embedding(vocab_size, embed_size)
        
        self.lstm = nn.LSTM(input_size = embed_size,hidden_size = hidden_size,
                            num_layers = num_layers, batch_first = True)
        
        self.linear = nn.Linear(hidden_size, vocab_size)
    
    def forward(self, features, captions):
        captions = captions[:, :-1]
        embed = self.embedding_layer(captions)
        embed = torch.cat((features.unsqueeze(1), embed), dim = 1)
        lstm_outputs, _ = self.lstm(embed)
        out = self.linear(lstm_outputs)
        
        return out
    
    def generate_captions_deterministic(self, config_data, inputs, states = None):
        max_len = config_data['generation']['max_length']
        ids_storage = []
        
        for i in range(max_len):
            hiddens, states = self.lstm(inputs, states)
            
            hiddens = hiddens.squeeze(1)
            
            outputs = self.linear(hiddens)
            
            teach_prediction = outputs.argmax(1)
            prediction = outputs.argmax(1).cpu().detach().numpy()
            
            ids_storage.append(prediction)
            
            inputs = self.embedding_layer(teach_prediction)
            inputs = inputs.unsqueeze(1)
#             print(inputs.shape)
        return ids_storage
    
    def generate_captions_stocastic(self, config_data, inputs, states = None):
        max_len = config_data['generation']['max_length']
#         temperature = config_data['generation']['temperature']
        temperature = 0.1
        ids_storage = []
        
        for i in range(max_len):
            hiddens, states = self.lstm(inputs, states)
            
            ##
            hiddens = hiddens.squeeze(1)
            ##
            
            outputs = self.linear(hiddens)

            prediction = nn.functional.softmax(outputs.div(temperature)).multinomial(1).view(-1)
            ids_storage.append(prediction.cpu().detach().numpy())
            
            inputs = self.embedding_layer(prediction)
            inputs = inputs.unsqueeze(1)
            
            
            
        return ids_storage

class DecoderVanilla(nn.Module):
    def __init__(self, embed_size, hidden_size, vocab_size, num_layers=1):
        super().__init__()
        self.embedding_layer = nn.Embedding(vocab_size, embed_size)
        
        self.RNN = nn.RNN(input_size = embed_size,hidden_size = hidden_size,
                            num_layers = num_layers, batch_first = True)
        
        self.linear = nn.Linear(hidden_size, vocab_size)
    
    def forward(self, features, captions):
        captions = captions[:, :-1]
        embed = self.embedding_layer(captions)
        embed = torch.cat((features.unsqueeze(1), embed), dim = 1)
        RNN_outputs, _ = self.RNN(embed)
        out = self.linear(RNN_outputs)
        
        return out
    
    def generate_captions_deterministic(self, config_data, inputs, states = None):
        max_len = config_data['generation']['max_length']
        ids_storage = []
        
        for i in range(max_len):
            hiddens, states = self.RNN(inputs, states)
            
            hiddens = hiddens.squeeze(1)
            
            outputs = self.linear(hiddens)
            
            teach_prediction = outputs.argmax(1)
            prediction = outputs.argmax(1).cpu().detach().numpy()
            
            ids_storage.append(prediction)
            
            inputs = self.embedding_layer(teach_prediction)
            inputs = inputs.unsqueeze(1)
            
            
        return ids_storage
    
    def generate_captions_stocastic(self, config_data, inputs, states = None):
        max_len = config_data['generation']['max_length']
#         temperature = config_data['generation']['temperature']
        temperature = 2
        ids_storage = []
        
        for i in range(max_len):
            hiddens, states = self.RNN(inputs, states)
            
            ##
            hiddens = hiddens.squeeze(1)
            ##
            
            outputs = self.linear(hiddens)

            prediction = nn.functional.softmax(outputs.div(temperature)).multinomial(1).view(-1)
            ids_storage.append(prediction.cpu().detach().numpy())
            
            inputs = self.embedding_layer(prediction)
            inputs = inputs.unsqueeze(1)  
            
        return ids_storage
    
def get_model(config_data, vocab):
    hidden_size = config_data['model']['hidden_size']
    embedding_size = config_data['model']['embedding_size']
    model_type = config_data['model']['model_type']
    
    #create a vocab object

    # You may add more parameters if you want
    encoder = EncoderCNN(embedding_size)
    decoder = DecoderLSTM(embedding_size, hidden_size, vocab.__len__())
    print("successfully generated model...")
    return encoder, decoder

#create encoder, decoder
    
