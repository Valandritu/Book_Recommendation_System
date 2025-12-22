from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
import os
import random
import requests
import math
import MySQLdb  # used for catching IntegrityError

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong secret key
bcrypt = Bcrypt(app)

# -----------------------------
# MYSQL CONFIGURATION
# -----------------------------
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'book_system'

mysql = MySQL(app)

# -----------------------------
# FILE UPLOAD CONFIGURATION
# -----------------------------
UPLOAD_FOLDER = 'static/uploads/books'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ===================================================
# HOME PAGE (User)
# ===================================================
@app.route('/', methods=['GET'])
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    try:
        api_url = "https://www.googleapis.com/books/v1/volumes?q=bestseller&maxResults=20"
        response = requests.get(api_url, timeout=5)
        data = response.json()
        suggestions = []

        if "items" in data:
            for item in data["items"]:
                volume = item.get("volumeInfo", {})
                suggestions.append({
                    "id": item.get("id"),
                    "title": volume.get("title", "N/A"),
                    "author": ", ".join(volume.get("authors", ["Unknown"])),
                    "image": volume.get("imageLinks", {}).get("thumbnail", ""),
                    "link": volume.get("infoLink", "#")
                })

        if len(suggestions) > 10:
            suggestions = random.sample(suggestions, 10)

        return render_template("index.html", books=None, suggestions=suggestions, search=None, message=None)
    except Exception as e:
        print(f"Error loading suggestions from API: {e}")
        # Fallback: show books from database if API fails
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT id, title, author FROM books LIMIT 10")
            db_books = cur.fetchall()
            cur.close()
            
            # Convert database tuples to dictionaries for template
            suggestions = []
            for book in db_books:
                suggestions.append({
                    "id": book[0],
                    "title": book[1],
                    "author": book[2],
                    "image": "",
                    "link": "#"
                })
            
            if suggestions:
                return render_template("index.html", books=None, suggestions=suggestions, search=None, message=None)
        except Exception as db_error:
            print(f"Database fallback error: {db_error}")
        
        return render_template("index.html", books=None, suggestions=None, search=None, message="Error loading suggestions")


# =================================================
# SEARCH + PAGINATION
# ===================================================
@app.route('/recommend', methods=['GET', 'POST'])
def recommend():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        query = request.form['query']
        session['last_search'] = query
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO search_history (user_id, query) VALUES (%s, %s)", (session['user_id'], query))
        mysql.connection.commit()
        cur.close()
    else:
        query = session.get('last_search')
        if not query:
            return redirect(url_for('home'))

    page = int(request.args.get("page", 1))
    results_per_page = 5

    # Fetch matching local/admin-uploaded books first (limit to current page size)
    books = []
    try:
        # fetch API results
        api_url = f"https://www.googleapis.com/books/v1/volumes?q={query}&startIndex={(page - 1) * results_per_page}&maxResults={results_per_page}"
        response = requests.get(api_url)
        data = response.json()
        total_items = data.get("totalItems", 0)
        total_pages = math.ceil(total_items / results_per_page) if results_per_page else 0

        if "items" in data:
            for item in data["items"]:
                volume = item.get("volumeInfo", {})
                books.append({
                    "id": item.get("id"),
                    "title": volume.get("title", "N/A"),
                    "author": ", ".join(volume.get("authors", ["Unknown"])),
                    "image": volume.get("imageLinks", {}).get("thumbnail", ""),
                    "link": volume.get("infoLink", "#")
                })

        if books:
            return render_template("index.html", books=books, search=query, page=page, total_pages=total_pages,
                                   suggestions=None, message=None)
        return render_template("index.html", books=None, search=query, suggestions=None, message="No books found")
    except Exception as e:
        print(f"Error fetching API books: {e}")
        return render_template("index.html", books=None, search=query, suggestions=None, message="Error fetching results")


# ===================================================
# ADMIN FORGOT PASSWORD
# ===================================================
@app.route('/admin/forgot-password', methods=['GET', 'POST'])
def admin_forgot_password():
    if request.method == 'POST':
        username = request.form['username']
        new_password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM admin WHERE username = %s", (username,))
        admin = cur.fetchone()

        if admin:
            hashed_pw = bcrypt.generate_password_hash(new_password).decode('utf-8')
            cur.execute("UPDATE admin SET password = %s WHERE username = %s",
                        (hashed_pw, username))
            mysql.connection.commit()
            cur.close()
            flash('Password reset successful. Please login.', 'success')
            return redirect(url_for('admin_login'))
        else:
            cur.close()
            flash('Admin not found', 'danger')

    return render_template('admin_forgot_password.html')


# ===================================================
# USER REGISTER
# ===================================================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, password))
        mysql.connection.commit()
        cur.close()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


# ===================================================
# USER LOGIN
# ===================================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        # Server-side validation for empty fields
        if not email or not password:
            flash('Email and password are required.', 'danger')
            return render_template('login.html')
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        
        if not user:
            flash('Email not found.', 'danger')
        elif not bcrypt.check_password_hash(user[3], password):
            flash('Incorrect password.', 'danger')
        else:
            # Successful login
            session['logged_in'] = True
            session['user_id'] = user[0]
            session['username'] = user[1]
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
    
    return render_template('login.html')


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        new_password = request.form['new_password']
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        
        if user:
            hashed_pw = bcrypt.generate_password_hash(new_password).decode('utf-8')
            cur.execute("UPDATE users SET password = %s WHERE email = %s", (hashed_pw, email))
            mysql.connection.commit()
            cur.close()
            flash('Password reset successful. Please login.', 'success')
            return redirect(url_for('login'))
        else:
            cur.close()
            flash('Email not found', 'danger')
    
    return render_template('forgot_password.html')
# ===================================================
# USER LOGOUT
# ===================================================
@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))

# ===================================================
# BOOK DETAILS
# ===================================================
@app.route('/book/<book_id>')
def book_details(book_id):
    reviews = []
    # support local admin-uploaded books which use ids like 'local-<db_id>'
    if str(book_id).startswith('local-'):
        try:
            local_id = int(str(book_id).split('-', 1)[1])
            cur = mysql.connection.cursor()
            cur.execute("SELECT id, title, author, category, year, pdf_file")
            row = cur.fetchone()
            cur.close()

            if not row:
                return "Book not found."

            _, title, author, category, year, pdf_file = row

            preview_link = None
            if pdf_file:
                try:
                    preview_link = url_for('static', filename=f'uploads/books/{pdf_file}')
                except Exception:
                    preview_link = f"/static/uploads/books/{pdf_file}"


            book = {
                "id": book_id,
                "title": title,
                "author": author,
                "description": f"Category: {category}" if category else "No description available.",
                "publisher": "Admin Upload",
                "publishedDate": year or "N/A",
                "pageCount": "N/A",
                "categories": category or "N/A",
                "preview": preview_link or "#"
            }

            # Fetch approved reviews for this local book (reviews stored with same local id)
            try:
                cur = mysql.connection.cursor()
                cur.execute("""SELECT r.id, u.username, r.review, r.rating
                               FROM reviews r
                               JOIN users u ON r.user_id = u.id
                               WHERE r.book_id = %s AND r.approved = 1
                               ORDER BY r.id DESC""", (book_id,))
                reviews = cur.fetchall()
                cur.close()
            except Exception as e:
                print(f"Error fetching reviews for local book: {e}")

            return render_template("book_details.html", book=book, reviews=reviews)
        except Exception as e:
            print(f"Error loading local book details: {e}")
            return "Error loading book details."

    # fallback: treat as Google Books id
    api_url = f"https://www.googleapis.com/books/v1/volumes/{book_id}"
    try:
        response = requests.get(api_url)
        data = response.json()
        volume = data.get("volumeInfo", {})
        book = {
            "id": data.get("id"),
            "title": volume.get("title", "N/A"),
            "author": ", ".join(volume.get("authors", ["Unknown"])),
            "image": volume.get("imageLinks", {}).get("thumbnail", ""),
            "description": volume.get("description", "No description available."),
            "publisher": volume.get("publisher", "Unknown"),
            "publishedDate": volume.get("publishedDate", "N/A"),
            "pageCount": volume.get("pageCount", "N/A"),
            "categories": ", ".join(volume.get("categories", ["N/A"])),
            "preview": volume.get("previewLink", "#")
        }

        # Fetch approved reviews for this book
        try:
            cur = mysql.connection.cursor()
            cur.execute("""SELECT r.id, u.username, r.review, r.rating 
                           FROM reviews r 
                           JOIN users u ON r.user_id = u.id 
                           WHERE r.book_id = %s AND r.approved = 1
                           ORDER BY r.id DESC""", (book_id,))
            reviews = cur.fetchall()
            cur.close()
        except Exception as e:
            print(f"Error fetching reviews: {e}")
        
        return render_template("book_details.html", book=book, reviews=reviews)
    except Exception as e:
        print(f"Error loading Google book details: {e}")
        return "Error loading book details."

# ===================================================
# ADD TO FAVORITES
# ===================================================
@app.route('/favorite/<book_id>/<title>/<author>/<path:image>')
def add_favorite(book_id, title, author, image):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO favorites (user_id, book_id, title, author, image) VALUES (%s, %s, %s, %s, %s)",
                (session['user_id'], book_id, title, author, image))
    mysql.connection.commit()
    cur.close()
    flash("Book added to favorites!", "success")
    return redirect(url_for('favorites'))

# ===================================================
# VIEW FAVORITES
# ===================================================
@app.route('/favorites')
def favorites():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM favorites WHERE user_id = %s", (session['user_id'],))
    favs = cur.fetchall()
    cur.close()
    return render_template("favorites.html", favorites=favs)

# ===================================================
# DELETE FAVORITE
# ===================================================
@app.route('/delete-favorite/<int:fav_id>')
def delete_favorite(fav_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM favorites WHERE id = %s AND user_id = %s", (fav_id, session['user_id']))
    mysql.connection.commit()
    cur.close()
    flash("Favorite deleted!", "success")
    return redirect(url_for('favorites'))

# ===================================================
# SEARCH HISTORY
# ===================================================
@app.route('/history')
def history():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT id, query, timestamp FROM search_history WHERE user_id = %s ORDER BY timestamp DESC", (session['user_id'],))
    history = cur.fetchall()
    cur.close()
    return render_template("history.html", history=history)


@app.route('/delete_history/<int:history_id>', methods=['POST'])
def delete_history(history_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    # Verify the history entry belongs to the current user
    cur.execute("SELECT user_id FROM search_history WHERE id = %s", (history_id,))
    result = cur.fetchone()
    
    if result and result[0] == session['user_id']:
        cur.execute("DELETE FROM search_history WHERE id = %s", (history_id,))
        mysql.connection.commit()
    
    cur.close()
    return redirect(url_for('history'))



# ===================================================
# ADMIN LOGIN
# ===================================================
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        # Server-side validation for empty fields
        if not username or not password:
            flash('Username and password are required.', 'danger')
            return render_template('admin_login.html')
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM admin WHERE username=%s", (username,))
        admin = cur.fetchone()
        cur.close()
        
        if not admin:
            flash('Username not found.', 'danger')
        elif not bcrypt.check_password_hash(admin[2], password):
            flash('Incorrect password.', 'danger')
        else:
            # Successful login
            session['admin_logged_in'] = True
            session['admin_username'] = admin[1]
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
    
    return render_template('admin_login.html')

# ===================================================
# ADMIN LOGOUT
# ===================================================
@app.route('/admin/logout')
def admin_logout():
    session.clear()
    flash('Admin logged out successfully', 'success')
    return redirect(url_for('admin_login'))

# ===================================================
# ADMIN DASHBOARD
# ===================================================
@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM books")
    total_books = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM reviews")
    total_reviews = cur.fetchone()[0]
    cur.close()

    return render_template('admin_dashboard.html',
                           total_users=total_users,
                           total_books=total_books,
                           total_reviews=total_reviews)

# ===================================================
# ADMIN BOOK MANAGEMENT
# ===================================================
@app.route('/admin/manage_books')
def manage_books():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT id, title, author, category, year, pdf_file FROM books")
    books = cur.fetchall()
    cur.close()
    return render_template('manage_books.html', books=books)

@app.route('/admin/add-book', methods=['GET', 'POST'])
def add_book():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        category = request.form.get('category', '').strip()
        year = request.form.get('year', '').strip()
        pdf_file = request.files.get('pdf_file')

        filename = None
        if pdf_file and allowed_file(pdf_file.filename):
            filename = f"{random.randint(1000,9999)}_{pdf_file.filename}"
            pdf_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO books(title, author, category, year, pdf_file) VALUES(%s,%s,%s,%s,%s)",
                    (title, author, category, year, filename))
        mysql.connection.commit()
        cur.close()
        flash('Book added successfully!', 'success')
        return redirect(url_for('manage_books'))

    return render_template('add_book.html')

@app.route('/admin/edit-book/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    cur = mysql.connection.cursor()
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        category = request.form.get('category', '').strip()
        year = request.form.get('year', '').strip()
        pdf_file = request.files.get('pdf_file')

        if pdf_file and allowed_file(pdf_file.filename):
            filename = f"{random.randint(1000,9999)}_{pdf_file.filename}"
            pdf_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            cur.execute("UPDATE books SET title=%s, author=%s, category=%s, year=%s, pdf_file=%s WHERE id=%s",
                        (title, author, category, year, filename, book_id))
        elif pdf_file and allowed_file(pdf_file.filename):
            filename = f"{random.randint(1000,9999)}_{pdf_file.filename}"
            pdf_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            cur.execute("UPDATE books SET title=%s, author=%s, category=%s, year=%s, pdf_file=%s WHERE id=%s",
                        (title, author, category, year, filename, book_id))
        else:
            cur.execute("UPDATE books SET title=%s, author=%s, category=%s, year=%s WHERE id=%s",
                        (title, author, category, year, book_id))

        mysql.connection.commit()
        cur.close()
        flash('Book updated successfully!', 'success')
        return redirect(url_for('manage_books'))

    cur.execute("SELECT * FROM books WHERE id=%s", (book_id,))
    book = cur.fetchone()
    cur.close()
    return render_template('edit_book.html', book=book)

@app.route('/admin/delete-book/<int:book_id>')
def delete_book(book_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM books WHERE id=%s", (book_id,))
    mysql.connection.commit()
    cur.close()
    flash('Book deleted successfully', 'success')
    return redirect(url_for('manage_books'))

# ===================================================
# ADMIN USER MANAGEMENT
# ===================================================
@app.route('/admin/manage_users')
def manage_users():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT id, username, email FROM users")
    users = cur.fetchall()
    cur.close()
    return render_template('manage_users.html', users=users)

@app.route('/admin/add_user', methods=['GET', 'POST'])
def add_user():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if not username or not email or not password:
            flash("All fields are required.", "warning")
            return redirect(url_for('add_user'))

        # Hash the password before storing
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')

        conn = mysql.connection
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO users (username, email, password)
            VALUES (%s, %s, %s)
        """, (username, email, hashed_pw))

        conn.commit()
        cursor.close()

        flash("User added successfully!", "success")
        return redirect(url_for('manage_users'))

    return render_template('add_user.html')

@app.route('/admin/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    conn = mysql.connection
    cursor = conn.cursor()

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']

        cursor.execute("""
            UPDATE users 
            SET username = %s, email = %s 
            WHERE id = %s
        """, (username, email, user_id))

        conn.commit()
        cursor.close()
        flash('User updated successfully.', 'success')
        return redirect(url_for('manage_users'))

    # Fetch user details for editing
    cursor.execute("SELECT id, username, email FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()

    if not user:
        flash('User not found.', 'warning')
        return redirect(url_for('manage_users'))

    return render_template("edit_user.html", user=user)


@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    conn = mysql.connection
    cursor = conn.cursor()

    try:
        # Attempt to delete child rows that reference the user first.
        # Here we delete from favorites (the error you showed referenced this table).
        # If you have other child tables (e.g. reviews, orders, etc.) that reference users,
        # delete from them as well BEFORE deleting from users.
        cursor.execute("DELETE FROM favorites WHERE user_id = %s", (user_id,))
        # Example: cursor.execute("DELETE FROM reviews WHERE user_id = %s", (user_id,))

        # Now delete parent user row
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        flash('User and related data deleted successfully.', 'success')
    except MySQLdb.IntegrityError as ie:
        # Still couldn't delete — foreign key constraint remains (maybe another child table).
        conn.rollback()
        flash(f'Integrity error while deleting user: {ie}', 'danger')
    except Exception as e:
        conn.rollback()
        flash(f'Error deleting user: {e}', 'danger')
    finally:
        cursor.close()

    return redirect(url_for('manage_users'))

# ===================================================
# USER REVIEW FUNCTIONALITY
# ===================================================
@app.route('/add_review/<book_id>', methods=['POST'])
def add_review(book_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    rating = request.form.get('rating')
    review_text = request.form.get('review')
    user_id = session.get('user_id')
    
    if not rating or not review_text:
        flash('Rating and review text are required', 'warning')
        return redirect(url_for('book_details', book_id=book_id))
    
    try:
        # Fetch book title from Google Books API
        book_title = "Unknown Book"
        try:
            api_url = f"https://www.googleapis.com/books/v1/volumes/{book_id}"
            response = requests.get(api_url, timeout=5)
            data = response.json()
            volume = data.get("volumeInfo", {})
            book_title = volume.get("title", "Unknown Book")
        except:
            book_title = "Unknown Book"
        
        cur = mysql.connection.cursor()
        # Insert review with book title
        cur.execute("""INSERT INTO reviews (user_id, book_id, review, rating, approved) 
                       VALUES (%s, %s, %s, %s, 0)""",
                    (user_id, book_id, review_text, rating))
        mysql.connection.commit()
        cur.close()
        flash('Review submitted successfully! Awaiting admin approval.', 'success')
    except Exception as e:
        print(f"Error adding review: {e}")
        flash('Error submitting review', 'danger')
    
    return redirect(url_for('book_details', book_id=book_id))

# ===================================================
# ADMIN REVIEWS MANAGEMENT
# ===================================================
@app.route('/admin/manage_reviews')
def manage_reviews():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    cur = mysql.connection.cursor()
    cur.execute("""SELECT r.id, u.username, r.book_id, r.review, r.rating, r.approved 
                   FROM reviews r 
                   LEFT JOIN users u ON r.user_id = u.id 
                   ORDER BY r.id DESC""")
    reviews_data = cur.fetchall()
    cur.close()
    
    # Fetch book titles from Google Books API
    reviews = []
    for review in reviews_data:
        review_id, username, book_id, review_text, rating, approved = review
        book_title = "Unknown Book"
        try:
            api_url = f"https://www.googleapis.com/books/v1/volumes/{book_id}"
            response = requests.get(api_url, timeout=5)
            data = response.json()
            volume = data.get("volumeInfo", {})
            book_title = volume.get("title", "Unknown Book")
        except:
            book_title = "Unknown Book"
        
        reviews.append((review_id, username, book_title, review_text, rating, approved))
    
    return render_template('manage_reviews.html', reviews=reviews)

@app.route('/admin/approve_review/<int:review_id>')
def approve_review(review_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    try:
        cur = mysql.connection.cursor()
        cur.execute("UPDATE reviews SET approved = 1 WHERE id = %s", (review_id,))
        mysql.connection.commit()
        cur.close()
        flash('Review approved successfully!', 'success')
    except Exception as e:
        print(f"Error approving review: {e}")
        flash('Error approving review', 'danger')
    
    return redirect(url_for('manage_reviews'))

@app.route('/admin/delete_review/<int:review_id>')
def delete_review(review_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM reviews WHERE id = %s", (review_id,))
        mysql.connection.commit()
        cur.close()
        flash('Review deleted successfully!', 'success')
    except Exception as e:
        print(f"Error deleting review: {e}")
        flash('Error deleting review', 'danger')
    
    return redirect(url_for('manage_reviews'))

# ===================================================
# ADMIN ANALYTICS
# ===================================================
@app.route('/admin/analytics')
def admin_analytics():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    cur = mysql.connection.cursor()
    
    # Get total counts
    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM books")
    total_books = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM reviews")
    total_reviews = cur.fetchone()[0]
    
    # Get category distribution
    cur.execute("SELECT category, COUNT(*) FROM books GROUP BY category")
    analytics = cur.fetchall()
    
    # Get top reviewed books - fetch books from reviews table directly
    cur.execute("""SELECT book_id, COUNT(*) as review_count 
                   FROM reviews 
                   GROUP BY book_id 
                   ORDER BY review_count DESC LIMIT 5""")
    books_review_data = cur.fetchall()
    
    # Fetch book titles from Google Books API for each reviewed book
    top_books = []
    for book_id, review_count in books_review_data:
        book_title = "Unknown Book"
        try:
            api_url = f"https://www.googleapis.com/books/v1/volumes/{book_id}"
            response = requests.get(api_url, timeout=5)
            data = response.json()
            volume = data.get("volumeInfo", {})
            book_title = volume.get("title", "Unknown Book")
        except:
            book_title = "Unknown Book"
        top_books.append((book_title, review_count))
    
    # Get recent users
    cur.execute("SELECT username, created_at FROM users ORDER BY id DESC LIMIT 5")
    recent_users_data = cur.fetchall()
    recent_users = [(user[0], user[1] if len(user) > 1 and user[1] else "N/A") for user in recent_users_data]
    
    # Get reviews per day (last 7 days)
    cur.execute("""SELECT DATE(timestamp) as date, COUNT(*) as count 
                   FROM reviews 
                   WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                   GROUP BY DATE(timestamp) 
                   ORDER BY date ASC""")
    review_data = cur.fetchall()
    review_dates = [str(row[0]) for row in review_data] if review_data else ['No data']
    review_counts = [row[1] for row in review_data] if review_data else [0]
    
    cur.close()
    
    return render_template('admin_analytics.html', 
                         total_users=total_users,
                         total_books=total_books,
                         total_reviews=total_reviews,
                         analytics=analytics,
                         top_books=top_books,
                         recent_users=recent_users,
                         review_dates=review_dates,
                         review_counts=review_counts)

# ===================================================
# MAIN
# ===================================================
if __name__ == "__main__":
    app.run(debug=True)
