from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String

app = Flask(__name__)

class Base(DeclarativeBase):
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///new-books-collection.db"
db = SQLAlchemy(model_class=Base)
db.init_app(app)

#Create Table
class Book(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    rating: Mapped[str] = mapped_column(nullable=False)

    def __repr__(self):
        return f'<Book {self.title}>'

with app.app_context():
    db.create_all()


@app.route('/', methods=["GET", "POST"])
def home():
    with app.app_context():
        result = db.session.execute(db.select(Book).order_by(Book.title))
        all_books = result.scalars()
        return render_template('index.html', all_books=all_books)



@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        with app.app_context():
            new_book = Book(
                title = request.form['title'],
                author = request.form['author'],
                rating = request.form['rating']
            )
            db.session.add(new_book)
            db.session.commit()

        return redirect(url_for('home'))

    return render_template('add.html')

@app.route("/edit", methods=["GET", "POST"])
def edit():
    #after edit form id submitted, redirects to home
    if request.method == "POST":
        with app.app_context():
            book_id = request.form['id']
            book_to_update = db.session.execute(db.select(Book).where(Book.id==book_id)).scalar()
            book_to_update.rating = request.form['rating']
            db.session.commit()
        return redirect(url_for('home'))

    # this takes the id parameter from the anchor link in form in index.html
    book_id = request.args.get('id')
    #this get the specific book data and passes it to edit.html
    book_selected = db.get_or_404(Book, book_id)
    return render_template('edit.html', book=book_selected)

@app.route("/delete")
def delete():
    book_id = request.args.get('id')
    with app.app_context():
        book_to_delete = db.get_or_404(Book, book_id)
        db.session.delete(book_to_delete)
        db.session.commit()
        return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)

