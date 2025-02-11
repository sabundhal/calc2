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

Основные поля, которые можно выделить:

tabletOnly: Является ли препарат только таблеткой (булево значение).
mlsvar: Объем в миллилитрах на единицу дозы.
mgsvar: Доза в миллиграммах на единицу дозы.
numberOfTimesADay: Частота приема в день.
mlsmax: Максимальный объем в миллилитрах.
mgsmax: Максимальная доза в миллиграммах.
loadingdose: Наличие ударной дозы (булево значение).
mlsvarloading: Объем ударной дозы в миллилитрах.
mgsvarloading: Доза ударной дозы в миллиграммах.
mlsmaxloading: Максимальный объем ударной дозы.
mgsmaxloading: Максимальная доза ударной дозы.
instructions: Инструкции по применению.
nzflink: Ссылка на NZ Formulary.

CREATE TABLE IF NOT EXISTS calculation_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,           -- ID пользователя, выполнившего расчет
    drug_id INTEGER NOT NULL,           -- ID препарата
    drug_name TEXT,                     -- Название препарата
    username TEXT,                      -- Имя пользователя
    weight REAL NOT NULL,               -- Вес пациента
    dosage_mls REAL,                    -- Доза в мл
    dosage_mgs REAL,                    -- Доза в мг
    totalMgs REAL,                      -- Общее количество мг
    totalhigh REAL,                     -- Высокая доза с модификатором
    totalhighsachets REAL,              -- Расчет сашетов
    maximumMgsPerDay REAL,              -- Максимальная доза в мг в день
    highMgs REAL,                       -- Максимальная доза для высокого диапазона
    loading_dose INTEGER,               -- Загрузочная доза
    strep_drug INTEGER,                 -- Флаг стрептококкового препарата
    messageMgs TEXT,                    -- Сообщение о дозе в мг
    messageOther TEXT,                  -- Другое сообщение
    calculation_type TEXT,              -- Тип расчета (например, "стандартный", "загрузочный")
    calculation_status TEXT,            -- Статус расчета (например, "успешно", "ошибка")
    calculation_version TEXT,           -- Версия алгоритма расчета
    patient_id INTEGER,                 -- ID пациента (если расчеты связаны с пациентами)
    patient_name TEXT,                  -- Имя пациента (удобно для анализа без JOIN)
    error_message TEXT,                 -- Лог ошибки (если расчет завершился ошибкой)
    calculation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Время выполнения расчета
);

name: 'Paracetamol120' — название препарата.
category_id: 1 — ID категории (предполагаем, что 1 — категория "Анальгетики").
tablet_only: False — не таблетированная форма.
mls_var: 0.625 — мл на кг веса для стандартной дозы.
mgs_var: 15 — мг на кг веса для стандартной дозы.
number_of_times_a_day: 'every four hours, up to a maximum of four doses in 24 hours' — частота приема.
mls_max: 42 — максимальный объем (мл) за один прием.
mgs_max: 1000 — максимальная доза (мг) за один прием.
loading_dose: True — загрузочная доза разрешена.
mls_var_loading: 1.25 — мл на кг веса для загрузочной дозы.
mgs_var_loading: 30 — мг на кг веса для загрузочной дозы.
mls_max_loading: 62.5 — максимальный объем (мл) для загрузочной дозы.
mgs_max_loading: 1500 — максимальная доза (мг) для загрузочной дозы.
instructions: '<div class=\'message__section-dosing-item message__section-dosing-label\'><strong>General Dosing:</strong> <br> <div class=\'message__section-dosing-instructions\'><span class=\'age-group\'>1 month - 18 years</span> 15 mg/kg per dose (maximum 1 g) every four hours; maximum 75 mg/kg per day (without exceeding 4 g) for 48 hours, maximum of 60 mg/kg per day (without exceeding 4 g) thereafter <br> <span class=\'age-group\'> Note</span> A loading dose of 30 mg/kg (maximum 1.5 g) may be given provided there has been no paracetamol given within the preceding 12 hours</div></div>' — инструкции по применению.
nzf_link: 'https://nzfchildren.org.nz/nzf_2439' — ссылка на источник.
high_range: False — нет диапазона верхней дозы.
high_modifier: None — модификатор верхней дозы не указан.
mls_max_high: None — максимальный объем для верхней дозы не указан.
mgs_max_high: None — максимальная доза для верхней дозы не указан.
strep_drug: False — не используется для лечения стрептококковой инфекции.
strep_frequency: '' — частота приема для стрептококковой инфекции не указана.
mls_var_strep: None — мл на кг веса для стрептококковой инфекции не указаны.
mgs_var_strep: None — мг на кг веса для стрептококковой инфекции не указаны.
mls_strep_max: None — максимальный объем для стрептококковой инфекции не указан.
mgs_strep_max: None — максимальная доза для стрептококковой инфекции не указана.