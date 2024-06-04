# Build paths inside the project like this: BASE_DIR / 'subdir'.
from pathlib import Path

from split_settings.tools import include, optional

BASE_DIR = Path(__file__).resolve().parent.parent

include(
    'settings_components/base.py',
    'settings_components/application.py',
    'settings_components/database.py',
    'settings_components/rest_framework.py',
    optional('settings_components/local.py')
)