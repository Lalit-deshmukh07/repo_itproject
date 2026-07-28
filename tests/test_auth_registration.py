import pytest

from backend.app import app
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
