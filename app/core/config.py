import os

from dotenv import load_dotenv
from starlette.datastructures import CommaSeparatedStrings, Secret
from databases import DatabaseURL

DEBUG = True

API_V1_STR = "/api"

JWT_TOKEN_PREFIX = "Bearer"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # one week

load_dotenv(".env")

MAX_CONNECTIONS_COUNT = int(os.getenv("MAX_CONNECTIONS_COUNT", 10))
MIN_CONNECTIONS_COUNT = int(os.getenv("MIN_CONNECTIONS_COUNT", 10))
SECRET_KEY = Secret(os.getenv("SECRET_KEY", "asdsd"))

PROJECT_NAME = os.getenv("PROJECT_NAME", "New Glot API")
ALLOWED_HOSTS = CommaSeparatedStrings(os.getenv("ALLOWED_HOSTS", "~g998rIX:O+jmxg3L@.U1[,/.jHbD8nRm(^Y&b$zHF*b09R@L9mmyKlcy]aGr3?"))

MONGODB_URL = os.getenv("MONGODB_URL", "")  # deploying without docker-compose

DESCRIPTION = """
Glot API helps you do awesome stuff. 🚀\n
Glot API поможет вам делать потрясающие вещи. 🚀
"""

if DEBUG is True:
    MONGODB_URL = DatabaseURL(
        f"mongodb://localhost:27017/"
    )
else:
    if not MONGODB_URL:

        MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
        MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
        MONGO_USER = os.getenv("MONGO_USER", "")
        MONGO_PASS = os.getenv("MONGO_PASSWORD", "")
        MONGO_DB = os.getenv("MONGO_DB", "main")

        MONGODB_URL = DatabaseURL(
            f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}"
        )
    else:
        MONGODB_URL = DatabaseURL(MONGODB_URL)

database_name = "main"
database_name_messages = "messages"
users_collection_name = "users"
device_collection_name = "devices"

