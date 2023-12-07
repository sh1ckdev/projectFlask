from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, current_user, login_required, logout_user, LoginManager
from app import app
from app.models import get_database_connection, User, Product, UserPurchases, Reviews
from app.password_hash import hash_password, check_password

login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    user = User.get(user_id)
    return user

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/concerts')
def concerts():
    return render_template('concerts.html')

@app.route('/gallery')
def gallery():
    reviews = Reviews.get_reviews()
    print(reviews)
    return render_template('gallery.html', reviews=reviews)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        new_username = request.form['newUsername']
        new_password = request.form['newPassword']

        try:
            existing_user = User.get_by_username(new_username)

            if existing_user:
                return render_template('reg.html', message='Вы уже зарегистрированы')

            hashed_password = hash_password(new_password)
            new_user = User.create(username=new_username, password=hashed_password)
            user = User.get_by_credentials(new_username, hashed_password)

            login_user(user)
            return redirect(url_for('personal_page'))
        except Exception as e:
            return render_template('reg.html', message=f'Ошибка регистрации: {str(e)}')

    return render_template('reg.html')



@app.route('/admin')
@login_required
def admin_panel():
    if current_user.is_authenticated and current_user.is_admin:
        db, cursor = get_database_connection()
        query = "SELECT id, username, password FROM users"
        cursor.execute(query)
        data = cursor.fetchall()
        columns = [i[0] for i in cursor.description]
        db.close()
        return render_template('admin_panel.html', data=data, columns=columns)
    else:
        return redirect(url_for('personal_page'))
    
@app.route('/load_products', methods=['POST'])
@login_required
def load_products():
    if current_user.is_authenticated and current_user.is_admin:
        db, cursor = get_database_connection()
        product_query = "SELECT id, name, description, price FROM products"
        cursor.execute(product_query)
        products_data = cursor.fetchall()
        product_columns = [i[0] for i in cursor.description]
        db.close()
        return render_template('admin_panel.html', data=products_data, columns=product_columns, show_products=True)
    else:
        return redirect(url_for('personal_page'))

@app.route('/load_users', methods=['POST'])
@login_required
def load_users():
    if current_user.is_authenticated and current_user.is_admin:
        db, cursor = get_database_connection()
        user_query = "SELECT id, username, password FROM users"
        cursor.execute(user_query)
        users_data = cursor.fetchall()
        user_columns = [i[0] for i in cursor.description]
        db.close()
        return render_template('admin_panel.html', data=users_data, columns=user_columns, show_users=True)
    else:
        return redirect(url_for('personal_page'))

@app.route('/load_reviews', methods=['POST'])
@login_required
def load_reviews():
    if current_user.is_authenticated and current_user.is_admin:
        db, cursor = get_database_connection()
        reviews_query = "SELECT id, user_id, review FROM reviews"
        cursor.execute(reviews_query)
        reviews_data = cursor.fetchall()
        reviews_columns = [i[0] for i in cursor.description]
        db.close()
        return render_template('admin_panel.html', data=reviews_data, columns=reviews_columns, show_reviews=True)
    else:
        return redirect(url_for('personal_page'))


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def personal_page():
    if current_user.is_authenticated:
        if request.method == 'POST':
            reviews_description = request.form['reviews_description']
            Reviews.add_review(current_user.id, reviews_description)

        user_purchases = UserPurchases.get_user_purchases(current_user.id)
        products_in_cart = []
        for purchase in user_purchases:
            product_id = purchase[2]
            product = Product.get_product_by_id(product_id)
            if product:
                products_in_cart.append(product)

        return render_template('profile.html', username=current_user.username, cart=products_in_cart)
    else:
        return render_template('profile.html', username='Гость')




@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('authorize'))


@app.route('/login', methods=['GET', 'POST'])
def authorize():
    if current_user.is_authenticated:
        return redirect(url_for('personal_page'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.get_by_username(username)

        if user and check_password(user.password, password):
            if user.is_admin:
                login_user(user)
                return redirect(url_for('admin_panel'))
            else:
                login_user(user)
                next_url = request.args.get('next')
                return redirect(next_url or url_for('personal_page'))
        else:
            return render_template('auth.html', message='Такого пользователя не существует')

    return render_template('auth.html')


@app.route('/products')
def products():
    all_products = Product.get_all_products()
    return render_template('products.html', products=all_products)


@app.route('/add_product', methods=['POST'])
@login_required
def add_product():
    if current_user.is_authenticated and current_user.is_admin:
        if request.method == 'POST':
            product_name = request.form['product_name']
            product_description = request.form['product_description']
            product_price = request.form['product_price']

            db, cursor = get_database_connection()
            insert_query = "INSERT INTO products (name, description, price) VALUES (%s, %s, %s)"
            cursor.execute(insert_query, (product_name, product_description, product_price))
            db.commit()
            db.close()

        return redirect(url_for('admin_panel'))
    else:
        return redirect(url_for('personal_page'))
    

@app.route('/delete_product', methods=['POST'])
@login_required
def delete_product():
    if current_user.is_authenticated and current_user.is_admin:
        if request.method == 'POST':
            product_name = request.form['delete_product_name']

            db, cursor = get_database_connection()
            delete_user_purchases_query = "DELETE FROM user_purchases WHERE product_id = (SELECT id FROM products WHERE name = %s)"
            cursor.execute(delete_user_purchases_query, (product_name,))
            delete_product_query = "DELETE FROM products WHERE name = %s"
            cursor.execute(delete_product_query, (product_name,))

            db.commit()
            db.close()

        return redirect(url_for('admin_panel'))
    else:
        return redirect(url_for('personal_page'))




@app.route('/delete_service/<int:product_id>', methods=['GET','POST'])
@login_required
def delete_service(product_id):
    if current_user.is_authenticated:
        UserPurchases.delete_service_from_cart(current_user.id, product_id)
        return redirect(url_for('personal_page'))
    else:
        return redirect(url_for('authorize'))


    
@app.route('/buy_product/<int:product_id>')
def buy_product(product_id):
    if current_user.is_authenticated:
        print(f"User {current_user.username} is buying product {product_id}")

        if current_user.is_authenticated:
            UserPurchases.add_purchase(current_user.id, product_id)


        return redirect(url_for('products'))
    else:  
        redirect(url_for('authorize'))

@app.route('/add_review', methods=['POST'])
@login_required
def add_review():
    if request.method == 'POST':
        reviews_description = request.form['reviews_description']
        Reviews.add_review(current_user.id, reviews_description)

        return redirect(url_for('gallery'))
    else: 
        return redirect(url_for('gallery'))

@app.route('/delete_reviews', methods=['POST'])
@login_required
def delete_reviews():
    if current_user.is_authenticated and current_user.is_admin:
        if request.method == 'POST':
            reviews_id = request.form['delete_reviews_id']

            db, cursor = get_database_connection()
            delete_reviews_query = "DELETE FROM reviews WHERE id = %s"
            cursor.execute(delete_reviews_query, (reviews_id,))

            db.commit()
            db.close()

        return redirect(url_for('admin_panel'))
    else:
        return redirect(url_for('personal_page'))