from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# Stores all registered users — both sellers who list items and bidders who place bids.
# Primary key: id. Referenced by Item.seller_id (one user can sell many items)
# and Bid.bidder_id (one user can place many bids).
# UserMixin adds the required Flask-Login methods (is_authenticated, is_active, etc.)
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship('Item', backref='seller', lazy=True, foreign_keys='Item.seller_id')
    bids = db.relationship('Bid', backref='bidder', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'


# Lookup table for item categories — keeps category names normalized instead of repeated on every item.
# Primary key: id. Referenced by Item.category_id (one category can have many items).
class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    items = db.relationship('Item', backref='category', lazy=True)

    def __repr__(self):
        return f'<Category {self.name}>'


# Represents each auction listing — stores title, description, price, end time, and status.
# Primary key: id.
# Foreign key: seller_id -> User.id (the user who created the listing).
# Foreign key: category_id -> Category.id (the category this item belongs to).
# One item can receive many bids via the Bid table.
class Item(db.Model):
    __tablename__ = 'item'
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    starting_price = db.Column(db.Float, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(10), default='open')  # 'open' or 'closed'

    bids = db.relationship('Bid', backref='item', lazy=True)

    def current_price(self):
        if self.bids:
            return max(b.amount for b in self.bids)
        return self.starting_price

    def bid_count(self):
        return len(self.bids)

    def is_open(self):
        return self.status == 'open' and datetime.utcnow() < self.end_time

    def __repr__(self):
        return f'<Item {self.title}>'


# Records every bid placed on an auction.
# Primary key: id.
# Foreign key: item_id -> Item.id (the auction this bid was placed on).
# Foreign key: bidder_id -> User.id (the user who placed the bid).
# Acts as a junction between User and Item — one user can bid on many items,
# one item can receive bids from many users.
class Bid(db.Model):
    __tablename__ = 'bid'
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    bidder_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    placed_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Bid {self.amount} on Item {self.item_id}>'