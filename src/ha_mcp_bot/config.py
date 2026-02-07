import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration class that loads from environment variables with sensible defaults."""

    # Server settings
    HOST: str = os.getenv("HOST", "localhost")
    PORT: int = int(os.getenv("PORT", "5555"))
    MCP_SCOPE: str = os.getenv("MCP_SCOPE", "mcp:tools")
    OAUTH_STRICT: bool = os.getenv("OAUTH_STRICT", "false").lower() in ("true", "1", "yes")
    TRANSPORT: str = os.getenv("TRANSPORT", "streamable-http")
    DEBUG: str = os.getenv("DEBUG", "true") == 'true'

    # API Configuration
    HA_URL: str = os.getenv('HA_URL', "http://homeassistant.local:8123/api/")
    HA_TOKEN: str = os.getenv('HA_TOKEN')


    def validate(self) -> None:
        """Validate configuration."""
        if not self.HA_TOKEN:
            raise ValueError("HA_TOKEN is missing.")
        

config = Config()
