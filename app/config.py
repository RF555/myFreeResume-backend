from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mongodb_uri: str
    jwt_secret: str
    jwt_refresh_secret: str
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 7
    frontend_url: str = "http://localhost:5173"
    google_client_id: str = ""
    google_client_secret: str = ""
    github_client_id: str = ""
    github_client_secret: str = ""
    linkedin_client_id: str = ""
    linkedin_client_secret: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
