from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os
from app.core.config import settings
from app.core.prompts import CURRICULUM_PROMPT
from typing import Dict, Any


router = APIRouter()

class StudentData(BaseModel):
    background: str
    goals: str
    current_level: str


class CurriculumResponse(BaseModel):
    curriculum: str


class RawDataResponse(BaseModel):
    data_type: str
    raw_data: str
    data_dict: Dict[str, Any] | None


class InputData(BaseModel):
    data: Any


@router.post("/recommend", response_model=CurriculumResponse)
async def recommend_curriculum(data: StudentData):
    try:
        formatted_data = f"""
        Background: {data.background}
        Goals: {data.goals}
        Current Level: {data.current_level}
        """
        client = OpenAI(
            api_key=os.getenv('API_KEY', settings.openai_api_key)
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a curriculum advisor."},
                {"role": "user", "content": CURRICULUM_PROMPT.format(student_data=formatted_data)}
            ]
        )

        return CurriculumResponse(curriculum=response.choices[0].message.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/test", response_model=RawDataResponse)
async def log_raw_data(data: InputData):
    try:
        # OpenAI 클라이언트 초기화
        client = OpenAI(
            api_key=os.getenv('API_KEY', settings.openai_api_key)
        )

        # ChatGPT에 메시지 전송
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # 사용할 모델
            messages=[
                {"role": "user", "content": data.message}
            ]
        )

        # 응답 메시지 추출
        chat_response = response.choices[0].message.content

        return RawDataResponse(
            data_type=str(type(data)),
            raw_data=chat_response,
            data_dict=data.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




@router.post("/log", response_model=RawDataResponse)
async def log_raw_data(data: InputData):
    try:

        print("타입 : ", type(data))
        print("데이터 : ", data)
        print("출력 : ", data.dict() if hasattr(data, "dict") else None)

        return RawDataResponse(
            data_type=str(type(data)),
            raw_data=str(data),
            data_dict=data.dict() if hasattr(data, "dict") else None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))