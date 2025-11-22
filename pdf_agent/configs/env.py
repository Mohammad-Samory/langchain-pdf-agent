from os import getenv

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database Configuration (optional - can be removed if not using DB)
DB_HOST = getenv('DB_HOST', 'localhost')
DB_NAME = getenv('DB_NAME', 'postgres')
DB_PASSWORD = getenv('DB_PASSWORD', 'postgres')
DB_PORT = getenv('DB_PORT', '5432')
DB_USERNAME = getenv('DB_USERNAME', 'postgres')

# Application Configuration
ENVIRONMENT = getenv('ENVIRONMENT', 'development')
LOG_LEVEL = getenv('LOG_LEVEL', 'INFO')

# LLM Provider Configuration
LLM_PROVIDER = getenv('LLM_PROVIDER', 'google')

# OpenAI Configuration
OPENAI_API_KEY = getenv('OPENAI_API_KEY', '')

# Google Gemini Configuration
GOOGLE_API_KEY = getenv('GOOGLE_API_KEY', '')

# Agent Configuration
LLM_MODEL = getenv('LLM_MODEL', 'gpt-4o-mini')
LLM_TEMPERATURE = float(getenv('LLM_TEMPERATURE', '0.0'))
CHUNK_SIZE = int(getenv('CHUNK_SIZE', '1000'))
CHUNK_OVERLAP = int(getenv('CHUNK_OVERLAP', '200'))
EMBEDDING_MODEL = getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
