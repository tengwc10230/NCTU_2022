import requests
import time
import numpy as np

import torch
import torch.nn as nn
import torch.nn.functional as F

class Net(nn.Module):
    """Model (simple CNN adapted from 'PyTorch: A 60 Minute Blitz')"""

    def __init__(self) -> None:
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(3, 6, 5)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.fc1 = nn.Linear(16 * 5 * 5, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 16 * 5 * 5)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        return self.fc3(x)

    def get_model_hash():
        files = {
            'weight': (open('./round-3-weights.npz', 'rb')),
        }

        response = requests.post('https://ipfs.infura.io:5001/api/v0/add', files=files)
        p = response.json()
        hash = p['Hash']
        return hash

    def load_model_by_hash(hash):
        params = (
            ('arg', hash),
        )
        response = requests.post('https://ipfs.infura.io:5001/api/v0/block/get', params=params)
        print(response.text)

# # TEST 0
if __name__ == "__main__":
    model_hash = Net.get_model_hash()
    Net.load_model_by_hash(model_hash)
    weights_data = np.load("./round-1-weights.npz", allow_pickle=True)
    lst = weights_data.files
    for item in lst:
        print(item)
        print(weights_data[item])
# model = Net()
# model.load_state_dict(torch.load('./round-3-weights.npz'))

# # TEST 1
# WEIGHT = 'Hello World!'
# start_time = time.time()
# print('hash:', Net.get_model_hash())
# Net.load_model_by_hash(Net.get_model_hash(WEIGHT))
# print('time cost:', time.time()-start_time)

# # TEST 2
# start_time = time.time()
# print('hash:', Net.get_model_hash())
# Net.load_model_by_hash(str(Net.get_model_hash('Hello World')))
# print('time cost:', time.time()-start_time)

########### Output 1 ###########
# hash: Qmf1rtki74jvYmGeqaaV51hzeiaa6DyWc98fzDiuPatzyy
    
# Hello World!

# time cost: 2.7858269214630127
################################
    
########### Output 2 ###########
# hash: QmUXTtySmd7LD4p6RG6rZW6RuUuPZXTtNMmRQ6DSQo3aMw

# Hello World

# time cost: 2.6761679649353027
################################