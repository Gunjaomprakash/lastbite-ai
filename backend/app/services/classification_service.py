from PIL import Image
import io
import torch
from torchvision import transforms
from app.models.fruit_model import DualFruitCNN, load_model_checkpoint

# load once at import
model, class_map = load_model_checkpoint('/Users/omprakashgunja/Documents/GitHub/lastbite-ai/backend/app/models/fruit_dual_cnn.pth')
device = next(model.parameters()).device

preprocess = transforms.Compose([
    transforms.Resize((128,128)),
    transforms.ToTensor(),
    transforms.Normalize([0.5]*3, [0.5]*3)
])

def predict_fruit_state(file_storage):
    file_storage.stream.seek(0)
    img_bytes = file_storage.read()
    img = Image.open(io.BytesIO(img_bytes)).convert('RGB')

    x = preprocess(img).unsqueeze(0).to(device)
    print("Input tensor stats:", x.mean().item(), x.std().item())

    model.eval()
    with torch.no_grad():
        fruit_logits, state_logits = model(x)
    print("Fruit logits:", fruit_logits.tolist())
    print("State logits:", state_logits.tolist())

    fruit_idx = fruit_logits.argmax(dim=1).item()
    state_idx = state_logits.argmax(dim=1).item()

    return {
        'fruit': class_map['fruit'][fruit_idx],
        'state': class_map['state'][state_idx]
    }