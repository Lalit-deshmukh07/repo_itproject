from backend.app import create_app
from backend.common.models import User, db


def test_authenticated_user_can_fetch_saved_outfits():
    app = create_app()
    app.config['TESTING'] = True

    with app.app_context():
        db.drop_all()
        db.create_all()
        user = User(first_name='Test', last_name='User', email='profile@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

    with app.test_client() as client:
        login_response = client.post('/api/auth/login', json={'email': 'profile@example.com', 'password': 'password123'})
        assert login_response.status_code == 200

        save_response = client.post('/api/outfit/save', json={
            'occasion': 'Casual Day Out',
            'items': {
                'outerwear': {'name': 'Coat', 'url': 'coat.jpg'},
                'top': {'name': 'Tee', 'url': 'tee.jpg'},
                'bottom': {'name': 'Jeans', 'url': 'jeans.jpg'},
                'shoes': {'name': 'Boots', 'url': 'boots.jpg'},
            },
            'weather': 'Sunny',
            'aiNote': 'Test note'
        })
        assert save_response.status_code == 201

        wardrobe_response = client.get('/api/outfit/get-all')
        assert wardrobe_response.status_code == 200
        payload = wardrobe_response.get_json()
        assert payload['totalOutfits'] == 1
        assert payload['outfits'][0]['occasion'] == 'Casual Day Out'
