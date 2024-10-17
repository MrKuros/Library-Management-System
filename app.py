from flask import Flask, render_template, request, redirect, url_for, flash
import requests
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.orm import relationship, joinedload

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://your_username:your_password@localhost/library_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'dummy_secret_key'

mysql = SQLAlchemy(app)

# Models retrieved from database
class Book(mysql.Model):
    __tablename__ = 'books'
    id = mysql.Column(mysql.Integer, primary_key=True)
    title = mysql.Column(mysql.String(100), nullable=False)
    authors = mysql.Column(mysql.String(100))
    rating = mysql.Column(mysql.Float)
    stock = mysql.Column(mysql.Integer, nullable=False)

    # Define the relationship with Transaction
    transactions = relationship('Transaction', back_populates='book')

    def __repr__(self):
        return f'<Book {self.title}>'

class Member(mysql.Model):
    __tablename__ = 'members'
    id = mysql.Column(mysql.Integer, primary_key=True)
    name = mysql.Column(mysql.String(100), nullable=False)
    email = mysql.Column(mysql.String(100), nullable=False)
    outstanding_debt = mysql.Column(mysql.Float, default=0.0)

    # Define the relationship with Transaction
    transactions = relationship('Transaction', back_populates='member')

    def __repr__(self):
        return f'<Member {self.name}>'

class Transaction(mysql.Model):
    __tablename__ = 'transactions'
    id = mysql.Column(mysql.Integer, primary_key=True)
    member_id = mysql.Column(mysql.Integer, mysql.ForeignKey('members.id'), nullable=False)
    book_id = mysql.Column(mysql.Integer, mysql.ForeignKey('books.id'), nullable=False)
    issue_date = mysql.Column(mysql.DateTime, nullable=False, default=datetime.utcnow)
    return_date = mysql.Column(mysql.DateTime)
    fee = mysql.Column(mysql.Float, default=0.0)

    # Define relationships
    member = relationship('Member', back_populates='transactions')
    book = relationship('Book', back_populates='transactions')

@app.route("/")
def home():
    return render_template('index.html')

# Show books and routes for CRUD operations on books
@app.route("/books")
def books():
    books = Book.query.all()
    return render_template('books.html', books=books)

@app.route('/book/add', methods=['POST'])
def add_book():
    title = request.form['title']
    authors = request.form['authors']
    rating = request.form['rating']
    stock = request.form['stock']
    new_book = Book(title=title, authors=authors, rating=rating, stock=stock)
    mysql.session.add(new_book)
    mysql.session.commit()
    flash('Book added successfully!')
    return redirect(url_for('books'))

@app.route('/book/delete/<int:id>')
def delete_book(id):
    book = Book.query.filter_by(id=id).one()
    if book:
        mysql.session.delete(book)
        mysql.session.commit()
        flash("Book deleted successfully")
    else:
        flash("Book not found!")
    return redirect(url_for('books'))

@app.route('/book/edit/<int:id>', methods=['GET', 'POST', 'PUT'])
def edit_book(id):
    book = Book.query.filter_by(id=id).one()
    
    if request.method in ['POST', 'PUT']:
        book.title = request.form['title']
        book.authors = request.form['authors']
        book.stock = request.form['stock']
        
        mysql.session.commit()  
        
        flash('Book updated successfully')
        return redirect(url_for('books'))

    return render_template('edit_book.html', book=book)

# Routes for members and CRUD operations on members
@app.route("/members")
def members():
    members = Member.query.all()
    return render_template('members.html', members=members)

@app.route("/member/add", methods=['POST'])
def add_member():
    name = request.form['name']
    email = request.form['email']
    new_member = Member(name=name, email=email)
    mysql.session.add(new_member)
    mysql.session.commit()
    flash("Member added successfully")
    return redirect(url_for('members'))

@app.route("/member/delete/<int:id>")
def delete_member(id):
    member = Member.query.filter_by(id=id).one()
    if member:
        mysql.session.delete(member)
        mysql.session.commit()
        flash("Member deleted successfully!")
    else:
        flash("Member not found!")
    return redirect(url_for('members'))

@app.route('/member/edit/<int:id>', methods=['GET', 'POST', 'PUT'])
def edit_member(id):
    member = Member.query.filter_by(id=id).one()
    if request.method in ['POST','PUT']:
        member.name = request.form['name']
        member.email = request.form['email']
        # Ensure outstanding_debt is present in the form
        if 'outstanding_debt' in request.form:
            member.outstanding_debt = float(request.form['outstanding_debt'])
        try:
            mysql.session.commit()
            flash('Member updated successfully')
        except Exception as e:
            mysql.session.rollback()  # Rollback in case of error
            flash(f'Error updating member: {str(e)}')
        return redirect(url_for('members'))
    return render_template('edit_member.html', member=member)

@app.route("/issue", methods=['GET', 'POST'])
def issue_book():
    if request.method == 'POST':
        member_id = request.form['member_id']
        book_id = request.form['book_id']
        book = Book.query.get(book_id)
        member = Member.query.get(member_id)

        # Check if member's debt exceeds Rs. 500
        if member.outstanding_debt > 500:
            flash('Cannot issue book! Member has exceeded the debt limit of Rs. 500.')
            return redirect(url_for('books'))

        # Check if book is in stock
        if book.stock <= 0:
            flash('Book out of stock!')
            return redirect(url_for('books'))

        # Issue the book
        new_transaction = Transaction(
            member_id=member_id,
            book_id=book_id,
            issue_date=datetime.utcnow().date()
        )
        book.stock -= 1
        mysql.session.add(new_transaction)
        mysql.session.commit()

        flash("Book issued successfully")
        return redirect(url_for('books'))

    # If GET request, render the issue form
    members = Member.query.all()  # Fetch members
    books = Book.query.all()      # Fetch books
    return render_template('issue.html', members=members, books=books)

@app.route("/return_book/<int:transaction_id>", methods=['POST'])
def return_book(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    
    if transaction.return_date:
        flash('Book already returned!')
        return redirect(url_for('transactions'))

    # Set return date to current UTC time
    transaction.return_date = datetime.utcnow().date()

    # Calculate rental fee based on days
    rental_days = (transaction.return_date - transaction.issue_date).days
    transaction.fee = rental_days * 10  # Rs. 10 per day fee

    # Add fee to member's outstanding debt
    member = Member.query.get(transaction.member_id)
    member.outstanding_debt += transaction.fee

    # Commit changes to the database
    mysql.session.commit()

    if member.outstanding_debt > 500:
        flash('Member has exceeded the debt limit of Rs. 500!')
    else:
        flash(f'Book returned successfully! Rental fee: Rs. {transaction.fee}')

    return redirect(url_for('transactions'))

# Using Frappe API
@app.route('/import_books', methods=['GET', 'POST'])
def import_books():
    if request.method == 'POST':
        title = request.form['title']
        num_books = int(request.form['num_books'])
        page = 1

        total_imported = 0

        while total_imported < num_books:
            response = requests.get(f'https://frappe.io/api/method/frappe-library?page={page}&title={title}')
            if response.status_code == 200:
                books = response.json().get('message', [])
                
                for book in books:
                    if total_imported >= num_books:
                        break
                    
                    new_book = Book(
                        title=book['title'],
                        authors=book['authors'],
                        rating=book['average_rating'],  # Store rating instead of ISBN
                        stock=1
                    )
                    mysql.session.add(new_book)
                    total_imported += 1
                    
                mysql.session.commit()
                page += 1
            else:
                flash('Failed to fetch books from the API.')
                break

        flash(f'Successfully imported {total_imported} books!')
        return redirect(url_for('import_books'))

    return render_template('import_books.html')

@app.route('/transactions')
def transactions():
    transactions = mysql.session.query(Transaction).\
        options(joinedload(Transaction.member), joinedload(Transaction.book)).all()
    return render_template('transactions.html', transactions=transactions)

if __name__ == "__main__":
    app.run(debug=True)
