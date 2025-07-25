from datetime import datetime

from SaleBook import app, db
import hashlib
from SaleBook.models import User, UserRole, Book, Category, Cart, Author, Order, OrderDetail, Import, \
    ImportDetail, Regulation, OrderType, OrderStatus
import cloudinary.uploader


# add__ thêm mới
# get__ lấy thông tin
# get_all__ lấy tất cả, lấy tất cả theo điều kiện
# count__ đếm số lượng
# check__ kiểm tra tồn tại
# access_check__ kiểm tra quyền truy cập


# load sản phẩm cho trang chủ
def load_book(kw=None, page=1):
    """Get all books on the paginated page. And filter books by query."""
    query = Book.query

    page_size = app.config["PAGE_SIZE"]
    start = (page - 1) * page_size

    if kw:
        query = query.filter(Book.name.contains(kw))

    # if cate_id:
    #     query = query.filter(Product.category_id == cate_id)
    query = query.slice(start, start + page_size)

    return query.all()


# đếm số lượng sách (phân trang)
def count_books():
    return Book.query.count()


def get_book_by_id(book_id):
    return Book.query.get(book_id)


def get_all_book():
    return Book.query.all()


def add_new_book(name, price, quantity, description, barcode, category_id, author_id, image=None):
    b = Book(name=name, price=price, stock_quantity=quantity, description=description, barcode=barcode,
             category_id=category_id, author_id=author_id)
    if image:
        res = cloudinary.uploader.upload(image)
        b.image = res.get('secure_url')
    db.session.add(b)
    db.session.commit()
    return b


def check_exist_book(book_name):
    b = Book.query.filter(Book.name == book_name).first()
    return b.id


def get_all_barcode_book():
    """Get all barcode of books."""
    return Book.query.with_entities(Book.barcode).all()


def add_exist_book(book_id, quantity):
    """Add a book that already exists in the database."""
    b = Book.query.get(book_id)
    b.stock_quantity += quantity
    db.session.add(b)
    db.session.commit()
    return


def reduce_book_bought(book_id, quantity):
    """Reduce the quantity of books that have been bought."""
    b = Book.query.get(book_id)
    b.stock_quantity -= int(quantity)
    db.session.add(b)
    db.session.commit()
    return


def get_all_category():
    return Category.query.all()


def add_category(name, description):
    c = Category(name=name, description=description)
    db.session.add(c)
    db.session.commit()
    return


def get_all_author():
    """Get all authors."""
    return Author.query.all()


def add_author(name, description):
    """Add an author."""
    a = Author(name=name, description=description)
    db.session.add(a)
    db.session.commit()
    return


def get_user_by_id(user_id):
    return User.query.get(user_id)


def auth_user(username, password, role=None):
    """Authenticate a user by username and password. Optionally checks user role."""
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    u = User.query.filter(User.username.__eq__(username.strip()), User.password.__eq__(password))

    if role:
        u = u.filter(User.user_role.__eq__(role))

    return u.first()


def add_customer(name, username, password, avatar=None):
    """Add a customer to the database."""
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    u = User(name=name, username=username, password=password)
    if avatar:
        res = cloudinary.uploader.upload(avatar)
        u.avatar = res.get('secure_url')

    db.session.add(u)
    db.session.commit()
    return


# Kiểm tra user đã tồn tại khi tạo tài khoản
def check_exist_user(username):
    """Check if a username exists in the database."""
    return User.query.filter(User.username.__eq__(username.strip())).first()


def access_check(user_id):
    """Check if a user haven't admin permission."""
    u = User.query.get(user_id)
    if u and u.user_role in {UserRole.INVENTORY_MANAGER, UserRole.EMPLOYEE, UserRole.CUSTOMER}:
        return True
    return False


def access_check_importer(user_id):
    """Check if a user is an importer."""
    u = User.query.get(user_id)
    if u and u.user_role == UserRole.INVENTORY_MANAGER:
        return True
    return False


def access_check_employee(user_id):
    """Check if a user is an employee."""
    u = User.query.get(user_id)
    if u and u.user_role == UserRole.EMPLOYEE:
        return True
    return False


def access_check_admin(user_id):
    """Check if a user is an admin."""
    u = User.query.get(user_id)
    if u and u.user_role == UserRole.ADMIN:
        return True
    return False


# Thêm một sản phẩm vô cart
def add_to_cart(customer_id, book_id, quantity):
    """Add a book to the cart."""
    cart = Cart.query.filter(Cart.book_id == book_id, Cart.customer_id == customer_id).first()
    if cart: # if exist increase quantity
        cart.quantity += quantity
    else: # else add new book in cart
        new_cart = Cart(quantity=quantity, book_id=book_id, customer_id=customer_id)
        db.session.add(new_cart)
    db.session.commit()
    return


# lấy tất cả sản phẩm trong cart của một user
def get_all_cart(customer_id):
    """Get all books in a cart."""
    return Cart.query.filter(Cart.customer_id == customer_id).all()


# xóa một saản phẩm trong cart
def remove_cart_by_id(cart_id):
    """Remove a book from the cart."""
    c = Cart.query.get(cart_id)
    db.session.delete(c)
    db.session.commit()
    return


# xóa tất cả sản phẩm trong cart
def remove_all_cart_by_userid(customer_id):
    """Remove all books from the cart."""
    cart = Cart.query.filter(Cart.customer_id == customer_id).all()
    for c in cart:
        db.session.delete(c)
    db.session.commit()
    return


# Thay đổi sô lượng sản phẩm trong cart
def change_cart_quantity(cart_id, quantity):
    """Change the quantity of books in a cart."""
    cart = Cart.query.get(cart_id)
    cart.quantity = quantity
    db.session.add(cart)
    db.session.commit()
    return


# Thêm một order
def add_order_online(customer_id):
    """Place an order on the website (online). Then pay for it."""
    order = Order(customer_id=customer_id, is_paid=True, order_type=OrderType.ONLINE, is_shipped=False,status=OrderStatus.PENDING)
    db.session.add(order)
    db.session.commit()
    return order


def add_order_pending(customer_id):
    """Place an order on the website (online). But do not make a payment. Select 'pay on pickup' instead."""
    order = Order(customer_id=customer_id, is_paid=False, order_type=OrderType.ONLINE, is_shipped=False, status=OrderStatus.PENDING)
    db.session.add(order)
    db.session.commit()
    return order


# Thêm một order_detail (danh mục nhỏ trong order)
def add_order_detail(order_id, book_id, quantity, unit_price):
    """Add a book to the order existed."""
    o_detail = OrderDetail(order_id=order_id, book_id=book_id, quantity=quantity, unit_price=unit_price)
    db.session.add(o_detail)
    db.session.commit()
    return


# lấy tất cả order của một customer
# def get_all_order_by_customer_id(customer_id):
#     return Order.query.filter(Order.customer_id == customer_id).order_by(Order.order_date.desc()).all()


def get_all_order_with_page_size(customer_id, page=1):
    """Get all orders on a paginated page."""
    page_size = app.config["PAGE_SIZE"]
    start = (page - 1) * page_size

    o = Order.query.filter(Order.customer_id == customer_id)
    o = o.order_by(Order.created_at.desc())
    o = o.slice(start, start + page_size)
    return o.all()


def count_order_by_customer(customer_id):
    """Count the total number of orders for a customer to calculate pagination"""
    return Order.query.filter(Order.customer_id == customer_id).count()


def get_all_order_pending():
    """Get all pending orders for employee review."""
    return Order.query.filter(Order.status == OrderStatus.PENDING).order_by(Order.created_at.desc()).all()


def get_order_by_id(order_id):
    return Order.query.get(order_id)


def set_order_success(order_id, employee_id):
    o = Order.query.get(order_id)
    if not o.is_shipped:
        o.status = OrderStatus.SUCCESS
        o.is_paid = True
        o.is_shipped = True
        o.employee_id = employee_id
        db.session.add(o)
        db.session.commit()
        return
    else:
        return


def add_order_offline(employee_id, customer_id=None):
    """Place an order at the store (offline)."""
    i = Order(employee_id=employee_id, status=OrderStatus.SUCCESS, is_paid=True, is_shipped=True,
              order_type=OrderType.OFFLINE)
    if customer_id:
        i.customer_id = customer_id
    db.session.add(i)
    db.session.commit()
    return i


def add_order_detail_offline(order_id, book_id, quantity, unit_price):
    i_detail = OrderDetail(order_id=order_id, book_id=book_id, quantity=quantity, unit_price=unit_price)
    db.session.add(i_detail)
    db.session.commit()
    return


def get_all_order_of_employee(employee_id):
    """Get all orders for an employee to view history."""
    return Order.query.filter(Order.employee_id.__eq__(employee_id)).order_by(Order.created_at.desc()).all()


def auto_cancel_order():
    """Automatically cancel an order if the customer doesn't come to pick it up."""
    expired_orders = Order.query.filter(Order.status == OrderStatus.PENDING).all()
    if expired_orders:  # Nếu có được list đơn hàng pending
        for order in expired_orders:  # với một đơn hàng trong list đơn hàng pending
            if order.time_to_cancel <= datetime.now():  # nếu đã vượt quá thời gian chờ thì hủy đơn
                order.status = OrderStatus.CANCEL
                for detail in order.order_detail:  # với mỗi chi tiết đơn hàng trong một đơn hàng
                    add_exist_book(book_id=detail.book_id, quantity=detail.quantity)
    db.session.commit()
    return


def add_import_book(importer_id):
    i = Import(importer_id=importer_id)
    db.session.add(i)
    db.session.commit()
    return i


def add_import_detail_book(quantity, unit_price, import_id, book_id):
    """Add a book to the import book."""
    i_detail = ImportDetail(quantity=quantity, unit_price=unit_price, import_id=import_id, book_id=book_id)
    db.session.add(i_detail)
    db.session.commit()
    return


def get_all_import_by_importer(importer_id):
    """Get all import records for an importer to view history."""
    return Import.query.filter(Import.importer_id == importer_id).order_by(Import.import_date.desc()).all()


def get_minimun_quantity():
    """Get the rule of system"""
    regulation = Regulation.query.get(1)
    return regulation.value


def get_minimum_stock():
    """Get the rule of system"""
    regulation = Regulation.query.get(2)
    return regulation.value


def get_cancel_time():
    """Get the rule of system"""
    regulation = Regulation.query.get(3)
    return regulation.value


# # Báo cáo thống kê
# from sqlalchemy import func, extract
#
#
# def invoice_stats(kw=None, from_date=None, to_date=None):
#     p = db.session.query(Book.id, Book.name, func.sum(InvoiceDetail.quantity * InvoiceDetail.unit_price)) \
#         .join(InvoiceDetail, InvoiceDetail.book_id.__eq__(Book.id), isouter=True) \
#         .join(Invoice, Invoice.id.__eq__(InvoiceDetail.invoice_id)) \
#         .group_by(Book.id, Book.name)
#
#     if kw:
#         p.filter(Book.name.contains(kw))
#
#     return p.all()
#
#
# def order_stats(kw=None, from_date=None, to_date=None):
#     p = db.session.query(
#         Category.name,
#         func.sum(OrderDetail.quantity * OrderDetail.unit_price).label('total_revenue')
#     ).join(Book, Book.id == OrderDetail.book_id) \
#         .join(Category, Category.id == Book.category_id) \
#         .join(Order, Order.id == OrderDetail.order_id) \
#         .filter(Order.status == 'SUCCESS') \
#         .group_by(Category.name) \
#
#     if kw:
#         p.filter(Book.name.contains(kw))
#
#     return p.all()
#
#
# def get_stats_online(year, month, kw=None):
#     results = db.session.query(
#         Category.name.label('category_name'),
#         func.sum(OrderDetail.quantity * OrderDetail.unit_price).label('revenue'),
#         func.sum(OrderDetail.quantity).label('rental_count')
#     ).join(Book, Book.id == OrderDetail.book_id) \
#         .join(Category, Category.id == Book.category_id) \
#         .join(Order, Order.id == OrderDetail.order_id) \
#         .filter(
#         Order.status == 'SUCCESS',
#         extract('year', Order.order_date) == year,
#         extract('month', Order.order_date) == month
#     ).group_by(Category.name)
#
#     # Tính tổng doanh thu
#     total_revenue = sum([row.revenue for row in results])
#
#     if kw:
#         results = results.filter(Category.name.ilike(f'%{kw}%'))
#
#     results = results.all()
#
#     # Thêm tỷ lệ doanh thu
#     report = []
#     for row in results:
#         percentage = (row.revenue / total_revenue * 100) if total_revenue > 0 else 0
#         report.append({
#             'category_name': row.category_name,
#             'revenue': row.revenue,
#             'rental_count': row.rental_count,
#             'percentage': percentage
#         })
#
#     return report, total_revenue
#
#
# def get_stats_store(year, month, kw=None):
#     results = db.session.query(
#         Category.name.label('category_name'),
#         func.sum(InvoiceDetail.quantity * InvoiceDetail.unit_price).label('revenue'),
#         func.sum(InvoiceDetail.quantity).label('rental_count')
#     ).join(Book, Book.id == InvoiceDetail.book_id) \
#         .join(Category, Category.id == Book.category_id) \
#         .join(Invoice, Invoice.id == InvoiceDetail.invoice_id) \
#         .filter(
#         extract('year', Invoice.created_date) == year,
#         extract('month', Invoice.created_date) == month
#     ).group_by(Category.name)
#
#     # Tính tổng doanh thu
#     total_revenue = sum([row.revenue for row in results])
#
#     if kw:
#         results = results.filter(Category.name.ilike(f'%{kw}%'))
#
#     results = results.all()
#
#     # Thêm tỷ lệ doanh thu
#     report = []
#     for row in results:
#         percentage = (row.revenue / total_revenue * 100) if total_revenue > 0 else 0
#         report.append({
#             'category_name': row.category_name,
#             'revenue': row.revenue,
#             'rental_count': row.rental_count,
#             'percentage': percentage
#         })
#
#     return report, total_revenue
