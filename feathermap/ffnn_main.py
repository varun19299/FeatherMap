import torch
import torch.nn as nn
import torchvision
import torchvision.transforms as transforms
from feathermap.models.feathernet import FeatherNet
from feathermap.models.ffnn import FFNN, parse_arguments
from feathermap.utils.timer import timed


def load_data(batch_size, **kwargs):
    # MNIST dataset
    train_dataset = torchvision.datasets.MNIST(
        root="./data", train=True, transform=transforms.ToTensor(), download=True
    )

    test_dataset = torchvision.datasets.MNIST(
        root="./data", train=False, transform=transforms.ToTensor()
    )

    # Data loader
    train_loader = torch.utils.data.DataLoader(
        dataset=train_dataset, batch_size=batch_size, shuffle=True, **kwargs
    )

    test_loader = torch.utils.data.DataLoader(
        dataset=test_dataset, batch_size=batch_size, shuffle=False, **kwargs
    )
    return train_loader, test_loader


@timed
def train(model, train_loader, epochs, lr, device):
    model.train()
    # Loss and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    # Train the model
    total_step = len(train_loader)
    for epoch in range(epochs):
        for i, (images, labels) in enumerate(train_loader):
            # Move tensors to the configured device
            images = images.reshape(-1, 28 * 28).to(device)
            labels = labels.to(device)

            # Forward pass
            outputs = model(images)
            loss = criterion(outputs, labels)

            # Backward and optimize
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            if (i + 1) % 100 == 0:
                print(
                    "Epoch [{}/{}], Step [{}/{}], Loss: {:.4f}".format(
                        epoch + 1, epochs, i + 1, total_step, loss.item()
                    )
                )


@timed
def evaluate(model, test_loader, device):
    model.eval()
    with torch.no_grad():
        correct = 0
        total = 0
        for images, labels in test_loader:
            images = images.reshape(-1, 28 * 28).to(device)
            labels = labels.to(device)
            outputs = model(images)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

        accuracy = 100 * correct / total
        print("Accuracy of the network on the 10000 test images: {} %".format(accuracy))
        return accuracy


@timed
def main():
    args = parse_arguments()

    # Device configuration
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    kwargs = (
        {"num_workers": args.num_workers, "pin_memory": True}
        if torch.cuda.is_available()
        else {}
    )

    # MNIST-parameters
    input_size = 784
    num_classes = 10

    # Select model
    base_model = FFNN(input_size, args.hidden_size, num_classes)
    if args.compress:
        model = FeatherNet(base_model, compress=args.compress).to(device)
    else:
        model = base_model.to(device)

    # Load data
    train_loader, test_loader = load_data(args.batch_size, **kwargs)

    # Train, evaluate
    train(model, train_loader, args.epochs, args.lr, device)
    evaluate(model, test_loader, device)

    # Save the model checkpoint
    if args.save_model:
        torch.save(model.state_dict(), "ffnn.ckpt")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit()
