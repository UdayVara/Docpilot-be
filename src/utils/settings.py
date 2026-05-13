from pydantic_settings import BaseSettings, SettingsConfigDict


class SettingsSetup(BaseSettings):
    app_name: str
    DATABASE_URL: str
    SECRET_KEY: str

    CLOUDINARY_API_KEY:str
    CLOUDINARY_API_SECRET:str
    CLOUDINARY_CLOUD_NAME:str

    model_config = SettingsConfigDict(env_file=".env")

Settings = SettingsSetup()

