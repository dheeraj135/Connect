from flask import Flask,render_template, flash, redirect, url_for, session, logging,request
from data import Articles
from flask_mysqldb import MySQL
from wtforms import Form, StringField,TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)

#Config flask_mysql
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='prajjwal'
app.config['MYSQL_DB']='myflaskapp'
app.config['MYSQL_CURSORCLASS']='DictCursor'
#init MYSQL
mysql=MySQL(app)

_articles=Articles();

@app.route('/')
def index():
    return render_template('home.html')

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/articles")
def artic():
    return render_template('articles.html',data=_articles)

@app.route("/article/<string:id>/")
def art(id):
    return render_template('article.html',id=id)

class RegisterForm(Form):
    name= StringField('Name',[validators.Length(min=1,max=50)])
    username=StringField('Username',[validators.Length(min=4,max=25)])
    email=StringField('Email',[validators.Length(min=6,max=50)])
    password= PasswordField('Password',[
       validators.DataRequired(),
       validators.EqualTo('confirm',message="Passwords do not match")
    ])
    confirm=PasswordField('Confirm Password')

@app.route('/register',methods=['GET','POST'])
def register():
    form = RegisterForm(request.form)
    if request.method=='POST' and form.validate():
        name=form.name.data
        email=form.email.data
        username=form.username.data
        password=sha256_crypt.encrypt(str(form.password.data))

        #cursor
        cur= mysql.connection.cursor()
        cur.execute("INSERT INTO users(name,email,username,password) values(%s,%s,%s,%s)",(name,email,username,password))

        #commit to DB
        mysql.connection.commit()

        #close connection
        cur.close()

        flash('You are now registered','success')
        return redirect(url_for('index'))    #write function where u want the page to redirect
    return render_template('register.html',data=form)


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
         #get form fields
         username=request.form['username']
         password_candidate=request.form['password']

         #cursor
         cur= mysql.connection.cursor()
         result=cur.execute("select * from users where username=%s",[username])

         if result>0:
             data=cur.fetchone()
             password=data['password']

             if sha256_crypt.verify(password_candidate,password):
                 app.logger.info('PASSWORD MATCHED')#prints in terminal
                 session['logged_in']=True
                 session['username']=username
                 flash("You are now logged in",'success')
                 return redirect(url_for('dashboard'))

             else:
                 app.logger.info('PASSWORD NOT MATCHED')
                 msg="Invalid Password"
                 return render_template('login.html',error=msg)

         else:
             app.logger.info("No User")
             msg="username not found"
             return render_template('login.html',error=msg)

         #close connection
         cur.close()

    return render_template('login.html')

#check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if 'logged_in' in session:
            return f(*args,**kwargs)
        else:
            flash("Unauthorized, Please Login",'danger')
            return redirect(url_for('login'))
    return wrap


@app.route('/logout')
def logout():
    session.clear()
    flash("You are now logged out",'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard.html')

if __name__=='__main__':
    app.secret_key='123456'
    app.run(debug=True)
