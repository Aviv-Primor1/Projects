import numpy as np
from scipy.stats import t
import torch
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
import torch.nn as nn
from torchvision.models import resnet18
from torch.optim import Adam
import torchvision.transforms as transforms
import matplotlib.pyplot as plt

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class StudentT_NLLLoss(nn.Module):
    def _init_(self):
        super(StudentT_NLLLoss, self)._init_()

    def forward(self, y_pred, y_true):
        # Calculate the negative log-likelihood loss
        loss = torch.lgamma((y_true + 1) / 2) - torch.lgamma(y_true / 2)
        loss += 0.5 * (torch.log(y_true * np.pi) + torch.log1p((y_pred - y_true)**2 / y_true))
        loss = loss.mean()

        return loss
def generate_hyperspectral_image(num_of_sampels: int, size_of_image: int = 224) -> (list, list):
    """
    Generate a random hyperspectral image
    :param num_of_sampels: number of samples to generate
    :return: a list of images and a list of labels
    """
    image_sizes = (size_of_image,size_of_image)
    images = []
    labels = []

    for _ in range(num_of_sampels):
        dof = np.random.uniform(2, 30, 1)
        image = t.rvs(dof, size=image_sizes)
        images.append(image)
        labels.append(dof)

    return images, labels


transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((224, 224)),
    transforms.ToTensor()
])


class HyperspectralDataset(Dataset):
    def __init__(self, images, labels):
        self.images = images
        self.labels = labels
        self.transform = transform

    def __len__(self):
        return len(self.images)

    def __getitem__(self, index):
        image = torch.from_numpy(self.images[index]).double()
        label = torch.from_numpy(self.labels[index]).double()

        if self.transform:
            image = self.transform(image)

        return image, label


class DOFNet(nn.Module):
    def __init__(self):
        super(DOFNet, self).__init__()

        self.features = nn.Sequential(
            nn.Sequential(
                nn.Conv2d(in_channels=1, out_channels=16, kernel_size=3, stride=1, padding=1),
                nn.ReLU(),
                nn.MaxPool2d(kernel_size=2, stride=2),
                nn.Dropout(p=0.1)
            ),
            nn.Sequential(
                nn.Conv2d(in_channels=16, out_channels=32, kernel_size=3, stride=1, padding=1),
                nn.ReLU(),
                nn.MaxPool2d(kernel_size=2, stride=2),
                nn.Dropout(p=0.1)
            ),
            nn.Sequential(
                nn.Conv2d(in_channels=32, out_channels=64, kernel_size=3, stride=1, padding=1),
                nn.ReLU(),
                nn.MaxPool2d(kernel_size=2, stride=2),
                nn.Dropout(p=0.1)
            )
        )

        self.classifier = nn.Sequential(
            nn.Linear(64 * 28 * 28, 64*28),
            nn.ReLU(),
            nn.Dropout(p=0.1),
            nn.Linear(64 * 28, 64),
            nn.ReLU(),
            nn.Linear(64, 1)
        )

    def forward(self, x):
        x = self.features(x)
        x = x.view(1, -1)
        x = self.classifier(x)

        return x


def train(model, train_dataloader, test_dataloader, criterion, optimizer, num_epochs):

    train_losses = []  # To store the training loss values
    val_losses = []  # To store the validation loss values
    best_valid_loss = np.inf

    for epoch in range(num_epochs):
        model.train()

        train_loss = 0.0
        idx = 0

        # Training loop
        model.train()
        for inputs, labels in train_dataloader:
            optimizer.zero_grad()

            inputs = inputs.to(device)
            labels = labels.to(device)

            outputs = model(inputs)
            loss = criterion(outputs, labels)

            loss.backward()
            optimizer.step()

            train_loss += loss.item() * inputs.size(0)
            idx += 1

            if idx % 100 == 0:
                print(f"Epoch {epoch + 1}/{num_epochs} | Iteration {idx} | Train Loss: {train_loss / idx:.4f}")

        # Validation loop
        model.eval()
        val_loss = 0.0

        with torch.no_grad():
            model.eval()
            for inputs, labels in test_dataloader:
                inputs = inputs.to(device)
                labels = labels.to(device)

                outputs = model(inputs)
                loss = criterion(outputs, labels)

                val_loss += loss.item() * inputs.size(0)

        # Calculate average losses
        train_loss = train_loss / len(train_dataloader.dataset)
        val_loss = val_loss / len(test_dataloader.dataset)

        train_losses.append(train_loss)
        val_losses.append(val_loss)

        print(f"Epoch {epoch + 1}/{num_epochs} | Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f}")

        if val_loss < best_valid_loss:
            best_valid_loss = val_loss
            torch.save(model.state_dict(), r"weights\r"+f'best_model_E_{epoch}_customLoss.pt')
            print('Saved the best model!')

    # Plot the learning curves
    plt.plot(range(1, num_epochs + 1), train_losses, label='Train')
    plt.plot(range(1, num_epochs + 1), val_losses, label='Validation')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Training and Validation Loss')
    plt.legend()
    plt.show()


if __name__ == "__main__":
    # Generate a random image
    sample_size = 10000
    images, labels = generate_hyperspectral_image(sample_size)
    images_train, images_test, labels_train, labels_test = train_test_split(images, labels, test_size=0.1,
                                                                            random_state=42)

    # Create the datasets
    train_dataset = HyperspectralDataset(images_train, labels_train)
    test_dataset = HyperspectralDataset(images_test, labels_test)

    # Set batch size for the dataloaders
    batch_size = 16

    # Create the dataloaders
    train_dataloader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_dataloader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)


    # Parameters
    num_epochs = 20
    learning_rate = 0.0001

    # Create the model
    model = DOFNet().to(device)
    # model.load_state_dict(torch.load('best_model.pt'))

    # Define loss function and optimizer
    # criterion = nn.MSELoss()
    criterion = StudentT_NLLLoss()
    optimizer = Adam(model.parameters(), lr=learning_rate)
    print("Starting training...")
    # Call the train function
    train(model, train_dataloader,test_dataloader, criterion, optimizer, num_epochs)