import pytest
from django.conf import settings

@pytest.fixture(scope='session')
def django_db_setup():
    """Configure test database"""
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }