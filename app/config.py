import os
from pathlib import Path

# Load .env file FIRST
env = os.getenv("ENVIRONMENT", "local")

if env == "local":
    from dotenv import load_dotenv

    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(dotenv_path=env_path, override=True)
# ECS: environment variables already injected by task definition
