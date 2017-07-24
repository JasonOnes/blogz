from flask import request, redirect, render_template, url_for, flash, session
from datetime import datetime
import re
from models import User, Blog
from app import app, db, BLOGS_PER_PAGE
from hashutility import check_pw_hash, make_pw_hash

        

#TO get this to work without redirecting css I changed the function up to what's not allowed
@app.before_request
def login_required():
    not_allowed_routes = ['index', 'add_blog', 'see_blog_page', 'see_blog_by_auth_page', 'display_authors' ]
    # it may seem weird to allow a user to logout if not logged in but makes it easier to redirect to login 
    # page with logout flash message 
    if request.endpoint  in not_allowed_routes and 'username' not in session:
        flash("You need to log in!", "negative")
        return redirect('/login')
    
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
    # basic login using light hashing
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = User.query.filter_by(username=username)
        if username == "random": # for dev to populate blogz randomly regular user might mistakenly find this
            User.make_fakes(5)
            flash("5 new fake users ceated, but still. . . ", "positive")
            return redirect('/index')
        elif users.count() == 1:
            #if there is only one user by that name then . . . shouldn't be duplicates due to condition at registration
            user = users.first()
            if user and check_pw_hash(password, user.pw_hash):
                session['username'] = username
                flash("(B)logged in!", "positive")
                return redirect('/index')
            else:
                flash("wrong hash", "negative")
                print(str(user) + "**" + str(make_pw_hash(password) + "**" + str(user.pw_hash)))
                #this was for testing salted hash functions which were giving me problems
                return redirect('/login')
        else:
            flash("Either you aren\'t registered or you screwed up the login", "negative")
            return redirect('/')
    return render_template('login.html')    

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
    # if name == 'random':
    #     User.make_fakes(5)
    #     return redirect('/index')
    user_with_that_name = User.query.filter_by(username=name).count()
    # filtering so no duplicate usernames can occur by checking to see if the list of the
    # names that match in database is 0
    if user_with_that_name > 0:
        flash("That name is already in use, come up with another", "negative")
        return render_template("signup.html")
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
        session['username'] = new_user.username
        flash("(B)Logged IN!", "positive")
        return redirect('/index')
    

@app.route('/index')#, methods=['GET','POST'])
@app.route('/index/<int:page>')#, methods=['GET', 'POST'])
def index(page=1):
    """turns list of blogs into a Pagination object which can can be divided by 5, said object must
    cannot be iterized however and must be converted to list by calling .items which is done at template
    level."""
    #BLOGS_PER_PAGE = put in app.py for consistency and DRY
    pages = Blog.query.order_by(Blog.entry_date.desc()).paginate(page, BLOGS_PER_PAGE, error_out=False)
    return render_template('index.html', pages=pages)

@app.route('/new_blog', methods=['GET','POST'])
def add_blog():
    # checks to make sure there is a title and a body to commit to database then displays blog to user
    if request.method == 'POST':
        title = request.form['blogtitle']
        body = request.form['body']
        if title == "random" and not body:# for dev to populate blogz
            Blog.bogus_blogs(5)
            flash("5 bogus blogs have been added.", "positive")
            return redirect('/index')
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
    return render_template('/new_blog.html')

@app.route('/blog/<blog_id>/')
#  gets the blogs id from the query paramater and then passes that blog to template
def see_blog_page(blog_id):
    check_blog = Blog.query.filter_by(id=blog_id).first()
    return render_template('/blog.html', blog=check_blog)

@app.route('/blogs_by_auth/<auth_id>')#/<int:page>')
@app.route('/blogs_by_auth/<auth_id>/<int:page>')
def see_blogs_by_auth_page(auth_id, page=1):
    # displays all the blogs by linked author
    pages = Blog.query.filter_by(auth_id=auth_id).order_by(Blog.entry_date.desc()).paginate(page, BLOGS_PER_PAGE, error_out=False)
    """ We'll do the following in views"""
    # prev_num = None
    # if pages.has_prev:
    #     prev_num = url_for('see_blogs_by_auth_page', auth_id=auth_id, page=page-1, _external=True)
    # #_next = None
    # if pages.has_next:
    #     next_num = url_for('see_blogs_by_auth_page', auth_id=auth_id, page=page+1, _external=True)
    try:
        author = str(pages.items[0-(len(pages.items))].author.username)#convoluted but works, gives the name of the
        #author for all the blogs on the pages can't check the paginate object itself
    except IndexError:
        flash("No blogs by this author at this time.", "negative")
        return render_template('blogs_by_auth.html', auth_id=auth_id, pages=pages)# since there are no blogs can't retreive author
    return render_template('blogs_by_auth.html', auth_id=auth_id, pages=pages, author=author)

@app.route('/auth_list')
def display_authors():
    authors = User.query.order_by(User.username).all()# alphabetic
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
