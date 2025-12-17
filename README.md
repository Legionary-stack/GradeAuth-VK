## Установка зависимостей:
`pip install -r requirements.txt`

## Создание .env файла:
Создате файл `.env` в корне проекта:
```env
VK_CLIENT_ID=ваш_ID_приложения
VK_CLIENT_SECRET=ваш_секретный_ключ
SECRET_KEY=super_secret_string_12345
```


## Генерация SSL:
`mkcert localhost 127.0.0.1`

## Запуск:
`sudo uvicorn main:app --reload --port 443 --ssl-keyfile localhost+1-key.pem --ssl-certfile localhost+1.pem`
