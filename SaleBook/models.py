from datetime import datetime, timedelta

from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime, Boolean, Double, Date, Text
from sqlalchemy.orm import relationship

from SaleBook import db, app
from enum import Enum as ClassEnum
from flask_login import UserMixin

class UserRole(ClassEnum):
    ADMIN = 1
    CUSTOMER = 2
    EMPLOYEE = 3
    INVENTORY_MANAGER = 4


class OrderType(ClassEnum):
    ONLINE = 1
    OFFLINE = 2


class OrderStatus(ClassEnum):
    PENDING = 1  # Chờ lấy hàng
    SUCCESS = 2  # Thành công
    CANCEL = 3  # Đã hủy


class TransactionType(ClassEnum):
    PAYMENT = 1 #Mua
    RENT = 2 #Thuê
    TOP_UP = 3 #Nạp


class Regulation(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    value = Column(Integer, nullable=False)


class WalletLog(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_type = Column(Enum(TransactionType)) # Loại giao dịch (Nạp: Top_up, thuê: Rent, mua: Paymnet)
    balance_after = Column(Double) # Số dư sau giao dịch
    created_at = Column(DateTime, default=datetime.now)
    amount = Column(Double) # Số tiền của giao dịch

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)


class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    email = Column(String(50), unique=True)
    phone_number = Column(String(12))
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)
    avatar = Column(String(150),
                    default='https://res.cloudinary.com/drzc4fmxb/image/upload/v1733907010/xvethjfe9cycrroqi7po.jpg')
    created_at = Column(DateTime, default=datetime.now)
    user_role = Column(Enum(UserRole), default=UserRole.CUSTOMER)
    balance = Column(Double, default=0) # Số tiền trong trong ví

    cart = relationship('Cart', lazy='subquery', cascade='all, delete-orphan')
    wallet_logs = relationship(WalletLog, backref='user', lazy='subquery', cascade='all, delete-orphan')

    def __str__(self):
        return self.name


class Book(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    price = Column(Double, default=0)
    stock_quantity = Column(Integer, default=0)
    description = Column(String(255), nullable=True)
    image = Column(String(150),
                   default='https://res.cloudinary.com/drzc4fmxb/image/upload/v1733048058/tkk9qbfthr5uzpnymx56.jpg')
    barcode = Column(String(50), unique=True, nullable=True)
    is_active = Column(Boolean, default=True)

    category_id = Column(Integer, ForeignKey('category.id'), nullable=False)
    author_id = Column(Integer, ForeignKey('author.id'), nullable=False)

    category = relationship('Category', backref='books', lazy=True)
    author = relationship('Author', backref='books', lazy=True)

    online_content_url = Column(String(255), nullable=True)
    trial_duration = db.Column(db.Integer, nullable=True, default=300)

    def __str__(self):
        return self.name


#New
class TrialHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    trial_date = db.Column(db.DateTime, default=datetime.now)

    __table_args__ = (db.UniqueConstraint('user_id', 'book_id', name='unique_user_book_trial'),)


class Author(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    description = Column(String(255))

    def __str__(self):
        return self.name


class Category(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    description = Column(String(255))

    def __str__(self):
        return self.name


class Rental(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.now)
    due = Column(Integer, nullable=False) # Thời hạn thuê (hours)
    price = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True) # User còn được đọc không

    book_id = Column(Integer, ForeignKey('book.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    book = relationship(Book, backref='rented_books', lazy='subquery')
    user = relationship(User, backref='rented', lazy='subquery')

    @property
    def time_to_return(self):
        """Tính thời gian phải trả lại"""
        if self.is_active:
            returned_time = self.created_at + timedelta(hours=self.due)
            return returned_time
        else:
            return None


class Order(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.now)
    status = Column(Enum(OrderStatus)) # Pending, success, cancel
    order_type = Column(Enum(OrderType)) #buy in website(online) or store(offline)
    is_paid = Column(Boolean) # False if "pay on pickup" is selected
    is_shipped = Column(Boolean)

    customer_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    employee_id = Column(Integer, ForeignKey('user.id'), nullable=True)

    customer = relationship('User', backref='cus_orders', lazy='subquery', foreign_keys=[customer_id])
    employee = relationship('User', backref='emp_orders', lazy='subquery', foreign_keys=[employee_id])

    order_detail = relationship('OrderDetail', backref='order', lazy='subquery', cascade='all, delete-orphan')

    @property
    def total_price(self):
        total_price = 0
        for detail in self.order_detail:
            total_price += detail.sub_total
        return total_price

    @property
    def time_to_cancel(self):
        if self.status.name == 'PENDING':
            regulation = Regulation.query.get(3).value

            expiry_time = self.created_at + timedelta(hours=regulation)
            return expiry_time
        return None


class OrderDetail(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Double, nullable=False, default=0)

    order_id = Column(Integer, ForeignKey('order.id'), nullable=False)
    book_id = Column(Integer, ForeignKey('book.id'), nullable=False)

    book = relationship('Book')

    @property
    def sub_total(self):
        return self.quantity * self.unit_price


class Import(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    import_date = Column(DateTime, default=datetime.now())

    importer_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    importer = relationship('User', backref='imports', lazy=True)
    import_detail = relationship('ImportDetail', backref='import', lazy=True, cascade='all, delete-orphan')

    @property
    def total_price(self):
        total_price = 0
        for detail in self.import_detail:
            total_price += detail.sub_total
        return total_price


class ImportDetail(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Double, nullable=False, default=0)

    import_id = Column(Integer, ForeignKey('import.id'), nullable=False)
    book_id = Column(Integer, ForeignKey('book.id'), nullable=False)

    book = relationship('Book')

    @property
    def sub_total(self):
        return self.quantity * self.unit_price


class Cart(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    quantity = Column(Integer, default=1)

    book_id = Column(Integer, ForeignKey('book.id'), nullable=False)
    customer_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    books = relationship('Book', lazy='subquery')


if __name__ == '__main__':
    try:
        with app.app_context():
            db.drop_all()
            db.create_all()

            r1 = Regulation(name='Số lượng nhập tối thiểu', value=150)
            r2 = Regulation(name='Nhập những đầu sách có số lượng ít hơn', value=300)
            r3 = Regulation(name='Thời gian hủy đơn (giờ)', value=48)
            db.session.add(r1)
            db.session.add(r2)
            db.session.add(r3)

            import hashlib

            admin = User(name='Admin', username='admin', password=str(hashlib.md5('123'.strip().encode('utf-8')).hexdigest()), user_role=UserRole.ADMIN)
            db.session.add(admin)

            employee = User(name='Employee', username='employee', password=str(hashlib.md5('123'.strip().encode('utf-8')).hexdigest()), user_role=UserRole.EMPLOYEE)
            db.session.add(employee)

            importer = User(name='Importer', username='importer', password=str(hashlib.md5('123'.strip().encode('utf-8')).hexdigest()), user_role=UserRole.INVENTORY_MANAGER)
            db.session.add(importer)


            author = Author(name='J. K. Rowling', description='J. K. Rowling là một nhà văn, nhà biên kịch người Anh')
            category = Category(name='Novel')
            db.session.add(author)
            db.session.add(category)

            data = [
                {
                    "name": "Harry Potter",
                    "price": 17000,
                    "stock_quantity": 20,
                    "description": "Bộ truyện viết về những cuộc phiêu lưu phù thủy của cậu bé Harry Potter cùng hai người bạn thân là Ron Weasley và Hermione Granger",
                    "image": 'https://res.cloudinary.com/drzc4fmxb/image/upload/v1734077860/qctxm4xjuiuy5axe767q.jpg',
                    "online_content_url": "http://res.cloudinary.com/drzc4fmxb/raw/upload/v1752389499/soznqxuwzjxlhr5gtoco.pdf",
                    "category_id": 1,
                    "author_id": 1
                },
                {
                    "name": "Lord of the Rings",
                    "price": 15000,
                    "stock_quantity": 15,
                    "description": "Một câu chuyện thần thoại đầy hấp dẫn của J.R.R. Tolkien về cuộc chiến chống lại thế lực hắc ám Sauron.",
                    "image": 'https://res.cloudinary.com/drzc4fmxb/image/upload/v1734077860/qctxm4xjuiuy5axe767q.jpg',
                    "online_content_url": "http://res.cloudinary.com/drzc4fmxb/raw/upload/v1752389499/soznqxuwzjxlhr5gtoco.pdf",
                    "category_id": 1,
                    "author_id": 1
                },
                {
                    "name": "The Great Gatsby",
                    "price": 20000,
                    "stock_quantity": 50,
                    "description": "Tác phẩm kinh điển của F. Scott Fitzgerald mô tả cuộc sống giàu có và đau khổ ở thập kỷ 1920.",
                    "image": 'https://res.cloudinary.com/drzc4fmxb/image/upload/v1734077860/lik7dt77bsptgg5eakgq.jpg',
                    "online_content_url": "http://res.cloudinary.com/drzc4fmxb/raw/upload/v1752389499/soznqxuwzjxlhr5gtoco.pdf",
                    "category_id": 1,
                    "author_id": 1
                },
                {
                    "name": "To Kill a Mockingbird",
                    "price": 30000,
                    "stock_quantity": 40,
                    "description": "Cuốn sách đoạt giải Pulitzer của Harper Lee về cuộc đấu tranh chống phân biệt chủng tộc.",
                    "image": 'https://res.cloudinary.com/drzc4fmxb/image/upload/v1734077860/lik7dt77bsptgg5eakgq.jpg',
                    "online_content_url": "http://res.cloudinary.com/drzc4fmxb/raw/upload/v1752389499/soznqxuwzjxlhr5gtoco.pdf",
                    "category_id": 1,
                    "author_id": 1
                },
                {
                    "name": "1984",
                    "price": 35000,
                    "stock_quantity": 30,
                    "description": "George Orwell vẽ ra một thế giới dystopian đầy ám ảnh.",
                    "image": 'https://res.cloudinary.com/drzc4fmxb/image/upload/v1734077860/g0b1ypwqdp3ron415wcv.jpg',
                    "online_content_url": "http://res.cloudinary.com/drzc4fmxb/raw/upload/v1752389499/soznqxuwzjxlhr5gtoco.pdf",
                    "category_id": 1,
                    "author_id": 1
                },
                {
                    "name": "Pride and Prejudice",
                    "price": 65000,
                    "stock_quantity": 25,
                    "description": "Tác phẩm lãng mạn nổi tiếng của Jane Austen kể về tình yêu và sự hiểu lầm.",
                    "image": 'https://res.cloudinary.com/drzc4fmxb/image/upload/v1734077860/g0b1ypwqdp3ron415wcv.jpg',
                    "online_content_url": "http://res.cloudinary.com/drzc4fmxb/raw/upload/v1752389499/soznqxuwzjxlhr5gtoco.pdf",
                    "category_id": 1,
                    "author_id": 1
                },
                {
                    "name": "Moby Dick",
                    "price": 45000,
                    "stock_quantity": 10,
                    "description": "Hành trình đầy bi kịch và phiêu lưu của thuyền trưởng Ahab do Herman Melville kể.",
                    "image": 'https://res.cloudinary.com/drzc4fmxb/image/upload/v1734077860/lik7dt77bsptgg5eakgq.jpg',
                    "online_content_url": "http://res.cloudinary.com/drzc4fmxb/raw/upload/v1752389499/soznqxuwzjxlhr5gtoco.pdf",
                    "category_id": 1,
                    "author_id": 1
                },
                {
                    "name": "The Catcher in the Rye",
                    "price": 25000,
                    "stock_quantity": 20,
                    "description": "Cuốn tiểu thuyết của J.D. Salinger về sự nổi loạn tuổi trẻ.",
                    "image": 'https://res.cloudinary.com/drzc4fmxb/image/upload/v1734077860/g0b1ypwqdp3ron415wcv.jpg',
                    "online_content_url": "http://res.cloudinary.com/drzc4fmxb/raw/upload/v1752389499/soznqxuwzjxlhr5gtoco.pdf",
                    "category_id": 1,
                    "author_id": 1
                },
                {
                    "name": "War and Peace",
                    "price": 35000,
                    "stock_quantity": 12,
                    "description": "Một tác phẩm vĩ đại của Leo Tolstoy về cuộc chiến và tình yêu ở nước Nga.",
                    "image": 'https://res.cloudinary.com/drzc4fmxb/image/upload/v1734077860/qctxm4xjuiuy5axe767q.jpg',
                    "online_content_url": "http://res.cloudinary.com/drzc4fmxb/raw/upload/v1752389499/soznqxuwzjxlhr5gtoco.pdf",
                    "category_id": 1,
                    "author_id": 1
                },
                {
                    "name": "Crime and Punishment",
                    "price": 50000,
                    "stock_quantity": 18,
                    "description": "Dostoevsky viết về tội ác và sự cứu chuộc đầy triết lý và sâu sắc.",
                    "image": 'https://res.cloudinary.com/drzc4fmxb/image/upload/v1734077860/g0b1ypwqdp3ron415wcv.jpg',
                    "online_content_url": "http://res.cloudinary.com/drzc4fmxb/raw/upload/v1752389499/soznqxuwzjxlhr5gtoco.pdf",
                    "category_id": 1,
                    "author_id": 1
                }
            ]

            for b in data:
                book = Book(**b)
                db.session.add(book)

            db.session.commit()
            print("success to create database")
    except Exception as e:
        print("Fail to create database, err:{}".format(e))


