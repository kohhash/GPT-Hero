import os
from pathlib import Path

import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Access environment variables
OPEN_API_KEY = os.getenv('OPEN_API_KEY')
PWAID_KEY = os.getenv('PWAID_KEY')
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
STRIPE_WEBHOOK = os.getenv("STRIPE_WEBHOOK")

BASE_DIR = Path(__file__).resolve().parent.parent
class Configuration:

    class Google:
        CLIENT_ID = CLIENT_ID
        CLIENT_SECRET = CLIENT_SECRET

    class Ngrok:
        # URL = "https://62dd-49-43-25-97.ngrok-free.app"
        URL = "https://popular-lamb-sunny.ngrok-free.app"

    class STRIPE_API:
        PUBLICK_KEY = "pk_test_51N1NfgSHA9iK3eg2GgVRnYXM9VFpc2j2BSXXqKE2bbJ28Zk6zUP9fneBdYX74ssz1Kvg6tB3dlreceu6ySnXuSY100p8O2FCE0"
        PRIVATE_KEY = PRIVATE_KEY
        REDIRECT_URI = "http://127.0.0.1:8000"
        STRIPE_WEBHOOK_SECRET = STRIPE_WEBHOOK_SECRET

    class ResourceValues:
        user_description_api = ""
        approach_api_description = ""
        approach_default_val = ""
        context_tooltip = ""

    class DefaultValues:
        config_file_path =  BASE_DIR/ "app/data/config-1.ini"
        database_path = BASE_DIR / "db.sqlite3"
        PROWRITINGAID_API_KEY = PWAID_KEY
        OPEN_API_KEY = OPEN_API_KEY


    class Environment:
        DEVELOPMENT = "development"
        PRODUCTION = "production"
        TESTING = "testing"
        STAGING = "staging"
        LOCAL = "local"
        APP_URL = os.environ.get("APP_URL", "http://localhost:8000")