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
async def log_data(request: Request):
    try:
        # 요청 본문을 JSON 형태로 읽어오기
        data = await request.json()

        # 질문과 답변을 저장할 리스트
        messages = []

        # 시스템 메시지 추가
        messages.append({"role": "system", "content": "You are a curriculum advisor."})

        # 'fields'와 'answers'에서 질문과 답변 추출
        fields = data['form_response']['definition']['fields']
        answers = data['form_response']['answers']

        # 질문과 답변을 매핑하여 messages 리스트에 추가
        for field, answer in zip(fields, answers):
            question = field['title']
            if answer['type'] == 'text':
                response = answer['text']
            elif answer['type'] == 'choice':
                response = answer['choice']['label']
            else:
                response = "응답 없음"  # 다른 타입에 대한 기본 응답

            messages.append({"role": "assistant", "content": question})
            messages.append({"role": "user", "content": response})

        messages.append({"role": "user", "content": "나에겐 무슨 커리큘럼이 어올릴까?"})

            # OpenAI API 호출
        client = OpenAI(
            api_key=os.getenv('API_KEY', settings.openai_api_key)
        )
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )

        print("gpt 답변 : ", response.choices[0].message.content)

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
