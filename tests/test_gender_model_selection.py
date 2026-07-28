from backend.auth.routes import _normalize_gender, _select_model_image


def test_normalize_gender_maps_common_values():
    assert _normalize_gender('Male') == 'male'
    assert _normalize_gender('female') == 'female'
    assert _normalize_gender('Diverse') == 'diverse'
    assert _normalize_gender('Non-binary') == 'diverse'


def test_select_model_image_uses_gender_specific_pool():
    male_image = _select_model_image('male', 'casual', 'fallback')
    female_image = _select_model_image('female', 'casual', 'fallback')
    diverse_image = _select_model_image('diverse', 'casual', 'fallback')

    assert male_image.startswith('https://images.unsplash.com/')
    assert female_image.startswith('https://images.unsplash.com/')
    assert diverse_image.startswith('https://images.unsplash.com/')
    assert male_image != female_image
