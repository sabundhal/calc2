from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
import sqlite3
import hashlib

##BD
conn = sqlite3.connect('myapp.db', check_same_thread=False)
cursor = conn.cursor()


cursor.execute('''CREATE TABLE IF NOT EXISTS users
                  (id INTEGER PRIMARY KEY, username TEXT, email TEXT UNIQUE, password TEXT)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS products
                  (id INTEGER PRIMARY KEY, name TEXT, category TEXT, price REAL, discount REAL)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS carts
                  (id INTEGER PRIMARY KEY, user_id INTEGER, total_price REAL, total_discount REAL)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS cart_items
                  (id INTEGER PRIMARY KEY, cart_id INTEGER, product_id INTEGER, quantity INTEGER)''')


products = [
    ('HP Pavilion Laptop', 'Electronics', 10.99, 10),
    ('Samsung Galaxy Smartphone', 'Electronics', 15.99, None),
    ('Adidas T-shirt', 'Clothing', 8.99, 2.50),
    ('Levis Jeans', 'Clothing', 12.99, 15)
]
cursor.executemany("INSERT INTO products (name, category, price, discount) VALUES (?, ?, ?, ?)", products)

conn.commit()
##BD


app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Замените 'your-secret-key' на ваш секретный ключ
jwt = JWTManager(app)
CORS(app)

# Список книг
BOOKS = []
# Список пользователей (заглушка для примера)
USERS = [
    {
        'username': 'test@test.ru',
        'password': 'test'
    }
]
#yjdsq
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
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute("SELECT id FROM users WHERE username=?", (username,))
    if cursor.fetchone():
        return jsonify({'message': 'User already exists'}), 400
    ##ДОБАВИТЬ ПРОВЕРКУ ПО ПОЧТЕ НА УНИКАЛЬНОСТЬ

    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
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




@app.route('/api/books', methods=['GET'])
@jwt_required()
def user_books():
    current_user = get_jwt_identity()  # Получаем идентификатор текущего пользователя из токена
    user_books = [book for book in BOOKS if book.get('username') == current_user]  # Фильтруем книги по текущему пользователю
    return jsonify({'status': 'success', 'books': user_books})

# Добавление новой книги
@app.route('/api/books', methods=['POST'])
@jwt_required()
def add_book():
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

if __name__ == '__main__':
    app.run()
