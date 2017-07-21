from flask import request, redirect, render_template, url_for, flash, session
from datetime import datetime
import re
from models import User, Blog
from app import app, db
from hashutility import check_pw_hash

            

#TO get this to work without redirecting css I changed the function up to what's not allowed
@app.before_request
def login_required():
    #allowed_routes = ['log_in', 'signup', 'confirm_register', 'logout', 'testy']
    not_allowed_routes = ['index', 'add_blog', 'see_blog_page', 'see_blog_by_auth_page', 'display_authors' ]
    # it may seem weird to allow a user to logout if not logged in but makes it easier to redirect to login 
    # page with logout flash message 
    if request.endpoint  in not_allowed_routes and 'username' not in session:
        flash("You need to log in!", "negative")
        return redirect('/login')
    # elif request.endpoint not in not_allowed_routes and 'username' in session:
    #     flash("You are (b)logged in!", "positive")

@app.route('/test')
def testy():
    blogs = Blog.query.first()
    return render_template('/test.html', blogs=blogs)

@app.route('/')
def login():
    # just so user doesn't have to manually input /login on arrival, how would they know to do this?
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def log_in():
    #TODO place an if in session flash already logged in as "username?""
    if request.method == 'POST':
       
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_pw_hash(password, user.pw_hash):
            session['username'] = username
            flash("(B)logged in!", "positive")
            return redirect('/index')
        
        else:
            flash("Either you aren\'t registered or you screwed up the login", "negative")
            redirect('/')
    # else:
    #      User.make_fakes(5)
    return render_template('login.html')    

# def main_page():
#     #TODO get users preference for how they want blogs sorted on main page
#     blog_sort = request.args.get('blog_sort')
#     if blog_sort == 'newest':
#         blogs = Blog.query.order_by(Blog.entry_date.desc()).all()
#     # sort alphabetically, by author, length of body?
#     else:
#         blogs = Blog.query.all()
#     return render_template('welcome.html', blogs=blogs)
@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/confirm', methods=['POST'])
def confirm_register():
    """checks to see if inputs valid for login"""
    name = request.form['username']
    psw = request.form['passw']
    con_psw = request.form['conf_pass']
    match = re.compile(r"[^\s-]{3,20}")
    match_name = match.fullmatch(name)
    match_psw = match.fullmatch(psw)
    if name == 'random':
        User.make_fakes(5)
        return redirect('/index')
    elif not match_name:
        flash("no spaces allowed and must be between 3 and 20 chars", "negative")
        return render_template("signup.html")
    elif not match_psw:
         flash("no spaces allowed and must be between 3 and 20 chars", "negative")
         return render_template("signup.html", username=name)
    elif psw != con_psw:
        flash("Passwords didn't match!!", "negative")
        return render_template("signup.html", username=name)
    else:
        new_user = User(name, psw)
        db.session.add(new_user)
        db.session.commit()
        flash("(B)Logged IN!", "positive")
        return redirect('/index')
        #return redirect('url_for(main_page)')#/index')

@app.route('/index')#, methods=['GET','POST'])
def index():
    """#TODO get users preference for how they want blogs sorted on main page
    # TODO blog_sort = request.args.get('blog_sort')
    if blog_sort == 'newest':
        blogs = Blog.query.order_by(Blog.entry_date.desc()).all()
    # sort alphabetically, by author, length of body?
    else:"""
    blogs = Blog.query.order_by(Blog.entry_date.desc()).all()
    return render_template('index.html', blogs=blogs)

@app.route('/new_blog', methods=['GET','POST'])
def add_blog():
    # checks to make sure there is a title and a body to commit to database then displays blog to user
    if request.method == 'POST':
        title = request.form['blogtitle']
        body = request.form['body']
        if title == "random":
            Blog.bogus_blogs(5)
        if not title and not body:
            flash("You haven't entered ANYTHING!", "negative")
            return render_template('/new_blog.html')
        if not title:
            flash("You need to title your post!", "negative")
            return render_template('/new_blog.html', body=body)
        if not body:
            flash("You haven't actually blogged about anything!", "negative")
            return render_template('/new_blog.html', title=title)
        user = User.query.filter_by(username=session['username']).first()
        new_blog = Blog(title, body, entry_date=datetime.now(), author=user) #utcnow())
        db.session.add(new_blog)
        db.session.commit()
        #print("######USER IS:" + str(user))
        blog = Blog.query.order_by(Blog.entry_date.desc()).first()
        return render_template('/blog.html', blog=blog)
    # else:
    #     blog = Blog.bogus_blogs(10)
    #     return render_template('/new_blog.html')

@app.route('/blog/<blog_id>/')
#  gets the blogs id from the query paramater and then passes that blog to template
def see_blog_page(blog_id):
    check_blog = Blog.query.filter_by(id=blog_id).first()
    return render_template('/blog.html', blog=check_blog)

@app.route('/blogs_by_auth/<auth_id>/')
def see_blogs_by_auth_page(auth_id):
    # creates list of blogs that have that author and passes to template
    blogs = Blog.query.filter_by(auth_id=auth_id).all()
    #print('#######BLOG list' + blogs)
    return render_template('/blogs_by_auth.html', blogs=blogs)

@app.route('/auth_list')
def display_authors():
    authors = User.query.all()
    return render_template('auth_list.html', authors=authors)

@app.route('/logout')
def logout():
    # pretty self explanatory
    try:
        if session['username']:
            del session['username']
            flash("You are successfully logged out! Go outside!", "positive")
            return redirect('/')
    except KeyError:
        flash("You aren't currently logged in.", "negative")
        return redirect('/')    

if __name__ == ('__main__'):
    app.run()
