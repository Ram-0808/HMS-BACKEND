import os
import sys
from pathlib import Path

# Add the project root to Python path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital.settings')

from django.core.wsgi import get_wsgi_application  # noqa: E402

app = get_wsgi_application()
