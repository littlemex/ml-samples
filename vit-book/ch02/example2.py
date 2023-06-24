import torch
import torch.nn as nn
import torch.optim as optim

# SimpleMlpクラスの定義（前述のコードと同じ）
class SimpleMlp(nn.Module):
    def __init__(self, vec_length=16, hidden_unit_1=8, hidden_unit_2=2):
        super(SimpleMlp, self).__init__()
        self.layer1 = nn.Linear(vec_length, hidden_unit_1)
        self.relu = nn.ReLU()
        self.layer2 = nn.Linear(hidden_unit_1, hidden_unit_2)

    def forward(self, x):
        out = self.layer1(x)
        out = self.relu(out)
        out = self.layer2(out)
        return out

# 学習データの準備
vec_length = 16
hidden_unit_1 = 8
hidden_unit_2 = 2
batch_size = 4

x_train = torch.randn(batch_size, vec_length)
y_train = torch.randn(batch_size, hidden_unit_2)

# SimpleMlpのインスタンス化
net = SimpleMlp(vec_length, hidden_unit_1, hidden_unit_2)

# 損失関数とオプティマイザの定義
criterion = nn.MSELoss()
optimizer = optim.SGD(net.parameters(), lr=0.01)

# 学習の実行
epochs = 100
for epoch in range(epochs):
    optimizer.zero_grad()  # 勾配の初期化

    # 順方向の計算
    outputs = net(x_train)
    
    # 損失の計算
    loss = criterion(outputs, y_train)
    
    # 逆方向の計算（勾配の計算）
    loss.backward()
    
    # パラメータの更新
    optimizer.step()

    # 途中結果の表示
    if (epoch+1) % 10 == 0:
        print(f"Epoch: {epoch+1}, Loss: {loss.item()}")

# 推論の実行
x_test = torch.randn(batch_size, vec_length)
outputs = net(x_test)
print(outputs)
