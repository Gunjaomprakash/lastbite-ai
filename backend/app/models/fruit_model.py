# app/models/fruit_model.py

import torch
import torch.nn as nn
import torch.nn.functional as F

class DualFruitCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 16, 3, padding=1)
        self.conv2 = nn.Conv2d(16, 32, 3, padding=1)
        self.pool  = nn.MaxPool2d(2, 2)
        self.fc_shared = nn.Linear(32 * 32 * 32, 128)
        self.fc_fruit  = nn.Linear(128, 3)
        self.fc_state  = nn.Linear(128, 2)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(x.size(0), -1)
        x = F.relu(self.fc_shared(x))
        return self.fc_fruit(x), self.fc_state(x)

def load_model_checkpoint(checkpoint_path, device=None):
    """
    Loads model weights and returns:
      - model: DualFruitCNN in eval() mode
      - class_map: dict mapping indices to labels
    """
    if device is None:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # instantiate model
    model = DualFruitCNN().to(device)

    # load only tensor data (weights) to avoid unpickling arbitrary objects
    checkpoint = torch.load(
        checkpoint_path,
        map_location=device,
        weights_only=True
    )

    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()

    # retrieve the class maps you saved (these are plain dicts, not tensors)
    class_map = checkpoint.get('class_map', {
        'fruit': {0: 'apple', 1: 'banana', 2: 'orange'},
        'state': {0: 'fresh', 1: 'rotten'}
    })

    return model, class_map