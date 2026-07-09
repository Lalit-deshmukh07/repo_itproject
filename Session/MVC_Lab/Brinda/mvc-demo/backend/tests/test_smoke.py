def test_client_fixture_wires_alice_as_current_user(client, alice):
    r = client.get("/tasks/")
    assert r.status_code == 200
    assert r.json() == []