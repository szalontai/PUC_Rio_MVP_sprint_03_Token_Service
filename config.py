from pydantic import BaseSettings
import random
import string
import os
from datetime import timedelta

from dotenv import load_dotenv
load_dotenv()


# Gera uma chave aleatória para aplicação a cada execução do servidor

gen = string.ascii_letters + string.digits + string.ascii_uppercase
key = ''.join(random.choice(gen) for i in range(12))

JWT_SECRET_KEY = key  # Change this!
JWT_COOKIE_SECURE = os.getenv('JWT_COOKIE_SECURE')
JWT_TOKEN_LOCATION = os.getenv('JWT_TOKEN_LOCATION')
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
JWT_REFRESH_COOKIE_NAME= os.getenv('JWT_REFRESH_COOKIE_NAME')
DEBUG = os.getenv('DEBUG')
JSON_SORT_KEYS = os.getenv('JSON_SORT_KEYS')

PASSWORD_RESET_EXPIRATION_HOURS = os.getenv('PASSWORD_RESET_EXPIRATION_HOURS')
EMAIL_URL = os.getenv('EMAIL_URL')
PHOTO_URL = os.getenv('PHOTO_URL')
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER')
CEP_URL = os.getenv('CEP_URL')

