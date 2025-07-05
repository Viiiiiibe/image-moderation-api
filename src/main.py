from fastapi import FastAPI, UploadFile, File, HTTPException
import requests
from typing import Dict, Any
from src.config import SIGHTENGINE_API_URL, SIGHTENGINE_API_USER, SIGHTENGINE_API_SECRET, THRESHOLD

app = FastAPI()


@app.get("/")
async def root():
    return {
        "message": "Welcome to the image-moderation-api! The API accepts `.jpg` and `.png` images and sends them for "
                   "moderation to see if there is any unwanted content on them. "
                   "To moderate, send a POST request with an image to `/moderate`."
    }


@app.post("/moderate")
async def moderate_image(file: UploadFile = File(...)):
    if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Only JPEG/PNG images are accepted"
        )

    try:
        # Чтение содержимого файла
        file_content = await file.read()

        # Параметры запроса с полным списком моделей проверок
        data = {
            'models': 'nudity-2.1,weapon,alcohol,recreational_drug,medical,offensive-2.0,text-content,face-attributes,gore-2.0,text,qr-content,tobacco,violence,self-harm',
            'api_user': SIGHTENGINE_API_USER,
            'api_secret': SIGHTENGINE_API_SECRET
        }

        # Отправка файла в Sightengine API
        files = {"media": (file.filename, file_content)}
        response = requests.post(
            SIGHTENGINE_API_URL,
            files=files,
            data=data
        )

        # Проверка статуса ответа
        if response.status_code != 200:
            error_data = response.json()
            error_msg = error_data.get("error", {}).get("message", response.text)
            raise HTTPException(
                status_code=502,
                detail=f"Sightengine API error: {error_msg}"
            )

        # Анализ результатов
        result: Dict[str, Any] = response.json()

        # Словарь для сбора всех результатов
        content_scores = {}

        # Проверка наготы (nudity-2.1)
        if "nudity" in result:
            nudity = result["nudity"]
            nsfw_score = max(
                nudity.get("sexual_activity", 0),
                nudity.get("sexual_display", 0),
                nudity.get("erotica", 0),
                nudity.get("very_suggestive", 0),
                nudity.get("suggestive", 0)
            )
            content_scores["nudity"] = nsfw_score
            if nsfw_score > THRESHOLD:
                return {"status": "REJECTED", "reason": "NSFW content"}

        # Проверка оружия (weapon)
        if "weapon" in result:
            weapon_classes = result["weapon"].get("classes", {})
            weapon_score = max(weapon_classes.values()) if weapon_classes else 0
            content_scores["weapon"] = weapon_score
            if weapon_score > THRESHOLD:
                return {"status": "REJECTED", "reason": "NSFW content"}

        # Проверка алкоголя (alcohol)
        if "alcohol" in result:
            alcohol_score = result["alcohol"].get("prob", 0)
            content_scores["alcohol"] = alcohol_score
            if alcohol_score > THRESHOLD:
                return {"status": "REJECTED", "reason": "NSFW content"}

        # Проверка наркотиков (recreational_drug)
        if "recreational_drug" in result:
            drug_score = result["recreational_drug"].get("prob", 0)
            content_scores["recreational_drug"] = drug_score
            if drug_score > THRESHOLD:
                return {"status": "REJECTED", "reason": "NSFW content"}

        # Проверка медицинского контента (medical)
        if "medical" in result:
            medical_score = result["medical"].get("prob", 0)
            content_scores["medical"] = medical_score
            if medical_score > THRESHOLD:
                return {"status": "REJECTED", "reason": "NSFW content"}

        # Проверка оскорбительного контента (offensive)
        if "offensive" in result:
            offensive_categories = [
                "nazi", "confederate", "supremacist",
                "terrorist", "middle_finger"
            ]
            offensive_score = max(
                result["offensive"].get(cat, 0)
                for cat in offensive_categories
            )
            content_scores["offensive"] = offensive_score
            if offensive_score > THRESHOLD:
                return {"status": "REJECTED", "reason": "NSFW content"}

        # Проверка сцен крови (gore)
        if "gore" in result:
            gore_score = result["gore"].get("prob", 0)
            content_scores["gore"] = gore_score
            if gore_score > THRESHOLD:
                return {"status": "REJECTED", "reason": "NSFW content"}

        # Проверка табака (tobacco)
        if "tobacco" in result:
            tobacco_score = result["tobacco"].get("prob", 0)
            content_scores["tobacco"] = tobacco_score
            if tobacco_score > THRESHOLD:
                return {"status": "REJECTED", "reason": "NSFW content"}

        # Проверка насилия (violence)
        if "violence" in result:
            violence_score = result["violence"].get("prob", 0)
            content_scores["violence"] = violence_score
            if violence_score > THRESHOLD:
                return {"status": "REJECTED", "reason": "NSFW content"}

        # Проверка селфхарма (self-harm)
        if "self-harm" in result:
            self_harm_score = result["self-harm"].get("prob", 0)
            content_scores["self-harm"] = self_harm_score
            if self_harm_score > THRESHOLD:
                return {"status": "REJECTED", "reason": "NSFW content"}

        # Проверка текста (text)
        if "text" in result:
            # Флаги для различных типов нежелательного текста
            text_flags = [
                "profanity", "personal", "extremism",
                "drug", "weapon", "violence", "self-harm"
            ]
            text_issues = any(
                result["text"].get(flag, [])
                for flag in text_flags
            )
            content_scores["text"] = 1.0 if text_issues else 0.0
            if text_issues:
                return {"status": "REJECTED", "reason": "NSFW content"}

        # Проверка QR-кодов (qr)
        if "qr" in result:
            # Флаги для нежелательных QR-кодов
            qr_flags = ["personal", "spam", "profanity", "blacklist"]
            qr_issues = any(
                result["qr"].get(flag, [])
                for flag in qr_flags
            )
            content_scores["qr"] = 1.0 if qr_issues else 0.0
            if qr_issues:
                return {"status": "REJECTED", "reason": "NSFW content"}

        return {"status": "OK"}

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
