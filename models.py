from app import db
import forgery_py
from random import seed, randint, choice
from hashutility import make_pw_hash

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    entry_date = db.Column(db.DateTime)
    auth_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, entry_date, author):#=datetime.utcnow()):
        self.title = title
        self.body = body
        self.entry_date = entry_date
        self.author = author

    def __repr__(self):
        return 'The {} blog contains {}.'.format(self.title, self.body)

    def bogus_blogs(count):
        # generates fake blogs 
        seed()
        auth_count = User.query.count()
        for fake in range(count):
            auth = User.query.offset(randint(0, auth_count -1)).first()
            blog = Blog(title=forgery_py.lorem_ipsum.word(), body=forgery_py.lorem_ipsum.sentences(randint(1,7)),
                        entry_date=forgery_py.date.date(), author=auth)
            # can't find a forgery_py module to give a time, datetime module not supported
            db.session.add(blog)
            db.session.commit()
        new_blog = Blog.query.first()
        return new_blog

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    pw_hash = db.Column(db.String(100)) 
    blogs = db.relationship('Blog', backref='author')

    def __init__(self, username, password):
        self.username = username
        self.pw_hash = make_pw_hash(password)

    def __repr__(self):
        return '{}'.format(self.username)

    def make_fakes(count):
        #generates however many (count) authors for testing population
        seed()
        for fake in range(count):
            author = User(username=forgery_py.internet.user_name(True), password=forgery_py.lorem_ipsum.word())
            db.session.add(author)
            db.session.commit()

        user = User.query.first()
        return user