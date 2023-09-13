from flask import Flask, request, jsonify
import pyodbc
import re

app = Flask(__name__)

try:
    conn = pyodbc.connect(
        'Driver={SQL Server};Server=DESKTOP-JF79DLE\MSSQLSERVER01;Database=AplicatieLicenta;Trusted_Connection=yes;')
    cursor = conn.cursor()
except pyodbc.Error as e:
    print("Database connection error:", str(e))

books = None


def validate_credentials(username, password):
    try:
        # Check if the username and password match the values in the database
        cursor.execute('SELECT COUNT(*) FROM users WHERE username = ? AND password = ?', (username, password))
        if cursor.fetchone()[0] > 0:
            return True
        else:
            return False
    except pyodbc.Error as e:
        print("Database query error:", str(e))
        return False


def fetch_books():
    global books
    cursor.execute("SELECT name, price, link FROM books")
    rows = cursor.fetchall()

    books = []
    for row in rows:
        book = {
            'name': row.name,
            'price': row.price,
            'link': row.link
        }
        books.append(book)


def email_validation(email):
    # Regular expression pattern for email validation
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'

    # Use the regular expression pattern to match the email address
    match = re.match(pattern, email)

    if match:
        return True
    else:
        return False


@app.route('/')
def index():
    return 'Bună'


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'message': 'All fields are required'}), 400

    if len(username) < 3 or len(username) > 20:
        return jsonify({'message': 'Username must be between 3 and 20 characters'}), 400

    if len(password) < 6 or len(password) > 20:
        return jsonify({'message': 'Password must be between 6 and 20 characters'}), 400

    if not email_validation(email):
        return jsonify({'message': 'Invalid email address'}), 400

    cursor.execute('SELECT COUNT(*) FROM users WHERE email = ?', (email,))
    if cursor.fetchone()[0] > 0:
        return jsonify({'message': 'Email is already registered'}), 409

    cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', (username, email, password))
    conn.commit()

    return jsonify({'message': 'Registration successful'}), 201


@app.route('/login', methods=['POST'])
def login():
    try:
        username = request.json.get('username')
        password = request.json.get('password')

        if validate_credentials(username, password):
            response = {'message': 'Autentificare reușită'}
            return jsonify(response), 200
        else:
            response = {'message': 'Credențiale invalide'}
            return jsonify(response), 401
    except Exception as e:
        print("Error during login:", str(e))
        response = {'message': 'Internal server error'}
        return jsonify(response), 500


@app.route('/search/<query>', methods=['GET'])
def search(query):
    try:
        # Define default values for page and pageSize
        page = request.args.get('page', default=1, type=int)
        page_size = request.args.get('pageSize', default=10, type=int)

        # Perform string matching search logic using the name of the book parameter
        # Retrieve the total count of results
        count_query = f"SELECT COUNT(*) FROM books WHERE name LIKE '%{query}%'"
        cursor.execute(count_query)
        total_count = cursor.fetchone()[0]

        # Calculate the total pages based on the total count and page size
        total_pages = (total_count + page_size - 1) // page_size

        # Adjust the SQL query to include pagination
        sql_query = f"SELECT bookid, name, price, link FROM books WHERE name LIKE '%{query}%' ORDER BY bookid OFFSET {page_size * (page - 1)} ROWS FETCH NEXT {page_size} ROWS ONLY"

        cursor.execute(sql_query)
        results = cursor.fetchall()

        # Process the search results and create a response
        response_data = {
            'total_pages': total_pages,
            'results': [{'bookid': row.bookid, 'name': row.name, 'price': row.price, 'link': row.link} for row in results]
        }

        if results:
            return jsonify(response_data), 200
        else:
            response = {'message': 'No results found'}
            return jsonify(response), 404
    except pyodbc.Error as e:
        print("Database query error:", str(e))
        response = {'message': 'Internal server error'}
        return jsonify(response), 500
    except Exception as e:
        print("Error during search:", str(e))
        response = {'message': 'Internal server error'}
        return jsonify(response), 500



@app.route('/books', methods=['GET'])
def get_books():
    global books
    if not books:
        fetch_books()

    return jsonify(books)


if __name__ == '__main__':
    app.run(debug=True)
