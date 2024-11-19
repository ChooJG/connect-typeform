from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os
from app.core.config import settings
from app.core.prompts import CURRICULUM_PROMPT
from typing import Dict, Any
import json


router = APIRouter()



class RawDataResponse(BaseModel):
    data_type: str
    raw_data: str
    data_dict: Dict[str, Any] | None


class InputData(BaseModel):
    data: Any


# StudentData 모델 정의
class StudentData(BaseModel):
    name: str
    education: str
    interests: str


# CurriculumResponse 모델 정의
class CurriculumResponse(BaseModel):
    curriculum: str


@router.post("/recommend", response_model=CurriculumResponse)
async def recommend_curriculum(data: StudentData):
    try:
        client = OpenAI(
            api_key=os.getenv('API_KEY', settings.openai_api_key)
        )

        # 질문과 답변을 순차적으로 구성
        messages = [
            {"role": "system", "content": "You are a curriculum advisor."},
            {"role": "assistant", "content": f"학생의 이름: {data.name}"},
            {"role": "user", "content": "최종 학력은 어디인가요?"},
            {"role": "assistant", "content": f"최종 학력: {data.education}"},
            {"role": "user", "content": "주요 관심사는 무엇인가요?"},
            {"role": "assistant", "content": f"관심사: {data.interests}"}
        ]

        # OpenAI API 호출
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )

        print("gpt의 답변 : ", response.choices[0].message.content)

        # ChatGPT의 응답을 CurriculumResponse로 반환
        return CurriculumResponse(curriculum=response.choices[0].message.content)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/log")
async def log_data(request: Request):
    try:
        # 요청 본문을 JSON 형태로 읽어오기
        data = await request.json()

        # 데이터를 보기 좋게 정리하여 출력
        pretty_data = json.dumps(data, ensure_ascii=False, indent=4)

        # 로그 출력
        print(pretty_data)

        return {"message": "Log received", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
