# inference.py
from typing import List

import torch
import torchvision.transforms as T
from PIL import Image
from torchvision.models import ResNet34_Weights, resnet34


preprocess = T.Compose(
    [
        T.Resize((224, 224)),
        T.ToTensor(),
        T.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225],
        ),
    ]
)

# Auto-detect GPU/CPU device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

model = resnet34(weights=ResNet34_Weights.IMAGENET1K_V1).eval()
model = torch.jit.script(model)  # TorchScript optimization
model = model.to(device)  # Move model to GPU/CPU

@torch.no_grad()
def inference(images: List[Image.Image]) -> List[int]:
    if not images:
        return []
    batch = torch.stack([preprocess(image) for image in images])
    batch = batch.to(device)  # Move batch to GPU/CPU
    logits = model(batch)
    preds = logits.argmax(dim=1).tolist()
    return preds

if __name__ == "__main__":
    image = Image.open("Images/cat.jpg")
    print(inference([image]))