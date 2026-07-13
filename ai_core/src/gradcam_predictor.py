"""
gradcam_predictor.py
VisionGuard AI — Reusable Grad-CAM prediction function

Loads the trained EfficientNet-B0 model once, then exposes
predict_with_gradcam(image_path, save_heatmap_path) which:
  - runs inference on any single image
  - returns the predicted class (real/fake), confidence, and
    a saved Grad-CAM heatmap image

Intended to be imported directly by the FastAPI backend (M5).
"""

import os
import numpy as np
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.image import show_cam_on_image

# ---------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------
# Path to the trained model weights, relative to this file's location
# ai_core/src/gradcam_predictor.py -> ai_core/models/checkpoints/*.pth
MODEL_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "models", "checkpoints", "efficientnet_b0_visionguard.pth"
)

CLASS_NAMES = ["fake", "real"]  # adjust order if your training used a different mapping

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

_IMAGE_TRANSFORM = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# ---------------------------------------------------------------------
# Load model + Grad-CAM once at import time (not on every call)
# ---------------------------------------------------------------------
_model = models.efficientnet_b0(weights=None)
_num_features = _model.classifier[1].in_features
_model.classifier[1] = nn.Linear(_num_features, 2)

_model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
_model = _model.to(DEVICE)
_model.eval()

_target_layers = [_model.features[-1]]
_cam = GradCAM(model=_model, target_layers=_target_layers)


def predict_with_gradcam(image_path: str, save_heatmap_path: str) -> dict:
    """
    Run prediction + Grad-CAM explainability on a single image.

    Args:
        image_path: path to the input image (jpg/png)
        save_heatmap_path: where to save the Grad-CAM heatmap overlay

    Returns:
        dict with keys: prediction (str), confidence (float), heatmap_path (str)
    """
    # Load and preprocess image
    pil_img = Image.open(image_path).convert("RGB")
    img_tensor = _IMAGE_TRANSFORM(pil_img)
    input_tensor = img_tensor.unsqueeze(0).to(DEVICE)

    # Run prediction
    with torch.no_grad():
        output = _model(input_tensor)
        probs = torch.softmax(output, dim=1)
        pred_class_idx = torch.argmax(probs, dim=1).item()
        confidence = probs[0][pred_class_idx].item()

    prediction = CLASS_NAMES[pred_class_idx]

    # Run Grad-CAM
    grayscale_cam = _cam(input_tensor=input_tensor, targets=None)[0]

    # Un-normalize image for overlay
    img_np = img_tensor.permute(1, 2, 0).cpu().numpy()
    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])
    img_np = std * img_np + mean
    img_np = np.clip(img_np, 0, 1)

    cam_image = show_cam_on_image(img_np, grayscale_cam, use_rgb=True)

    # Save heatmap
    os.makedirs(os.path.dirname(save_heatmap_path) or ".", exist_ok=True)
    Image.fromarray(cam_image).save(save_heatmap_path)

    return {
        "prediction": prediction,
        "confidence": confidence,
        "heatmap_path": save_heatmap_path
    }
