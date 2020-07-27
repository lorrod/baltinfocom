<h1> Тестовое задание для БалтИнфоКом </h1>

<h3> Описание </h3>

    Веб приложение для получения пользователей групп телеграмма, которые подписаны на 2 и больше заданных групп

    Скрипт для того же функционала "tools/sniff_group_usr.py"
    Запуск "python3 sniff_group_usr.py [TG-URL1] [TG-URL2]"

<h3> Ссылка </h3>

http://balt-info-com.theboxy.ru/

telegrambot: @sniff_user_bot

<h3> Используемые технологии </h3>

* библиотека для обращений к API Telegram - Telethon

* библиотека для обращений к API Telegram - pyTelegramBotAPI

* фреймворк Flask  

* фреймворк Quart

* база данных mongoDB

* nginx для перевода трафика на HTTPS

* Docker для размещения на одном сервере

<h3> Как запустить приложение </h3>

* Получить токен telegram-бота

* Зарегистрировать приложение в telegram и получить API_ID и API_HASH

* Получить ssl сертификат для телеграмм бота

* Использовать скрипт ./init-letsencrypt для получения сертификатов для nginx+certbot

* Заполнить config.py

* Запустить команду docker-compose up


<h3> Telethon </h3>

  Прокси используются лишь для запуска с одного сервера, чтобы использовать другой порт
  !Возможны длительные ответы от quart-сервера, при получении списка групп!
