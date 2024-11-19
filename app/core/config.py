import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수를 로드
load_dotenv()


class Settings:
    def __init__(self):
        # 환경 변수 불러오기
        self.openai_api_key = os.getenv("OPENAI_API_KEY")


# settings 인스턴스 생성
settings = Settings()
