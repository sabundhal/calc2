# Каталог книг - Flask Vue API

### Этот проект представляет собой простой каталог книг. 
 
В его функционал входит:

* Регистрация: Пользователи могут зарегистрироваться в системе, создавая учетные записи с помощью формы регистрации.

* Список книг: В сервисе доступен список книг (персональный для каждого пользователя), который можно добавлять, просматривать, обновлять и удалять.


Пример поднятого севиса можно посмотреть по ссылке [Books](http://9b142cdd34e.vps.myjino.ru:49274/books)

Рабочий docker контейнер можно скачать по ссылке из [Docker hub](https://hub.docker.com/repository/docker/testinginpractice/flask_vue/tags)

Запуск и настройка приложения производились на Pithon 3.11 и Node.js 20.11.0 lts

# Для запуска клиента локально, необходимо выполнить следующие действия
### переходим в директорию с клиентом
```bash
cd client
```
### Установаем все зависимости, указанные в файле package.json
```bash
npm install
```
### Запуск приложения Vue
```bash
npm run dev
```

# Для запуска сервера локально, необходимо выполнить следующие действия
### переходим в директорию с сервером
```bash
cd server
```
### Установка зависимостей Python
```bash
pip install -r requirements.txt
```
### Запуск приложения Flask
```bash
python app.py
```

### Эндпоинты
* POST /api/register: Регистрация нового пользователя. Ожидает JSON с полями username и password.
```bash
Ожидает JSON
{
  "username": "example@example.com",
  "password": "example_password"
}
```
* POST /api/login: Вход пользователя. Ожидает JSON с полями username и password. Возвращает JWT токен для аутентификации.
```bash
Ожидает JSON
{
  "username": "example@example.com",
  "password": "example_password"
}
```
* GET /api/books: Получение списка книг пользователя. Требуется авторизация через JWT токен.
* POST /api/books: Добавление новой книги в каталог пользователя. Требуется авторизация через JWT токен.
```bash
Ожидает JSON
{
  "title": "Example Book",
  "author": "John Doe",
  "read": false
}
```
* GET /api/books/<book_id>: Получение информации о конкретной книге по ее ID. Требуется авторизация через JWT токен.
* PUT /api/books/<book_id>: Обновление информации о конкретной книге по ее ID. Требуется авторизация через JWT токен. 
```bash
Ожидает JSON
{
  "title": "Example Book",
  "author": "John Doe",
  "read": false
}
```
* DELETE /api/books/<book_id>: Удаление конкретной книги по ее ID. Требуется авторизация через JWT токен.

# Для запуска сервиса в Docker контейнере, необходимо выполнить следующие действия
### Установка Docker если не устанвлен
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```
### Сборка Docker-образа
```bash
sudo docker image build -t flask_vue .
```
### Запуск Docker-контейнера
```bash
docker run -d -p 8080:80 flask_vue
```