import torch
import torch.nn as nn
from torchsummary import summary
from torchviz import make_dot

class VitInputLayer(nn.Module):
    def __init__(self,
        in_channels:int=3,
        emb_dim:int=384,
        num_patch_row:int=2,
        image_size:int=32
    ):
    
        super(VitInputLayer, self).__init__()
        self.in_channels=in_channels
        self.emb_dim=emb_dim
        self.num_patch_row=num_patch_row
        self.image_size=image_size

        self.num_patch = self.num_patch_row**2

        self.patch_size = int(self.image_size // self.num_patch_row)

        self.patch_emb_layer = nn.Conv2d(
            in_channels=self.in_channels,
            out_channels=self.emb_dim,
            kernel_size=self.patch_size,
            stride=self.patch_size
        )

        self.cls_token = nn.Parameter(
            torch.randn(1, 1, emb_dim)
        )

        self.pos_emb = nn.Parameter(
            torch.randn(1, self.num_patch+1, emb_dim)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        x: 入力画像 (B, C, H, W)
        z_0: ViTへの入力 (B, N, D)
        """
        z_0 = self.patch_emb_layer(x)
        z_0 = z_0.flatten(2)
        z_0 = z_0.transpose(1, 2)
        z_0 = torch.cat([self.cls_token.repeat(repeats=(x.size(0),1,1)), z_0], dim=1)
        z_0 = z_0 + self.pos_emb

        return z_0

batch_size, channel, height, width = 2, 3, 32, 32
x = torch.randn(batch_size, channel, height, width)
input_layer = VitInputLayer(num_patch_row=2)
z_0 = input_layer(x)
print(z_0.shape)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = VitInputLayer()
summary(model.to(device), input_size=(3, 32, 32))

# required graphviz
image = make_dot(z_0, show_attrs=True, show_saved=True)
image.format = "png"
image.save("VitInput.png")