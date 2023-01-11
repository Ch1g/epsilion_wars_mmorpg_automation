"""Application settings."""
import os

from pydantic import BaseSettings, Field


class AppSettings(BaseSettings):
    """Application settings class."""

    telegram_api_id: int = 123456
    telegram_api_hash: str = 'u_api_hash_here'
    debug: bool = Field(default=False, description='Logging level')
    game_username: str = 'EpsilionWarBot'
    minimum_hp_level_for_grinding: int = Field(default=49, ge=1, le=100)
    auto_healing_enabled: bool = True
    hp_level_for_low_heal_pot: int = Field(default=75, ge=1, le=100)
    hp_level_for_mid_heal_pot: int = Field(default=50, ge=1, le=100)
    ping_message: str = '/me'
    message_log_limit: int = 100
    character_high_level_threshold: int = 20
    character_middle_level_threshold: int = 10


app_settings = AppSettings(
    _env_file=os.path.join(os.path.dirname(__file__), '..', '.env'),
)
