from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # Defanging notation — e.g. example[.]com → example.com
    defang_open: str = "["
    defang_close: str = "]"

    # Auto-incrementing counters
    start_rule_id: int = 10000000
    start_ti_no: int = 1000

    # TI record metadata defaults
    ti_area: str = "etas"
    site_tp: str = "rio"
    reg_user_id: str = "admin"


settings = Settings()
