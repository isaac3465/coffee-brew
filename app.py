from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database configuration
db_path = r'C:\Users\741093.NEWCOLLEGE\Downloads\SQLiteDatabaseBrowserPortable\newcoffee.db'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


# Order model
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='Pending', nullable=False)
    user = db.relationship('User', backref=db.backref('orders', lazy=True))
    items = db.relationship('OrderItem', backref='order', lazy=True)


# OrderItem model (for storing individual items in the order)
class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    item_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)


# Payment model
class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    card_name = db.Column(db.String(100), nullable=False)
    card_number = db.Column(db.String(16), nullable=False)
    expiration_date = db.Column(db.String(5), nullable=False)  # MM/YY format
    cvv = db.Column(db.String(3), nullable=False)
    order = db.relationship('Order', backref=db.backref('payment', uselist=False))


# Routes
@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password', 'danger')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='sha256')

        if User.query.filter_by(email=email).first():
            flash('Email already exists!', 'danger')
        elif User.query.filter_by(username=username).first():
            flash('Username already exists!', 'danger')
        else:
            new_user = User(username=username, email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('home'))


@app.route('/menu')
def menu():
    return render_template('menu.html')


@app.route('/about')
def about_us():
    return render_template('About Us.html')


@app.route('/contact')
def contact_us():
    return render_template('Contact Us.html')


@app.route('/order', methods=['GET', 'POST'])
def order():
    if request.method == 'POST':
        if 'user_id' not in session:
            flash('You need to login first', 'danger')
            return redirect(url_for('login'))

        # Get the items and quantities from the form
        items = request.form.getlist('item')  # List of items in the cart
        quantities = request.form.getlist('quantity')  # Quantities for each item
        total_amount = float(request.form['total_amount'])

        # Create the order
        new_order = Order(user_id=session['user_id'], total_amount=total_amount)
        db.session.add(new_order)
        db.session.commit()

        # Add items to the order
        for item, qty in zip(items, quantities):
            order_item = OrderItem(order_id=new_order.id, item_name=item, price=2.50,
                                   quantity=int(qty))  # Example price
            db.session.add(order_item)

        # Get payment details
        card_name = request.form['card_name']
        card_number = request.form['card_number']
        expiration_date = request.form['expiration_date']
        cvv = request.form['cvv']

        # Save payment information
        payment = Payment(order_id=new_order.id, card_name=card_name, card_number=card_number,
                          expiration_date=expiration_date, cvv=cvv)
        db.session.add(payment)
        db.session.commit()

        flash('Order placed successfully!', 'success')
        return redirect(url_for('home'))

    return render_template('order.html')


if __name__ == '__main__':
    # Ensure database directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # Create database tables within the application context
    with app.app_context():
        db.create_all()
    app.run(debug=True)


