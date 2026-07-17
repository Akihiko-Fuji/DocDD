from db import DEFAULT_LOCAL_DATABASE_URL, resolve_database_url


def test_database_url_defaults_to_local_teaching_database():
    assert resolve_database_url({}) == DEFAULT_LOCAL_DATABASE_URL


def test_database_url_can_be_overridden_by_environment():
    custom_url = "postgresql+psycopg://example:secret@db.example.invalid/example"
    assert resolve_database_url({"RESULTS_DATABASE_URL": custom_url}) == custom_url
