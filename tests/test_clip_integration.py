import io
import importlib
import sys

import pytest
from PIL import Image

from backend.clip import cosine_similarity


def test_cosine_similarity_same_vector():
    a = [1.0, 0.0, 0.0]
    b = [1.0, 0.0, 0.0]
    assert cosine_similarity(a, b) == pytest.approx(1.0)


def test_cosine_similarity_orthogonal_vectors():
    a = [1.0, 0.0, 0.0]
    b = [0.0, 1.0, 0.0]
    assert cosine_similarity(a, b) == pytest.approx(0.0)


def test_cosine_similarity_zero_vector():
    assert cosine_similarity([], [1.0, 2.0]) == 0.0
    assert cosine_similarity([0.0, 0.0], [0.0, 0.0]) == 0.0


def test_clip_model_generates_embeddings():
    pytest.importorskip('torch')
    pytest.importorskip('transformers')
    pytest.importorskip('PIL')

    sys.modules.pop('backend.clip', None)
    clip_module = importlib.import_module('backend.clip')

    text_embedding = clip_module.get_text_embedding('summer outfit')
    assert isinstance(text_embedding, list)
    assert len(text_embedding) > 0
    assert all(isinstance(value, float) for value in text_embedding)

    image = Image.new('RGB', (64, 64), color=(123, 45, 67))
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    image_embedding = clip_module.get_image_embedding(buffer.getvalue())
    assert isinstance(image_embedding, list)
    assert len(image_embedding) > 0
    assert all(isinstance(value, float) for value in image_embedding)
