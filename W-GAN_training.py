import torch
import torch.nn as nn
import torchvision
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import torchvision.transforms as transforms
import torchvision.datasets as datasets
from W_GAN import Critic, Generator, initialize_weight
from torchvision.utils import save_image

# hyperparameter
batch_size = 64
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
lr_ = 5e-5
epochs = 100
image_chenel = 1
feature_dim = 4
z_dim = 100
weight_clip = 0.01
critic_iteration = 1
dis_ = Critic(image_chenel, feature_dim).to(device)
gen_ = Generator(z_dim, image_chenel, feature_dim).to(device)
initialize_weight(dis_)
initialize_weight(gen_)
optimizer_critic = optim.RMSprop(dis_.parameters(), lr=lr_)
optimizer_gen = optim.RMSprop(gen_.parameters(), lr=lr_)
transform = transforms.Compose([transforms.Resize((64, 64)), transforms.ToTensor(),
                                transforms.Normalize([0.5 for _ in range(image_chenel)],
                                                     [0.5 for _ in range(image_chenel)])])
dataset = torchvision.datasets.MNIST(root='MNIST/', transform=transform, download=True)
data_loader = DataLoader(dataset=dataset, shuffle=True, batch_size=batch_size)
fix_noise = torch.randn(40, 100, 1, 1)
for epoch in range(epochs):
    for _, (image, target) in enumerate(data_loader):

        for i in range(critic_iteration):
            noise = torch.randn((batch_size, z_dim, 1, 1))
            fake_image = gen_(noise)
            real_lable = dis_(image).reshape(-1)
            fake_lable = dis_(fake_image).reshape(-1)
            loss_dis = -(torch.mean(real_lable) - torch.mean(fake_lable))
            optimizer_critic.zero_grad()
            loss_dis.backward(retain_graph=True)
            optimizer_critic.step()
            for p in dis_.parameters():
                p.data.clamp_(-weight_clip,weight_clip)

        #############
        f = dis_(fake_image).reshape(-1)
        loss_gen = -(torch.mean(f))
        optimizer_gen.zero_grad()
        loss_gen.backward()
        optimizer_gen.step()

    print(f'in epoch {epoch}, the dis loss is {loss_dis:4f} and the gen loss is {loss_gen:4f}')
    with torch.no_grad():
        fake_image_ = gen_(fix_noise)
        fake_image_grid = torchvision.utils.make_grid(fake_image_, normalize=True)
        path = 'WGAN_Results/' + 'image_' + str(epoch) + '.png'
        save_image(fake_image_grid, path)
