import io
import math
from typing import List

from PIL import Image
import torch
from transformers import CLIPModel, CLIPProcessor

CLIP_MODEL_NAME = 'openai/clip-vit-base-patch32'

_clip_model = None
_clip_processor = None
_clip_device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


def _load_clip():
    global _clip_model, _clip_processor
    if _clip_model is not None and _clip_processor is not None:
        return _clip_model, _clip_processor

    _clip_model = CLIPModel.from_pretrained(CLIP_MODEL_NAME)
    _clip_processor = CLIPProcessor.from_pretrained(CLIP_MODEL_NAME)
    _clip_model.to(_clip_device)
    _clip_model.eval()
    return _clip_model, _clip_processor


def _normalize_vector(vector: torch.Tensor) -> List[float]:
    norm = vector.norm(p=2, dim=-1, keepdim=True)
    normalized = vector / (norm + 1e-10)
    return normalized.cpu().tolist()[0]


def get_image_embedding(image_bytes: bytes) -> List[float]:
    model, processor = _load_clip()
    image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    inputs = processor(images=image, return_tensors='pt')
    inputs = {k: v.to(_clip_device) for k, v in inputs.items()}
    with torch.no_grad():
        features = model.get_image_features(**inputs)
    return _normalize_vector(features)


def get_text_embedding(text: str) -> List[float]:
    model, processor = _load_clip()
    inputs = processor(text=[text], return_tensors='pt')
    inputs = {k: v.to(_clip_device) for k, v in inputs.items()}
    with torch.no_grad():
        features = model.get_text_features(**inputs)
    return _normalize_vector(features)


def cosine_similarity(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)
