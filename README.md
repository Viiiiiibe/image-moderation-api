# image-moderation-api
### API для модерации изображений

API принимает .jpg и .png изображения и отправляет их на модерацию в бесплатный сервис [Sightengine](https://sightengine.com/), чтобы понять, есть ли на них нежелательный контент.
Происходит проверка содержания наготы, оружия, алкоголя, наркотиков, табака, крови, насилия, селфхарма, оскорбительного контента, подозрительного текста и QR-кодов в изображении.
Если nsfw_score > 0.7 → REJECTED, иначе → OK.

- [Локальный запуск с Docker Compose](#Docker_Compose)
- [Локальный запуск без Docker](#No_Docker_Compose)
- [Пример запроса](#Request)

## Локальный запуск с Docker compose <a name="Docker_Compose"></a> 

- Рядом с файлом .env.example разместить .env файл (или просто скопировать .env.example и переименовать в .env). Env переменные:
```  
SIGHTENGINE_API_USER='your_api_user'
SIGHTENGINE_API_SECRET='your_api_secret'
```
Необходимо вставить в .env файл [ваши Sightengine Api-ключи](https://dashboard.sightengine.com/api-credentials)
- Выполнить билд и запуск контейнера
```console  
docker-compose up --build -d
```
Документация к API будет доступна по адресу http://localhost:8000/docs

## Локальный запуск без Docker <a name="No_Docker_Compose"></a> 
- Желательно иметь версию Python 3.12
- Через консоль перейти в папку проекта (image-moderation-api), установить и активировать виртуальное окружение
установка:
```console  
python -m venv venv
```
или
```console  
python3 -m venv venv
```
активация Windows:
```console  
.\venv\Scripts\activate.bat
```
активация macOS и Linux:
```console  
source venv/bin/activate
```
- Установить в виртуальное окружение используемые библиотеки
```console  
pip install -r requirements.txt
``` 
- Рядом с файлом .env.example разместить .env файл (или просто скопировать .env.example и переименовать в .env). Env переменные:
```  
SIGHTENGINE_API_USER='your_api_user'
SIGHTENGINE_API_SECRET='your_api_secret'
```
Необходимо вставить в .env файл [ваши Sightengine Api-ключи](https://dashboard.sightengine.com/api-credentials)
- Через консоль выполнить команду для запуска локального сервера (из папки проекта image-moderation-api):
```console  
uvicorn src.main:app --reload 
```
Документация к API будет доступна по адресу http://localhost:8000/docs

## Пример запроса <a name="Request"></a> 
- Запрос через curl: через консоль перейти в папку с файлом и выполнить команду, вставив имя вашего файла (напрмер ak47.jpg)
```console  
curl -X POST -F "file=@ИМЯ_ВАШЕГО_ФАЙЛА" http://localhost:8000/moderate
```
- Для запроса через UI FastAPI - http://localhost:8000/docs
