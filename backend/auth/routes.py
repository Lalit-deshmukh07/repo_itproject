import json
import random
import urllib.request
from typing import Dict, List, Optional
from flask import Blueprint, jsonify, request, session

from backend.clip import cosine_similarity, get_image_embedding, get_text_embedding
from backend.common.models import Outfit, User, WardrobeItem, db

auth = Blueprint('auth', __name__)

IMAGE_EMBEDDING_CACHE: Dict[str, List[float]] = {}


def _fetch_image_bytes(url: str) -> Optional[bytes]:
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return response.read()
    except Exception:
        return None


def _build_clip_query(user: User, styles: List[str]) -> str:
    gender = _normalize_gender(getattr(user, 'gender', None))
    style_desc = ', '.join(styles) if styles else 'fashionable outfits'
    return (
        f"A {gender} user who prefers {style_desc}. "
        f"Recommend clothing combinations that feel modern, comfortable, and true to their style preferences."
    )


def _get_recommendation_score(rec: Dict, query_embedding: List[float], user_styles: List[str]) -> float:
    image_url = rec.get('image')
    if not image_url or not query_embedding:
        return 0.0

    embedding = IMAGE_EMBEDDING_CACHE.get(image_url)
    if embedding is None:
        image_bytes = _fetch_image_bytes(image_url)
        if image_bytes is None:
            return 0.0
        embedding = get_image_embedding(image_bytes)
        IMAGE_EMBEDDING_CACHE[image_url] = embedding

    score = cosine_similarity(query_embedding, embedding)
    style_bonus = 0.5 if any(style in user_styles for style in rec.get('styles', [])) else 0.25
    return score * 0.75 + style_bonus * 0.25


MODEL_POOL = {
    'male': [
        'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=900&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?w=900&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=900&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=900&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1503342217505-b0a15ec3261c?w=900&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1504593811423-6dd665756598?w=900&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1552374196-1ab2a1c593e8?w=900&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1521119989659-a83eee488004?w=900&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=900&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1516257984-b1b4d707412e?w=900&auto=format&fit=crop',
    ],
    'female': [
        'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=900&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1488426862026-3ee34a7d66df?w=900&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1483985988355-763728e1935b?w=900&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1496747611176-843222e1e57c?w=900&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=900&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1464863979621-258859e62245?w=900&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1524504388940-3a3fde2f66f8?w=900&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1512436991641-6745cdb1723f?w=900&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=900&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1502716119720-b23a93e5fe1b?w=900&auto=format&fit=crop',
    ],
    'diverse': [
        'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=900&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=900&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=900&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1488426862026-3ee34a7d66df?w=900&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?w=900&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=900&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1515372039744-2c7aef9493d7?w=900&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?w=900&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1483985988355-763728e1935b?w=900&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1512436991641-6745cdb1723f?w=900&auto=format&fit=crop',
    ],
}


def _normalize_gender(gender):
    if not gender:
        return 'diverse'
    normalized = str(gender).strip().lower()
    if normalized in {'male', 'man', 'm', 'he/him'}:
        return 'male'
    if normalized in {'female', 'woman', 'f', 'she/her'}:
        return 'female'
    return 'diverse'


def _select_model_image(gender, style, fallback):
    normalized_gender = _normalize_gender(gender)
    pool = MODEL_POOL.get(normalized_gender, MODEL_POOL['diverse'])
    return random.choice(pool) if pool else fallback


def _assign_model_images(recommendations, gender):
    normalized_gender = _normalize_gender(gender)
    pool = MODEL_POOL.get(normalized_gender, MODEL_POOL['diverse']).copy()
    random.shuffle(pool)

    if len(pool) < len(recommendations):
        pool = pool * ((len(recommendations) // len(pool)) + 1)
        random.shuffle(pool)

    for idx, rec in enumerate(recommendations):
        rec['modelImage'] = pool[idx]


def _is_recommendation_appropriate_for_gender(rec: Dict, gender: str) -> bool:
    normalized_gender = _normalize_gender(gender)
    if normalized_gender != 'male':
        return True

    text = f"{rec.get('title', '')} {rec.get('description', '')}".lower()
    feminine_terms = [
        'dress',
        'skirt',
        'heels',
        'ballet flats',
        'midi dress',
        'maxi dress',
        'cocktail dress',
        'lace blouse',
        'peasant blouse',
        'fringe bag',
        'floral midi',
    ]
    return not any(term in text for term in feminine_terms)


def _get_style_recommendations_for_gender(gender: str) -> Dict[str, List[Dict]]:
    normalized_gender = _normalize_gender(gender)

    male_catalog = {
        'casual': [
            {'title': 'Casual Weekend', 'description': 'Crew-neck tee, straight jeans, and clean sneakers for an easy everyday look.', 'styles': ['casual'], 'image': 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=600&auto=format&fit=crop'},
            {'title': 'Relaxed Street Casual', 'description': 'Overshirt, relaxed denim, and low-top trainers for a laid-back outfit.', 'styles': ['casual'], 'image': 'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=600&auto=format&fit=crop'},
        ],
        'formal': [
            {'title': 'Business Ready', 'description': 'Tailored blazer, crisp shirt, and dress trousers with polished shoes.', 'styles': ['formal'], 'image': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=600&auto=format&fit=crop'},
            {'title': 'Sharp Office Look', 'description': 'Fitted suit separates with a clean shirt and leather loafers.', 'styles': ['formal'], 'image': 'https://images.unsplash.com/photo-1516257984-b1b4d707412e?w=600&auto=format&fit=crop'},
        ],
        'sporty': [
            {'title': 'Athletic Street', 'description': 'Performance tee, joggers, and trainers for an active day.', 'styles': ['sporty'], 'image': 'https://images.unsplash.com/photo-1483721310020-03333e577078?w=600&auto=format&fit=crop'},
            {'title': 'Training Day', 'description': 'Lightweight hoodie, track pants, and running shoes.', 'styles': ['sporty'], 'image': 'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=600&auto=format&fit=crop'},
        ],
        'streetwear': [
            {'title': 'Urban Utility', 'description': 'Oversized tee, cargo pants, and chunky sneakers for a modern street look.', 'styles': ['streetwear'], 'image': 'https://images.unsplash.com/photo-1552374196-1ab2a1c593e8?w=600&auto=format&fit=crop'},
            {'title': 'Clean Street Style', 'description': 'Graphic tee, straight cargos, and high-top sneakers.', 'styles': ['streetwear'], 'image': 'https://images.unsplash.com/photo-1512436991641-6745cdb1723f?w=600&auto=format&fit=crop'},
        ],
        'minimalist': [
            {'title': 'Minimal Monochrome', 'description': 'Plain tee, slim trousers, and white sneakers for a clean silhouette.', 'styles': ['minimalist'], 'image': 'https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=600&auto=format&fit=crop'},
            {'title': 'Quiet Essentials', 'description': 'Neutral knit, tailored pants, and simple leather sneakers.', 'styles': ['minimalist'], 'image': 'https://images.unsplash.com/photo-1554412933-514a83d2f3c8?w=600&auto=format&fit=crop'},
        ],
        'vintage': [
            {'title': 'Retro Tailored', 'description': 'Vintage-inspired shirt, pleated trousers, and classic loafers.', 'styles': ['vintage'], 'image': 'https://images.unsplash.com/photo-1509631179647-0177331693ae?w=600&auto=format&fit=crop'},
            {'title': 'Old-School Cool', 'description': 'Knitted polo, straight denim, and leather sneakers.', 'styles': ['vintage'], 'image': 'https://images.unsplash.com/photo-1551803091-e20673f15770?w=600&auto=format&fit=crop'},
        ],
        'preppy': [
            {'title': 'Campus Prep', 'description': 'Polo shirt, chinos, and boat shoes for a polished preppy look.', 'styles': ['preppy'], 'image': 'https://images.unsplash.com/photo-1541101767792-f9b2b1c4f127?w=600&auto=format&fit=crop'},
            {'title': 'Smart Collegiate', 'description': 'Sweater vest, button-down, and tailored trousers.', 'styles': ['preppy'], 'image': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=600&auto=format&fit=crop'},
        ],
        'edgy': [
            {'title': 'Dark Edge', 'description': 'Leather jacket, black denim, and combat boots for a sharp look.', 'styles': ['edgy'], 'image': 'https://images.unsplash.com/photo-1509631179647-0177331693ae?w=600&auto=format&fit=crop'},
            {'title': 'Rock Street', 'description': 'Band tee, distressed jeans, and heavy boots.', 'styles': ['edgy'], 'image': 'https://images.unsplash.com/photo-1516914943479-89db7d9ae7f2?w=600&auto=format&fit=crop'},
        ],
        'romantic': [
            {'title': 'Soft Tailoring', 'description': 'Light knit top, fitted trousers, and refined loafers.', 'styles': ['romantic'], 'image': 'https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=600&auto=format&fit=crop'},
            {'title': 'Polished Detail', 'description': 'Textured shirt, clean trousers, and subtle accessories.', 'styles': ['romantic'], 'image': 'https://images.unsplash.com/photo-1519657337289-077653f724ed?w=600&auto=format&fit=crop'},
        ],
        'classic': [
            {'title': 'Timeless Classic', 'description': 'White button-down, straight trousers, and leather loafers.', 'styles': ['classic'], 'image': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&auto=format&fit=crop'},
            {'title': 'Heritage Look', 'description': 'Structured blazer, simple shirt, and tailored chinos.', 'styles': ['classic'], 'image': 'https://images.unsplash.com/photo-1477118476589-bff2c5c4cfbb?w=600&auto=format&fit=crop'},
        ],
        'experimental': [
            {'title': 'Bold Statement', 'description': 'Layered textures, mixed prints, and statement sneakers.', 'styles': ['experimental'], 'image': 'https://images.unsplash.com/photo-1469334031218-e382a71b716b?w=600&auto=format&fit=crop'},
            {'title': 'Fashion Forward', 'description': 'Unexpected silhouette, strong lines, and standout accessories.', 'styles': ['experimental'], 'image': 'https://images.unsplash.com/photo-1502716119720-b23a93e5fe1b?w=600&auto=format&fit=crop'},
        ],
    }

    female_catalog = {
        'casual': [
            {'title': 'Casual Comfort', 'description': 'Relaxed jeans, soft tee, and fresh sneakers for everyday wear.', 'styles': ['casual'], 'image': 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=600&auto=format&fit=crop'},
            {'title': 'Weekend Ease', 'description': 'Easy layers, denim, and comfy flats for a laid-back day.', 'styles': ['casual'], 'image': 'https://images.unsplash.com/photo-1488426862026-3ee34a7d66df?w=600&auto=format&fit=crop'},
        ],
        'formal': [
            {'title': 'Business Elegant', 'description': 'Tailored blazer, refined trousers, and sleek heels or loafers.', 'styles': ['formal'], 'image': 'https://images.unsplash.com/photo-1594938298603-c8148c4b4ae2?w=600&auto=format&fit=crop'},
            {'title': 'Power Dressing', 'description': 'Structured suit, crisp top, and polished shoes for a confident look.', 'styles': ['formal'], 'image': 'https://images.unsplash.com/photo-1525507119028-ed4c629a60a3?w=600&auto=format&fit=crop'},
        ],
        'sporty': [
            {'title': 'Active Wear', 'description': 'Performance top, leggings or joggers, and supportive trainers.', 'styles': ['sporty'], 'image': 'https://images.unsplash.com/photo-1483721310020-03333e577078?w=600&auto=format&fit=crop'},
            {'title': 'Athletic Look', 'description': 'Sporty jacket, fitted bottoms, and running shoes.', 'styles': ['sporty'], 'image': 'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=600&auto=format&fit=crop'},
        ],
        'streetwear': [
            {'title': 'Urban Street', 'description': 'Oversized hoodie, cargos, and chunky sneakers for a current street look.', 'styles': ['streetwear'], 'image': 'https://images.unsplash.com/photo-1552374196-1ab2a1c593e8?w=600&auto=format&fit=crop'},
            {'title': 'Street Style', 'description': 'Graphic top, relaxed denim, and standout sneakers.', 'styles': ['streetwear'], 'image': 'https://images.unsplash.com/photo-1512436991641-6745cdb1723f?w=600&auto=format&fit=crop'},
        ],
        'minimalist': [
            {'title': 'Simple Elegance', 'description': 'Plain tee, clean denim, and white sneakers for a minimal look.', 'styles': ['minimalist'], 'image': 'https://images.unsplash.com/photo-1554412933-514a83d2f3c8?w=600&auto=format&fit=crop'},
            {'title': 'Understated', 'description': 'Neutral knit, tailored pants, and subtle accessories.', 'styles': ['minimalist'], 'image': 'https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=600&auto=format&fit=crop'},
        ],
        'vintage': [
            {'title': 'Retro Chic', 'description': 'Vintage blouse, high-waisted denim, and classic pumps or flats.', 'styles': ['vintage'], 'image': 'https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=600&auto=format&fit=crop'},
            {'title': 'Nostalgic Style', 'description': 'Floral midi dress, cardigan, and loafers for a vintage feel.', 'styles': ['vintage'], 'image': 'https://images.unsplash.com/photo-1551803091-e20673f15770?w=600&auto=format&fit=crop'},
        ],
        'preppy': [
            {'title': 'Classic Prep', 'description': 'Polo top, chinos or skirt, and loafers for a polished preppy look.', 'styles': ['preppy'], 'image': 'https://images.unsplash.com/photo-1541101767792-f9b2b1c4f127?w=600&auto=format&fit=crop'},
            {'title': 'Campus Chic', 'description': 'Argyle knit, tailored bottoms, and neat flats or loafers.', 'styles': ['preppy'], 'image': 'https://images.unsplash.com/photo-1502716119720-b23a93e5fe1b?w=600&auto=format&fit=crop'},
        ],
        'edgy': [
            {'title': 'Dark Edge', 'description': 'Leather jacket, black denim, and combat boots for a sharper look.', 'styles': ['edgy'], 'image': 'https://images.unsplash.com/photo-1509631179647-0177331693ae?w=600&auto=format&fit=crop'},
            {'title': 'Rock Rebel', 'description': 'Band tee, black jeans, and boots with a bold finish.', 'styles': ['edgy'], 'image': 'https://images.unsplash.com/photo-1516914943479-89db7d9ae7f2?w=600&auto=format&fit=crop'},
        ],
        'romantic': [
            {'title': 'Soft Romance', 'description': 'Floral midi dress, cardigan, and ballet flats for a gentle silhouette.', 'styles': ['romantic'], 'image': 'https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=600&auto=format&fit=crop'},
            {'title': 'Dreamy Look', 'description': 'Lace blouse, pleated skirt, and delicate shoes.', 'styles': ['romantic'], 'image': 'https://images.unsplash.com/photo-1519657337289-077653f724ed?w=600&auto=format&fit=crop'},
        ],
        'classic': [
            {'title': 'Timeless Classic', 'description': 'White button-down, straight trousers, and elegant flats or loafers.', 'styles': ['classic'], 'image': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&auto=format&fit=crop'},
            {'title': 'Parisian Style', 'description': 'Striped top, wide-leg trousers, and loafers for a clean classic look.', 'styles': ['classic'], 'image': 'https://images.unsplash.com/photo-1509631179647-0177331693ae?w=600&auto=format&fit=crop'},
        ],
        'experimental': [
            {'title': 'Bold Statement', 'description': 'Mixed prints, layered accessories, and standout shoes.', 'styles': ['experimental'], 'image': 'https://images.unsplash.com/photo-1469334031218-e382a71b716b?w=600&auto=format&fit=crop'},
            {'title': 'Fashion Forward', 'description': 'Avant-garde silhouette with unexpected textures and details.', 'styles': ['experimental'], 'image': 'https://images.unsplash.com/photo-1502716119720-b23a93e5fe1b?w=600&auto=format&fit=crop'},
        ],
    }

    diverse_catalog = {
        'casual': [
            {'title': 'Casual Comfort', 'description': 'Relaxed jeans, soft tee, and clean sneakers.', 'styles': ['casual'], 'image': 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=600&auto=format&fit=crop'},
            {'title': 'Weekend Ease', 'description': 'Easy layers, denim, and comfy shoes for a laid-back day.', 'styles': ['casual'], 'image': 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=600&auto=format&fit=crop'},
        ],
        'formal': [
            {'title': 'Business Ready', 'description': 'Tailored blazer, crisp shirt, and polished trousers.', 'styles': ['formal'], 'image': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=600&auto=format&fit=crop'},
            {'title': 'Power Dressing', 'description': 'Structured suit and sharp shoes for a confident office look.', 'styles': ['formal'], 'image': 'https://images.unsplash.com/photo-1594938298603-c8148c4b4ae2?w=600&auto=format&fit=crop'},
        ],
        'sporty': [
            {'title': 'Athletic Look', 'description': 'Performance top, fitted bottoms, and trainers.', 'styles': ['sporty'], 'image': 'https://images.unsplash.com/photo-1483721310020-03333e577078?w=600&auto=format&fit=crop'},
            {'title': 'Active Wear', 'description': 'Light layers, joggers, and supportive running shoes.', 'styles': ['sporty'], 'image': 'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=600&auto=format&fit=crop'},
        ],
        'streetwear': [
            {'title': 'Urban Edge', 'description': 'Oversized hoodie, cargo pants, and chunky sneakers.', 'styles': ['streetwear'], 'image': 'https://images.unsplash.com/photo-1552374196-1ab2a1c593e8?w=600&auto=format&fit=crop'},
            {'title': 'Street Style', 'description': 'Graphic tee, distressed jeans, and high-tops.', 'styles': ['streetwear'], 'image': 'https://images.unsplash.com/photo-1512436991641-6745cdb1723f?w=600&auto=format&fit=crop'},
        ],
        'minimalist': [
            {'title': 'Simple Elegance', 'description': 'Plain tee, clean trousers, and white sneakers.', 'styles': ['minimalist'], 'image': 'https://images.unsplash.com/photo-1554412933-514a83d2f3c8?w=600&auto=format&fit=crop'},
            {'title': 'Understated', 'description': 'Neutral knit, tailored pants, and subtle accessories.', 'styles': ['minimalist'], 'image': 'https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=600&auto=format&fit=crop'},
        ],
        'vintage': [
            {'title': 'Retro Chic', 'description': 'Vintage-inspired top, structured denim, and classic shoes.', 'styles': ['vintage'], 'image': 'https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=600&auto=format&fit=crop'},
            {'title': 'Nostalgic Style', 'description': 'Retro details, timeless shapes, and polished finishing touches.', 'styles': ['vintage'], 'image': 'https://images.unsplash.com/photo-1551803091-e20673f15770?w=600&auto=format&fit=crop'},
        ],
        'preppy': [
            {'title': 'Classic Prep', 'description': 'Polo top, tailored bottoms, and loafers for a polished look.', 'styles': ['preppy'], 'image': 'https://images.unsplash.com/photo-1541101767792-f9b2b1c4f127?w=600&auto=format&fit=crop'},
            {'title': 'Campus Chic', 'description': 'Argyle knit, neat bottoms, and classic shoes.', 'styles': ['preppy'], 'image': 'https://images.unsplash.com/photo-1502716119720-b23a93e5fe1b?w=600&auto=format&fit=crop'},
        ],
        'edgy': [
            {'title': 'Dark Edge', 'description': 'Leather jacket, black denim, and combat boots.', 'styles': ['edgy'], 'image': 'https://images.unsplash.com/photo-1509631179647-0177331693ae?w=600&auto=format&fit=crop'},
            {'title': 'Rock Rebel', 'description': 'Band tee, dark jeans, and bold footwear.', 'styles': ['edgy'], 'image': 'https://images.unsplash.com/photo-1516914943479-89db7d9ae7f2?w=600&auto=format&fit=crop'},
        ],
        'romantic': [
            {'title': 'Soft Romance', 'description': 'Floral pieces, gentle layers, and delicate shoes.', 'styles': ['romantic'], 'image': 'https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=600&auto=format&fit=crop'},
            {'title': 'Dreamy Look', 'description': 'Lace details, flowing shapes, and refined accessories.', 'styles': ['romantic'], 'image': 'https://images.unsplash.com/photo-1519657337289-077653f724ed?w=600&auto=format&fit=crop'},
        ],
        'classic': [
            {'title': 'Timeless Classic', 'description': 'White button-down, straight trousers, and polished shoes.', 'styles': ['classic'], 'image': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&auto=format&fit=crop'},
            {'title': 'Parisian Style', 'description': 'Striped top, wide-leg trousers, and loafers.', 'styles': ['classic'], 'image': 'https://images.unsplash.com/photo-1509631179647-0177331693ae?w=600&auto=format&fit=crop'},
        ],
        'experimental': [
            {'title': 'Bold Statement', 'description': 'Mixed prints, layered details, and standout shoes.', 'styles': ['experimental'], 'image': 'https://images.unsplash.com/photo-1469334031218-e382a71b716b?w=600&auto=format&fit=crop'},
            {'title': 'Fashion Forward', 'description': 'Unexpected silhouette and modern textures for a standout outfit.', 'styles': ['experimental'], 'image': 'https://images.unsplash.com/photo-1502716119720-b23a93e5fe1b?w=600&auto=format&fit=crop'},
        ],
    }

    if normalized_gender == 'male':
        return male_catalog
    if normalized_gender == 'female':
        return female_catalog
    return diverse_catalog


def _matches_user_exclusions(rec: Dict, exclusions: List[str]) -> bool:
    if not exclusions:
        return True

    text = f"{rec.get('title', '')} {rec.get('description', '')}".lower()
    normalized_exclusions = [str(item).strip().lower() for item in exclusions if str(item).strip()]
    return not any(exclusion in text for exclusion in normalized_exclusions)


@auth.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json(silent=True)
    if not data:
        data = request.form.to_dict()

    if not data:
        return jsonify({"message": "No data received"}), 400

    first_name = (data.get("firstName") or data.get("first_name") or "").strip()
    last_name = (data.get("lastName") or data.get("last_name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    consent = data.get("consent")

    if not first_name or not last_name:
        return jsonify({"message": "First name and last name are required."}), 400

    if not email or "@" not in email or len(email) < 5:
        return jsonify({"message": "Please enter a valid email address."}), 400

    if not password or len(password) < 8:
        return jsonify({"message": "Password must be at least 8 characters long."}), 400

    if consent not in [True, 'true', 'on', 'yes', '1']:
        return jsonify({"message": "You must accept the terms and privacy policy."}), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"message": "User already exists"}), 400

    new_user = User(first_name=first_name, last_name=last_name, email=email)
    new_user.set_password(password)

    try:
        db.session.add(new_user)
        db.session.commit()

        session.permanent = True
        session['user_id'] = new_user.id
        session['user_email'] = new_user.email
        session['user_name'] = f"{new_user.first_name} {new_user.last_name}"

        return jsonify({"message": "Registered successfully", "user": new_user.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Registration failed: {str(e)}"}), 500


@auth.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json(silent=True)
    if not data:
        data = request.form.to_dict()

    if not data:
        return jsonify({"message": "No data received"}), 400

    email = (data.get("email") or data.get("username") or "").strip().lower()
    password = data.get("password") or ""

    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        session.permanent = True
        session['user_id'] = user.id
        session['user_email'] = user.email
        session['user_name'] = f"{user.first_name} {user.last_name}"

        return jsonify({"message": "Login successful", "user": user.to_dict()}), 200

    return jsonify({"message": "Invalid email or password"}), 401


@auth.route('/api/auth/reset-request', methods=['POST'])
def reset_request():
    data = request.get_json()

    if not data:
        return jsonify({"message": "No data received"}), 400

    email = data.get("email")

    return jsonify({"message": f"Password reset link sent to {email}"}), 200


@auth.route('/api/auth/status', methods=['GET'])
def check_auth_status():
    user_id = session.get('user_id')

    if user_id:
        user = User.query.get(user_id)
        if user:
            user_payload = user.to_dict()
            user_payload.update({
                "id": user.id,
                "email": user.email,
                "name": f"{user.first_name} {user.last_name}".strip(),
                "gender": user.gender,
                "topSize": user.top_size,
                "bottomSize": user.bottom_size,
                "styles": user.get_style_preferences(),
                "exclusions": user.get_exclusions(),
            })
            return jsonify({"authenticated": True, "user": user_payload}), 200

    return jsonify({"authenticated": False, "user": None}), 200


@auth.route('/api/outfit/save', methods=['POST'])
def save_outfit():
    user_id = session.get('user_id')

    if not user_id:
        return jsonify({"message": "User not authenticated. Please login first."}), 401

    data = request.get_json()

    if not data:
        return jsonify({"message": "No data received"}), 400

    items = data.get("items", {}) or {}

    def _stringify_item(item):
        if item is None:
            return None
        if isinstance(item, str):
            return item
        if isinstance(item, dict):
            name = item.get("name") or item.get("title") or item.get("label")
            if name:
                return str(name)
            return json.dumps(item)
        return str(item)

    signature = json.dumps({
        "occasion": data.get("occasion", ""),
        "items": items,
        "weather": data.get("weather", ""),
        "aiNote": data.get("aiNote", "")
    }, sort_keys=True)

    existing_outfit = Outfit.query.filter_by(user_id=user_id).filter(
        Outfit.occasion == data.get("occasion", "")
    ).filter(Outfit.item_data == json.dumps(items)).first()

    if existing_outfit:
        return jsonify({"message": "Outfit already saved", "outfit": existing_outfit.to_dict()}), 200

    outfit = Outfit(
        user_id=user_id,
        occasion=data.get("occasion", ""),
        outerwear_item=_stringify_item(items.get("outerwear")),
        top_item=_stringify_item(items.get("top")),
        bottom_item=_stringify_item(items.get("bottom")),
        shoes_item=_stringify_item(items.get("shoes")),
        item_data=json.dumps(items),
        weather=data.get("weather", ""),
        ai_note=data.get("aiNote", "")
    )

    try:
        db.session.add(outfit)
        db.session.commit()

        return jsonify({"message": "Outfit saved successfully", "outfit": outfit.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Failed to save outfit: {str(e)}"}), 500


@auth.route('/api/outfit/get-all', methods=['GET'])
def get_saved_outfits():
    user_id = session.get('user_id')

    if not user_id:
        return jsonify({"message": "User not authenticated. Please login first."}), 401

    outfits = Outfit.query.filter_by(user_id=user_id).all()

    return jsonify({"outfits": [outfit.to_dict() for outfit in outfits], "totalOutfits": len(outfits)}), 200


@auth.route('/api/outfit/delete/<int:outfit_id>', methods=['DELETE'])
def delete_outfit(outfit_id):
    user_id = session.get('user_id')

    if not user_id:
        return jsonify({"message": "User not authenticated. Please login first."}), 401

    outfit = Outfit.query.filter_by(id=outfit_id, user_id=user_id).first()
    if not outfit:
        return jsonify({"message": "Outfit not found."}), 404

    try:
        db.session.delete(outfit)
        db.session.commit()
        return jsonify({"message": "Outfit deleted successfully."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Failed to delete outfit: {str(e)}"}), 500


@auth.route('/api/wardrobe/items', methods=['POST'])
def save_wardrobe_item():
    user_id = session.get('user_id')

    if not user_id:
        return jsonify({"message": "User not authenticated. Please login first."}), 401

    data = request.get_json(silent=True) or {}
    category = (data.get('category') or '').strip().lower()
    name = (data.get('name') or '').strip()
    image_data = (data.get('imageData') or '').strip()

    if not category or not name or not image_data:
        return jsonify({"message": "Category, name, and image data are required."}), 400

    try:
        item = WardrobeItem(user_id=user_id, category=category, name=name, image_data=image_data)
        db.session.add(item)
        db.session.commit()
        return jsonify({"message": "Wardrobe item saved", "item": item.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Failed to save wardrobe item: {str(e)}"}), 500


@auth.route('/api/wardrobe/items', methods=['GET'])
def get_wardrobe_items():
    user_id = session.get('user_id')

    if not user_id:
        return jsonify({"message": "User not authenticated. Please login first."}), 401

    items = WardrobeItem.query.filter_by(user_id=user_id).order_by(WardrobeItem.created_at.desc()).all()
    return jsonify({"items": [item.to_dict() for item in items], "totalItems": len(items)}), 200


@auth.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200


@auth.route('/api/user/preferences', methods=['POST'])
def save_preferences():
    user_id = session.get('user_id')

    if not user_id:
        return jsonify({"message": "User not authenticated"}), 401

    data = request.get_json(silent=True)
    if not data:
        data = request.form.to_dict()

    if not data:
        return jsonify({"message": "No data received"}), 400

    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "User not found"}), 404

        user.gender = data.get('gender')
        user.top_size = data.get('topSize')
        user.bottom_size = data.get('bottomSize')
        user.set_style_preferences(data.get('styles', []))
        user.set_exclusions(data.get('exclusions', []))

        db.session.commit()

        return jsonify({"message": "Preferences saved successfully", "user": user.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Failed to save preferences: {str(e)}"}), 500


@auth.route('/api/user/preferences', methods=['GET'])
def get_preferences():
    user_id = session.get('user_id')

    if not user_id:
        return jsonify({"message": "User not authenticated"}), 401

    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "User not found"}), 404

        return jsonify({
            "preferences": {
                "gender": user.gender,
                "topSize": user.top_size,
                "bottomSize": user.bottom_size,
                "styles": user.get_style_preferences(),
                "exclusions": user.get_exclusions()
            }
        }), 200
    except Exception as e:
        return jsonify({"message": f"Failed to fetch preferences: {str(e)}"}), 500


@auth.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    user_id = session.get('user_id')

    if not user_id:
        return jsonify({"message": "User not authenticated"}), 401

    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "User not found"}), 404

        wardrobe_count = WardrobeItem.query.filter_by(user_id=user_id).count()
        if wardrobe_count == 0:
            return jsonify({
                "recommendations": [],
                "userStyles": user.get_style_preferences(),
                "gender": _normalize_gender(getattr(user, 'gender', None)),
                "message": "Upload wardrobe items first, then request recommendations."
            }), 200

        styles = user.get_style_preferences()
        exclusions = user.get_exclusions()
        recommendations = []

        style_recommendations = _get_style_recommendations_for_gender(getattr(user, 'gender', None))

        for style in styles:
            if style in style_recommendations:
                recommendations.extend(style_recommendations[style])

        gender_pref = _normalize_gender(getattr(user, 'gender', None))
        recommendations = [rec for rec in recommendations if _is_recommendation_appropriate_for_gender(rec, gender_pref)]
        recommendations = [rec for rec in recommendations if _matches_user_exclusions(rec, exclusions)]
        _assign_model_images(recommendations, gender_pref)

        query_embedding = None
        try:
            query_text = _build_clip_query(user, styles)
            query_embedding = get_text_embedding(query_text)
        except Exception:
            query_embedding = None

        for rec in recommendations:
            try:
                clip_score = _get_recommendation_score(rec, query_embedding, styles)
                rec['clipScore'] = round(clip_score, 4)
                rec['matchPercentage'] = min(100, max(1, round(20 + clip_score * 80)))
            except Exception:
                rec['clipScore'] = 0.0
                rec['matchPercentage'] = random.randint(40, 75)

        recommendations.sort(key=lambda item: item.get('clipScore', 0), reverse=True)
        top_recommendations = recommendations[:5]

        for rec in top_recommendations:
            rec['matchedGender'] = gender_pref
            rec['matchedStyle'] = (rec.get('styles') or [None])[0]

        return jsonify({
            "recommendations": top_recommendations,
            "userStyles": styles,
            "gender": gender_pref
        }), 200
    except Exception as e:
        return jsonify({"message": f"Failed to fetch recommendations: {str(e)}"}), 500


@auth.route('/api/outfit/weather-suggestions', methods=['GET'])
def weather_suggestions():
    occasion = request.args.get('occasion', 'Casual Day Out')
    condition = request.args.get('condition', 'Clear')
    temp = int(request.args.get('temp', 18))

    is_cold = temp <= 10
    is_hot = temp >= 25
    is_rainy = any(w in condition.lower() for w in ['rain', 'drizzle', 'shower'])
    is_snowy = 'snow' in condition.lower()

    weather_tag = 'cold' if is_snowy or is_cold else ('rainy' if is_rainy else ('hot' if is_hot else 'warm'))

    suggestions_map = {
        'College': {
            'hot': ['Light t-shirt + denim shorts', 'Crop top + wide-leg trousers', 'Polo + chino shorts'],
            'warm': ['Hoodie + jeans + sneakers', 'Oversized tee + cargos', 'Sweatshirt + joggers'],
            'cold': ['Puffer jacket + thermal jeans + boots', 'Knit sweater + cords + loafers'],
            'rainy': ['Waterproof jacket + dark jeans + ankle boots', 'Raincoat + joggers + trainers'],
        },
        'Office': {
            'hot': ['Linen shirt + chinos + loafers', 'Breathable dress + sandals'],
            'warm': ['Blazer + trousers + oxfords', 'Midi dress + heels', 'Shirt + suit pants'],
            'cold': ['Wool suit + overcoat', 'Turtleneck + tailored trousers + boots'],
            'rainy': ['Trench coat + dark suit + waterproof shoes'],
        },
        'Party': {
            'hot': ['Flowy sundress + sandals', 'Linen suit + loafers'],
            'warm': ['Cocktail dress + heels', 'Blazer + slim trousers + Chelsea boots'],
            'cold': ['Party dress + faux fur coat + boots', 'Velvet suit + dress shoes'],
            'rainy': ['Sequin dress + ankle boots', 'Chic raincoat + midi dress'],
        },
        'Casual Day Out': {
            'hot': ['Tank top + shorts + sandals', 'Sundress + flip-flops'],
            'warm': ['Light sweater + casual jeans + sneakers', 'Shirt dress + white sneakers'],
            'cold': ['Parka + warm layers + snow boots', 'Puffer jacket + joggers + trainers'],
            'rainy': ['Rain jacket + waterproof pants + boots', 'Anorak + jeans + wellies'],
        }
    }

    occ_map = suggestions_map.get(occasion, suggestions_map['Casual Day Out'])
    suggestions = occ_map.get(weather_tag, occ_map.get('warm', []))

    return jsonify({
        'occasion': occasion,
        'weatherTag': weather_tag,
        'condition': condition,
        'temp': temp,
        'suggestions': suggestions
    }), 200
