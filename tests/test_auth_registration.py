import pytest

import backend.app as backend_app
from backend.app import app, create_app
from backend.common.models import db


@pytest.fixture
def client():
    app.config.update(TESTING=True, SQLALCHEMY_DATABASE_URI='sqlite:///:memory:')
    with app.app_context():
        db.drop_all()
        db.create_all()
        with app.test_client() as client:
            yield client
        db.session.remove()
        db.drop_all()


def test_register_accepts_form_data_with_snake_case_fields(client):
    response = client.post(
        '/api/auth/register',
        data={
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'form@example.com',
            'password': 'password123',
            'consent': 'on',
        },
        content_type='application/x-www-form-urlencoded'
    )

    assert response.status_code == 201
    payload = response.get_json()
    assert payload['message'] == 'Registered successfully'
    assert payload['user']['email'] == 'form@example.com'


def test_localhost_profile_requests_redirect_to_loopback_host(client):
    response = client.get('/profile', base_url='http://localhost:5001')

    assert response.status_code == 307
    assert response.headers['Location'].startswith('http://127.0.0.1:5001/profile')


def test_auth_status_returns_profile_details_from_database(client):
    register_response = client.post(
        '/api/auth/register',
        json={
            'firstName': 'Profile',
            'lastName': 'User',
            'email': 'profile@example.com',
            'password': 'password123',
            'consent': True,
        }
    )
    assert register_response.status_code == 201

    preferences_response = client.post(
        '/api/user/preferences',
        json={
            'gender': 'Female',
            'topSize': 'M',
            'bottomSize': 'L',
            'styles': ['casual', 'formal'],
            'exclusions': ['leather']
        }
    )
    assert preferences_response.status_code == 200

    status_response = client.get('/api/auth/status')
    assert status_response.status_code == 200

    payload = status_response.get_json()
    assert payload['authenticated'] is True
    assert payload['user']['name'] == 'Profile User'
    assert payload['user']['email'] == 'profile@example.com'
    assert payload['user']['gender'] == 'Female'
    assert payload['user']['topSize'] == 'M'
    assert payload['user']['bottomSize'] == 'L'
    assert payload['user']['styles'] == ['casual', 'formal']
    assert payload['user']['exclusions'] == ['leather']


def test_saved_outfits_are_available_on_the_profile_wardrobe(client):
    client.post(
        '/api/auth/register',
        json={
            'firstName': 'Wardrobe',
            'lastName': 'User',
            'email': 'wardrobe@example.com',
            'password': 'password123',
            'consent': True,
        }
    )

    save_response = client.post(
        '/api/outfit/save',
        json={
            'occasion': 'Casual Day Out',
            'items': {
                'outerwear': {'name': 'Light Jacket', 'url': 'https://example.com/jacket.jpg'},
                'top': {'name': 'White Tee', 'url': 'https://example.com/top.jpg'},
                'bottom': {'name': 'Blue Jeans', 'url': 'https://example.com/bottom.jpg'},
                'shoes': {'name': 'Sneakers', 'url': 'https://example.com/shoes.jpg'}
            },
            'weather': 'Sunny, 24°C',
            'aiNote': 'Relaxed daytime look'
        }
    )

    assert save_response.status_code == 201

    wardrobe_response = client.get('/api/outfit/get-all')
    assert wardrobe_response.status_code == 200

    payload = wardrobe_response.get_json()
    assert payload['totalOutfits'] == 1
    assert payload['outfits'][0]['occasion'] == 'Casual Day Out'
    assert payload['outfits'][0]['items']['top']['name'] == 'White Tee'


def test_auth_register_bootstraps_missing_tables_before_request(tmp_path, monkeypatch):
    db_dir = tmp_path / 'instance'
    db_dir.mkdir(parents=True, exist_ok=True)
    sessions_dir = db_dir / 'sessions'
    sessions_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(backend_app, 'DB_PATH', db_dir)
    monkeypatch.setattr(backend_app, 'SESSION_PATH', sessions_dir)

    test_app = create_app()
    test_app.config.update(TESTING=True)

    with test_app.app_context():
        db.drop_all()
        with test_app.test_client() as client:
            response = client.post(
                '/api/auth/register',
                json={
                    'firstName': 'Bootstrap',
                    'lastName': 'User',
                    'email': 'bootstrap@example.com',
                    'password': 'password123',
                    'consent': True,
                }
            )

    assert response.status_code == 201
    assert response.get_json()['message'] == 'Registered successfully'
