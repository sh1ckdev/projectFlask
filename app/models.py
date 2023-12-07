import mysql.connector
from flask_login import UserMixin

def get_database_connection():
    db_config = {
        'host': '127.0.0.1',
        'user': 'root',
        'password': 'admin',
        'database': 'kursach'
    }
    db = mysql.connector.connect(**db_config)
    cursor = db.cursor()
    return db, cursor

class User(UserMixin):
    def __init__(self, id, username, password, is_admin=False):
        self.id = id
        self.username = username
        self.password = password
        self.is_admin = is_admin

    @staticmethod
    def get(user_id):
        db, cursor = get_database_connection()
        query = "SELECT * FROM users WHERE id = %s"
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        db.close()

        if result:
            user = User(id=result[0], username=result[1], password=result[2])
            user.is_admin = result[3] == 1
            return user
        return None

    @staticmethod
    def get_by_credentials(username, password):
        db, cursor = get_database_connection()
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        result = cursor.fetchone()
        db.close()

        if result:
            return User(id=result[0], username=result[1], password=result[2], is_admin=result[3])
        return None

    @staticmethod
    def get_by_username(username):
        db, cursor = get_database_connection()
        query = "SELECT * FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        result = cursor.fetchone()
        db.close()

        if result:
            return User(id=result[0], username=result[1], password=result[2], is_admin=result[3])
        return None

    @staticmethod
    def create(username, password, is_admin=False):
        db, cursor = get_database_connection()
        insert_query = "INSERT INTO users (username, password, is_admin) VALUES (%s, %s, %s)"
        cursor.execute(insert_query, (username, password, is_admin))
        db.commit()
        db.close()

class Product:
    def __init__(self, id, name, description, price):
        self.id = id
        self.name = name
        self.description = description
        self.price = price

    @staticmethod
    def get_all_products():
        db, cursor = get_database_connection()
        query = "SELECT * FROM products"
        cursor.execute(query)
        results = cursor.fetchall()
        db.close()

        products = []
        for result in results:
            product = Product(id=result[0], name=result[1], description=result[2], price=result[3])
            products.append(product)

        return products

    @staticmethod
    def get_product_by_id(product_id):
        db, cursor = get_database_connection()
        query = "SELECT * FROM products WHERE id = %s"
        cursor.execute(query, (product_id,))
        result = cursor.fetchone()
        db.close()

        if result:
            return Product(id=result[0], name=result[1], description=result[2], price=result[3])

        return None
    
    @staticmethod
    def get_user_cart(user_id):
        db, cursor = get_database_connection()
        query = "SELECT name FROM products WHERE id = %s"
        cursor.execute(query, (user_id,))
        results = cursor.fetchall()
        db.close()

        cart = [result[0] for result in results]
        return cart

class UserPurchases:
    @staticmethod
    def add_purchase(user_id, product_id):
        db, cursor = get_database_connection()
        insert_query = "INSERT INTO user_purchases (user_id, product_id) VALUES (%s, %s)"
        cursor.execute(insert_query, (user_id, product_id))
        db.commit()
        db.close()

    @staticmethod
    def get_user_purchases(user_id):
        db, cursor = get_database_connection()
        query = "SELECT * FROM user_purchases WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        user_purchases = cursor.fetchall()
        db.close()
        return user_purchases
    
    @staticmethod
    def delete_service_from_cart(user_id, product_id):
        db, cursor = get_database_connection()
        delete_query = "DELETE FROM user_purchases WHERE user_id = %s AND product_id = %s"
        cursor.execute(delete_query, (user_id, product_id))
        db.commit()
        db.close()

class Reviews:
    def __init__(self, id, user_id, reviews, username):
        self.id = id
        self.user_id = user_id
        self.reviews = reviews
        self.username = username
    @staticmethod
    def add_review(user_id, review):
        db, cursor = get_database_connection()
        query = "INSERT INTO reviews (user_id, review) VALUES (%s, %s)"
        cursor.execute(query, (user_id, review))
        db.commit()
        db.close()
    @staticmethod
    def get_reviews():
        db, cursor = get_database_connection()
        query = """
            SELECT reviews.*, users.username
            FROM reviews
            JOIN users ON reviews.user_id = users.id
        """
        cursor.execute(query)
        reviews = cursor.fetchall()
        db.close()
        return reviews

