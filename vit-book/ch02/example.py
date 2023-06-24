import torch
import torch.nn as nn

class SimpleMlp(nn.Module):
    def __init__(self,
        vec_length:int=16,
        hidden_unit_1:int=8,
        hidden_unit_2:int=2):

        super(SimpleMlp, self).__init__()

        self.layer1 = nn.Linear(vec_length, hidden_unit_1)
        self.relu = nn.ReLU()
        self.layer2 = nn.Linear(hidden_unit_1, hidden_unit_2)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out = self.layer1(x)
        out = self.relu(out)
        out = self.layer2(out)
        return out

vec_length = 16
hidden_unit_1 = 8
hidden_unit_2 = 2
batch_size = 4

x = torch.randn(batch_size, vec_length)
net = SimpleMlp(vec_length, hidden_unit_1, hidden_unit_2)
out = net(x)
print(out)
print(out.shape)