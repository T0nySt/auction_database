from flask import Flask, render_template, redirect, url_for, flash, request
from models import db, User, Category, Item, Bid
from forms import BidForm, ItemForm, LoginForm, RegisterForm
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/TonyStoneDB/auction/auction.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# ── Flask-Login setup ────────────────────────────────────────────────────────
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'You must be logged in to do that.'
login_manager.login_message_category = 'error'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ── Timezone filter ──────────────────────────────────────────────────────────
@app.template_filter('localtime')
def localtime_filter(dt):
    return dt - timedelta(hours=4)

# ── Seed data ────────────────────────────────────────────────────────────────
def seed_data():
    if Category.query.count() == 0:
        categories = ['Electronics', 'Clothing', 'Collectibles', 'Books', 'Sports', 'Other']
        for name in categories:
            db.session.add(Category(name=name))
        db.session.commit()

@app.before_request
def create_tables():
    db.create_all()
    seed_data()

# ── Home: all open auctions ──────────────────────────────────────────────────
@app.route('/')
def index():
    now = datetime.utcnow()
    items = Item.query.filter(Item.status == 'open', Item.end_time > now).order_by(Item.end_time.asc()).all()
    categories = Category.query.all()
    selected_cat = request.args.get('category', type=int)
    if selected_cat:
        items = [i for i in items if i.category_id == selected_cat]
    return render_template('index.html', items=items, categories=categories, selected_cat=selected_cat)

# ── Register ─────────────────────────────────────────────────────────────────
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        existing = User.query.filter_by(username=form.username.data).first()
        if existing:
            flash('Username already taken. Please choose another.', 'error')
            return redirect(url_for('register'))
        existing_email = User.query.filter_by(email=form.email.data).first()
        if existing_email:
            flash('Email already registered. Please log in.', 'error')
            return redirect(url_for('login'))
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data)
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash(f'Account created! Welcome, {user.username}.', 'success')
        return redirect(url_for('index'))
    return render_template('register.html', form=form)

# ── Login ─────────────────────────────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash(f'Welcome back, {user.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        flash('Invalid username or password.', 'error')
    return render_template('login.html', form=form)

# ── Logout ────────────────────────────────────────────────────────────────────
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

# ── Item detail + bidding ────────────────────────────────────────────────────
@app.route('/item/<int:item_id>', methods=['GET', 'POST'])
def item_detail(item_id):
    item = Item.query.get_or_404(item_id)
    form = BidForm()

    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash('You must be logged in to place a bid.', 'error')
            return redirect(url_for('login', next=request.url))

        if not item.is_open():
            flash('This auction has ended.', 'error')
            return redirect(url_for('item_detail', item_id=item_id))

        min_bid = item.current_price() + 0.01
        if form.amount.data < min_bid:
            flash(f'Bid must be higher than the current price of ${item.current_price():.2f}.', 'error')
            return redirect(url_for('item_detail', item_id=item_id))

        bid = Bid(item_id=item.id, bidder_id=current_user.id, amount=form.amount.data)
        db.session.add(bid)
        db.session.commit()
        flash(f'Bid of ${form.amount.data:.2f} placed successfully!', 'success')
        return redirect(url_for('item_detail', item_id=item_id))

    bids = Bid.query.filter_by(item_id=item_id).order_by(Bid.placed_at.desc()).all()
    return render_template('item.html', item=item, form=form, bids=bids)

# ── Create a new listing ─────────────────────────────────────────────────────
@app.route('/item/new', methods=['GET', 'POST'])
@login_required
def create_item():
    form = ItemForm()
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]

    if form.validate_on_submit():
        item = Item(
            seller_id=current_user.id,
            category_id=form.category_id.data,
            title=form.title.data,
            description=form.description.data,
            starting_price=form.starting_price.data,
            end_time=form.end_time.data + timedelta(hours=4),
            status='open'
        )
        db.session.add(item)
        db.session.commit()
        flash('Your item has been listed!', 'success')
        return redirect(url_for('index'))

    return render_template('create.html', form=form)

# ── Close an auction manually ────────────────────────────────────────────────
@app.route('/item/<int:item_id>/close', methods=['POST'])
@login_required
def close_item(item_id):
    item = Item.query.get_or_404(item_id)
    item.status = 'closed'
    db.session.commit()
    flash('Auction closed.', 'success')
    return redirect(url_for('item_detail', item_id=item_id))

if __name__ == '__main__':
    app.run(debug=True)