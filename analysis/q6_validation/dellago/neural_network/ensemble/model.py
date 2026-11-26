import torch
import torch.nn as nn


class NucleationMLP(nn.Module):
    def __init__(self, input_features=22):
        super().__init__()
        self.network = nn.Sequential(

            # hidden layer 1
            nn.Linear(input_features, 96),
            nn.BatchNorm1d(96),
            nn.ELU(),
            nn.Dropout(p=0.1),

            # hidden layer 2
            nn.Linear(96, 48),
            nn.BatchNorm1d(48),
            nn.ELU(),
            nn.Dropout(p=0.1),

            # hidden layer 3
            nn.Linear(48, 16),
            nn.BatchNorm1d(16),
            nn.ELU(),
            nn.Dropout(p=0.1),

            #output layer
            nn.Linear(16, 1)
        )

    def forward(self, x):
        return self.network(x).squeeze(-1)
