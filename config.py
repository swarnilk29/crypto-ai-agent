from dotenv import load_dotenv
import os

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SAFE_API_URL = os.getenv("SAFE_API_URL")
SAFE_WALLET_ADDRESS = os.getenv("SAFE_WALLET_ADDRESS")
ALCHEMY_RPC_URL = os.getenv("ALCHEMY_RPC_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OWNER_PRIVATE_KEY = os.getenv("OWNER_PRIVATE_KEY")
