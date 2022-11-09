import pytest

@pytest.mark.django_db
def test_utils(client):
	path = "/all_games"
	response = client.get(path)
	assert True