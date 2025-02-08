from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
import sqlite3
import hashlib

##
# Создание Flask-приложения
app = Flask(__name__)
# Подключение к базе данных

def initialize_database():
    conn = sqlite3.connect('myapp.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Устанавливаем row_factory для доступа по именам колонок
    cursor = conn.cursor()

    try:
        cursor.execute('''CREATE TABLE IF NOT EXISTS users
                  (id INTEGER PRIMARY KEY, username TEXT, email TEXT UNIQUE, password TEXT)''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS products
                  (id INTEGER PRIMARY KEY, name TEXT, category TEXT, price REAL, discount REAL)''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS carts
                  (id INTEGER PRIMARY KEY, user_id INTEGER, total_price REAL, total_discount REAL)''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS cart_items
                  (id INTEGER PRIMARY KEY, cart_id INTEGER, product_id INTEGER, quantity INTEGER)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS drugs_categories
                  (category_id SERIAL PRIMARY KEY, category_name TEXT NOT NULL)''')

        drugs_categories = [
            (1, 'Analgesics'),
            (2, 'Antibiotics'),
            (3, 'Anti-inflammatory'),
            (4, 'Antipyretic'),
            (5, 'Antiviral')
        ]
        cursor.executemany("INSERT INTO drugs_categories (category_id, category_name) VALUES (?, ?)", drugs_categories)

# Новая таблица для препаратов
        cursor.execute('''CREATE TABLE IF NOT EXISTS drugs
                (id INTEGER PRIMARY KEY,
                 category_id SERIAL,
                 name TEXT UNIQUE,
                 tablet_only INTEGER,
                 mls_var REAL,
                 mgs_var REAL,
                 number_of_times_a_day TEXT,
                 mls_max REAL,
                 mgs_max REAL,
                 loading_dose INTEGER,
                 mls_var_loading REAL,
                 mgs_var_loading REAL,
                 mls_max_loading REAL,
                 mgs_max_loading REAL,
                 instructions TEXT,
                 nzf_link TEXT,
                 high_range INTEGER,
                 high_modifier REAL,
                 mls_max_high REAL,
                 mgs_max_high REAL,
                 strep_drug INTEGER,
                 strep_frequency TEXT,
                 mls_var_strep REAL,
                 mgs_var_strep REAL,
                 mls_strep_max REAL,
                 mgs_strep_max REAL)''')

# Заполнение данных препаратов (пример для нескольких записей)
        drugs_data = [
            ('Paracetamol120',1, False, 0.625, 15, 'every four hours, up to a maximum of four doses in 24 hours', 42, 1000, True,
     1.25, 30, 62.5, 1500,
     '<div class=\'message__section-dosing-item message__section-dosing-label\'><strong>General Dosing:</strong> <br> <div class=\'message__section-dosing-instructions\'><span class=\'age-group\'>1 month - 18 years</span> 15 mg/kg per dose (maximum 1 g) every four hours; maximum 75 mg/kg per day (without exceeding 4 g) for 48 hours, maximum of 60 mg/kg per day (without exceeding 4 g) thereafter <br> <span class=\'age-group\'> Note</span> A loading dose of 30 mg/kg (maximum 1.5 g) may be given provided there has been no paracetamol given within the preceding 12 hours</div></div>',
     'https://nzfchildren.org.nz/nzf_2439', False, None, None, None, False, '', None, None, None, None),
            ('Paracetamol250',1, False, 0.3, 15, 'every four hours, up to a maximum of four doses in 24 hours', 20, 1000, True,
     0.6, 30, 30, 1500,
     '<div class=\'message__section-dosing-item message__section-dosing-label\'><strong>General Dosing:</strong> <br> <div class=\'message__section-dosing-instructions\'><span class=\'age-group\'>1 month - 18 years</span> 15 mg/kg per dose (maximum 1 g) every four hours; maximum 75 mg/kg per day (without exceeding 4 g) for 48 hours, maximum of 60 mg/kg per day (without exceeding 4 g) thereafter <br> <span class=\'age-group\'> Note</span> A loading dose of 30 mg/kg (maximum 1.5 g) may be given provided there has been no paracetamol given within the preceding 12 hours</div></div>',
     'https://nzfchildren.org.nz/nzf_2439', False, None, None, None, False, '', None, None, None, None),
    ('Paracetamol120nonloading', 1,  False, 0.625, 15, 'every four hours, up to a maximum of four doses in 24 hours', 42,
     1000, False, 1.25, 30, 62.5, 1500,
     '<div class=\'message__section-dosing-item message__section-dosing-label\'><strong>General Dosing:</strong> <br> <div class=\'message__section-dosing-instructions\'><span class=\'age-group\'>1 month - 18 years</span> 15 mg/kg per dose (maximum 1 g) every four hours; maximum 75 mg/kg per day (without exceeding 4 g) for 48 hours, maximum of 60 mg/kg per day (without exceeding 4 g) thereafter</div></div>',
     'https://nzfchildren.org.nz/nzf_2439', False, None, None, None, False, '', None, None, None, None),
    (
    'Paracetamol250nonloading', 1, False, 0.3, 15, 'every four hours, up to a maximum of four doses in 24 hours', 20, 1000,
    False, 0.6, 30, 30, 1500,
    '<div class=\'message__section-dosing-item message__section-dosing-label\'><strong>General Dosing:</strong> < br> <div class=\'message__section-dosing-instructions\'><span class=\'age-group\'>1 month - 18 years</span> 15 mg/kg per dose (maximum 1 g) every four hours; maximum 75 mg/kg per day (without exceeding 4 g) for 48 hours, maximum of 60 mg/kg per day (without exceeding 4 g) thereafter</div></div>',
    'https://nzfchildren.org.nz/nzf_2439', False, None, None, None, False, '', None, None, None, None),
    ('Ibuprofen100',1, False, 0.25, 5, 'three to four times a day', 10, 200, False, None, None, None, None,
     '<div class=\'message__section-dosing-item message__section-dosing-label\'><strong>General Dosing:</strong> <br> <div class=\'message__section-dosing-instructions\'><span class=\'age-group\'>1 - 3 months</span> 5 mg/kg 3-4 times daily <br> <span class=\'age-group\'> 3 months - 18 years</span> 5-10 mg/kg 3 or 4 times daily up to 30 mg/kg daily (maximum 2.4 g daily)</div></div>',
     'https://nzfchildren.org.nz/nzf_5524', True, 2, 20, 400, False, '', None, None, None, None),
    ('Ibuprofen100norange',1, False, 0.3, 6, 'three times a day', 20, 400, False, None, None, None, None,
     '<div class=\'message__section-dosing-item message__section-dosing-label\'><strong>General Dosing:</strong> <br> <div class=\'message__section-dosing-instructions\'><span class=\'age-group\'>3 months - 18 years</span> 6 mg/kg per dose (maximum 400mg) every 8 hours as needed for pain or fever. Do not take more than 3 doses in 24 hours.</div></div>',
     'https://nzfchildren.org.nz/nzf_5524', False, 2, 20, 400, False, '', None, None, None, None),
    ('Ibuprofen200norange', 1, False, 0.15, 6, 'three times a day', 10, 400, False, None, None, None, None,
     '<div class=\'message__section-dosing-item message__section-dosing-label\'><strong>General Dosing:</strong> <br> <div class=\'message__section-dosing-instructions\'><span class=\'age-group\'>3 months - 18 years</span> 6 mg/kg per dose (maximum 400mg) every 8 hours as needed for pain or fever. Do not take more than 3 doses in 24 hours.</div></div>',
     'https://nzfchildren.org.nz/nzf_5524', False, 2, 10, 400, False, '', None, None, None, None),
    ('Amoxicillin125', 2, False, 0.6, 15, 'three times a day', 40, 1000, False, None, None, None, None,
     '<div class=\'message__section-dosing-item message__section-dosing-label\'><strong>General Dosing:</strong> <br> <div class=\'message__section-dosing-instructions\'><span class=\'age-group\'>1 month - 18 years</span> 15 - 30mg/kg (maximum 1,000mg) three times daily </div> <strong>Strep A Dosing:</strong> <div class=\'message__section-dosing-instructions\'><span class=\'age-group\'>Under 15kg</span> 50mg/kg once daily for 10 days<br> <span class=\'age-group\'> 15 - 29.9kg</span> 750mg once daily for 10 days<br><span class=\'age-group\'> 30kg or over</span> 1,000mg once daily for 10 days</div></div>',
     'https://nzfchildren.org.nz/nzf_3025', True, 2, 40, 1000, True, 'once daily for 10 days', 30, 50, 40, 1000),
    ("Amoxicillin250", 2, False, 0.3, 15, "three times a day", 20, 1000, True, 0.3, 50, 20, 1000,
     "<div class='message__section-dosing-item message__section-dosing-label'><strong>General Dosing:</strong> <br> <div class='message__section-dosing-instructions'><span class='age-group'>1 month - 18 years</span> 15 - 30mg/kg (maximum 1,000mg) three times daily </div> <strong>Strep A Dosing:</strong> <div class='message__section-dosing-instructions'><span class='age-group'>Under 15kg</span> 50mg/kg once daily for 10 days<br> <span class='age-group'> 15 - 29.9kg</span> 750mg once daily for 10 days<br><span class='age-group'> 30kg or over</span> 1,000mg once daily for 10 days</div></div>",
     "https://nzfchildren.org.nz/nzf_3025", True, 2, 40, 1000, True, "once daily for 10 days", 30, 50, 40, 1000),
    ('Lactulose', 3, False, 0.5, 0.334, "twice daily (adjusted according to response)", 20, 20, False, None, None, None, None,
    "<div class='message__section-dosing-item message__section-dosing-label'><strong>General Dosing:</strong> <br> <div class='message__section-dosing-instructions'><span class='age-group'>1 month - 1 year</span> 2.5 mL twice daily, adjusted according to response<br><span class='age-group'>1 - 5 years</span> 2.5-10 mL twice daily, adjusted according to response<br><span class='age-group'>5 - 18 years</span> 5-20 mL twice daily, adjusted according to response <br> <span class='age-group'> Note</span> This calculator uses the UpToDate dosing of 0.5 mL/kg</div></div>",
    "https://nzfchildren.org.nz/nzf_895", False, None, None, None, False, "", None, None, None, None)

 ]
# Выполняем вставку

        cursor.executemany('''INSERT INTO drugs
    (name, category_id, tablet_only, mls_var, mgs_var, number_of_times_a_day,
     mls_max, mgs_max, loading_dose, mls_var_loading, mgs_var_loading,
     mls_max_loading, mgs_max_loading, instructions, nzf_link,
     high_range, high_modifier, mls_max_high, mgs_max_high,
     strep_drug, strep_frequency, mls_var_strep, mgs_var_strep,
     mls_strep_max, mgs_strep_max)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', drugs_data)

        products = [
            ('HP Pavilion Laptop', 'Electronics', 10.99, 10),
            ('Samsung Galaxy Smartphone', 'Electronics', 15.99, None),
            ('Adidas T-shirt', 'Clothing', 8.99, 2.50),
            ('Levis Jeans', 'Clothing', 12.99, 15)
            ]
        cursor.executemany("INSERT INTO products (name, category, price, discount) VALUES (?, ?, ?, ?)", products)

        conn.commit()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        # Закрываем соединение
        conn.close()




# Подключение к базе данных
def get_db_connection():
    conn = sqlite3.connect('myapp.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Устанавливаем row_factory для доступа по именам колонок
    cursor = conn.cursor()
    return cursor

# Генератор нового ID
def generate_id():
    return max(book['id'] for book in BOOKS) + 1 if BOOKS else 1

# Удаление книги по ID
def remove_book(book_id):
    global BOOKS
    BOOKS = [book for book in BOOKS if book['id'] != book_id]


# Регистрация нового пользователя
#@app.route('/api/register', methods=['POST'])
#def register_user():
 #   data = request.get_json()
  #  username = data.get('username')
   # password = data.get('password')
    #if not username or not password:
     #   return jsonify({'status': 'error', 'message': 'Username and password are required'}), 400
    #USERS.append({'username': username, 'password': password})
    #return jsonify({'status': 'success', 'message': 'User registered successfully'}), 201

@app.route('/api/register', methods=['POST'])
def register_user():
    conn = None
    conn = get_db_connection()
    cursor = conn.cursor()
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute("SELECT id FROM users WHERE username=?", (username,))
    if cursor.fetchone():
        return jsonify({'message': 'User already exists'}), 400
    ##ДОБАВИТЬ ПРОВЕРКУ ПО ПОЧТЕ НА УНИКАЛЬНОСТЬ

    cursor.execute("INSERT INTO users (username,email, password) VALUES (?, ?, ?)", (username, email, hashed_password))
    conn.commit()

    return jsonify({'message': 'User registered successfully'}), 201



# Вход пользователя
#@app.route('/api/login', methods=['POST'])
#def login_user():
 #   data = request.get_json()
  #  username = data.get('username')
   # password = data.get('password')
    #if not username or not password:
     #   return jsonify({'status': 'error', 'message': 'Username and password are required'}), 400
    #user = next((user for user in USERS if user['username'] == username and user['password'] == password), None)
    #if user:
     #   access_token = create_access_token(identity=username)  # Создание токена
      #  return jsonify({'status': 'success', 'access_token': access_token}), 200
    #else:
     #   return jsonify({'status': 'error', 'message': 'Invalid username or password'}), 401


@app.route('/api/login', methods=['POST'])
def login_user():
    conn = get_db_connection()
    cursor = conn.cursor()
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute("SELECT id FROM users WHERE username=? AND password=?", (username, hashed_password))
    user = cursor.fetchone()

    if not user:
        return jsonify({'message': 'Invalid credentials'}), 401

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token), 200

###Calculator
@app.route('/api/drugs', methods=['GET'])
def get_drugs():
    cursor = get_db_connection()
    try:
        # Выполняем SQL-запрос
        cursor.execute('''
            SELECT d.id, d.name, d.tablet_only, d.mls_var, d.instructions, dc.category_name
            FROM drugs d
            JOIN drugs_categories dc ON d.category_id = dc.category_id
            ORDER BY dc.category_name, d.name
        ''')
        drugs = cursor.fetchall()

        # Группируем препараты по категориям
        drugs_by_categories = {}
        for drug in drugs:
            category_name = drug['category_name']
            if category_name not in drugs_by_categories:
                drugs_by_categories[category_name] = []
            drugs_by_categories[category_name].append({
                'id': drug['id'],
                'name': drug['name'],
                'tablet_only': drug['tablet_only'],
                'mls_var': drug['mls_var'],
                'instructions': drug['instructions']
            })

        return jsonify(drugs_by_categories)
    except Exception as e:
        print(f"Database error: {e}")
        return jsonify({"error": "Failed to fetch drugs from the database."}), 500
    finally:
        cursor.connection.close()  # Закрываем соединение через курсор





@app.route('/api/books', methods=['GET'])
@jwt_required()
def user_books():
    conn = get_db_connection()
    cursor = conn.cursor()
    current_user = get_jwt_identity()  # Получаем идентификатор текущего пользователя из токена
    user_books = [book for book in BOOKS if book.get('username') == current_user]  # Фильтруем книги по текущему пользователю
    return jsonify({'status': 'success', 'books': user_books})

# Добавление новой книги
@app.route('/api/books', methods=['POST'])
@jwt_required()
def add_book():
    conn = get_db_connection()
    cursor = conn.cursor()
    current_user = get_jwt_identity()  # Получаем идентификатор текущего пользователя из токена
    data = request.get_json()
    new_book = {
        'id': generate_id(),
        'title': data.get('title'),
        'author': data.get('author'),
        'read': data.get('read'),
        'username': current_user  # Сохраняем имя текущего пользователя как владельца книги
    }
    BOOKS.append(new_book)
    return jsonify({'status': 'success', 'message': 'Book added!', 'book': new_book}), 201

# Получение, обновление или удаление конкретной книги по ее ID
@app.route('/api/books/<int:book_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def single_book(book_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    current_user = get_jwt_identity()  # Получаем имя текущего пользователя из токена
    book = next((book for book in BOOKS if book['id'] == book_id), None)
    if not book:
        return jsonify({'status': 'error', 'message': 'Book not found'}), 404

    # Проверяем, принадлежит ли книга текущему пользователю
    if book['username'] != current_user:
        return jsonify({'status': 'error', 'message': 'You do not have permission to access this book'}), 403

    if request.method == 'PUT':
        post_data = request.get_json()
        remove_book(book_id)
        updated_book = {
            'id': book_id,
            'title': post_data.get('title'),
            'author': post_data.get('author'),
            'read': post_data.get('read'),
            'username': current_user  # Сохраняем имя текущего пользователя как владельца книги
        }
        BOOKS.append(updated_book)
        return jsonify({'status': 'success', 'message': 'Book updated!', 'book': updated_book})
    elif request.method == 'DELETE':
        remove_book(book_id)
        return jsonify({'status': 'success', 'message': 'Book removed!'})
    else:
        return jsonify({'status': 'success', 'book': book})



# Запуск приложения
if __name__ == '__main__':
    # Инициализация базы данных
    initialize_database()

    # Настройка JWT
    app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Замените 'your-secret-key' на ваш секретный ключ
    jwt = JWTManager(app)
    # Настройка CORS
    CORS(app)
    app.run()
    # Список книг (заглушка для примера)
    BOOKS = []
    # Список пользователей (заглушка для примера)
    USERS = [
        {
            'username': 'test@test.ru',
            'password': 'test'
        }
    ]