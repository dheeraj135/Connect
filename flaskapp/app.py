from flask import Flask,render_template, flash, redirect, url_for, session, logging,request
from data import Articles
from flask_mysqldb import MySQL
from wtforms import *
from passlib.hash import sha256_crypt
from functools import wraps
import json
import base64
app = Flask(__name__)

#Config flask_mysql
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='php'
app.config['MYSQL_PASSWORD']='localhost'
app.config['MYSQL_DB']='myflaskapp'
app.config['MYSQL_CURSORCLASS']='DictCursor'
#init MYSQL
mysql=MySQL(app)

# _articles=Articles();

@app.route('/')
def index():
    return render_template('home.html')

# @app.route("/about")
# def about():
#     return render_template('about.html')
#
# @app.route("/articles")
# def artic():
#     return render_template('articles.html',data=_articles)

# @app.route("/article/<string:id>/")
# def art(id):
#     return render_template('article.html',id=id)

class RegisterForm(Form):
    name= StringField('Name',[validators.Length(min=1,max=50),validators.DataRequired()])
    roll= StringField('Roll-Number',[validators.Length(6)])
    username=StringField('Username',[validators.Length(min=4,max=25),validators.DataRequired()])
    email=StringField('Email',[validators.Length(min=6,max=50),validators.DataRequired()])
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
        roll=form.roll.data
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
                 session['name']=data['name']
                 session['roll']=data['roll']
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

@app.route('/add_tag')
def addTag():
	valueT = request.args.get('valueT')
	app.logger.info(valueT);
	app.logger.info(len(valueT));
	if len(valueT) :
		username = session['username']
		app.logger.info(username);
		cur = mysql.connection.cursor();
		result = cur.execute("select tagArray from users where username=%s",[username]);
		app.logger.info(result);
		app.logger.info("Step1");
		TagList = cur.fetchone();
		TagList = TagList["tagArray"];
		app.logger.info(type(TagList))
		app.logger.info(TagList);
		app.logger.info("Step2");
		if(TagList!=None):
			#app.logger.info(base64.b64decode(TagList))
			#TagList = json.loads(base64.b64decode(TagList))
			app.logger.info("IN NOT NONE");
			TagList = json.loads(TagList);
			app.logger.info("step3");
			TagList.append(valueT)
			app.logger.info(TagList);
			app.logger.info("YO");
			TagList = json.dumps(TagList)
			#TagList = base64.b64encode(TagList);
			cur.execute("update users SET tagArray = %s where username=%s",(TagList,username));
			mysql.connection.commit();
		else:
			TagList = []
			TagList.append(valueT)
			app.logger.info(TagList);
			app.logger.info("YO");
			TagList = json.dumps(TagList)
			app.logger.info(TagList);
			#TagList = base64.b64encode(TagList);
			app.logger.info(TagList);
			a = "update users SET tagArray = '"+TagList+"' where username = '"+username+"'";
			app.logger.info(a);
			#app.logger.info("update users SET tagArray = %s where username = %s",(TagList,username));
			#res = cur.execute("update users SET tagArray = %s where username = %s",(TagList,username));
			res = cur.execute(a);
			mysql.connection.commit();
			app.logger.info(res);

@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard.html')


class ProjectForm(Form):
    title= StringField('Title',[validators.Length(min=1,max=100)])
    description= TextAreaField('Description')


@app.route('/add_article',methods=['GET','POST'])
@is_logged_in
def add_article():
    form = RegisterForm(request.form)
    if request.method=='POST' and form.validate():
        title=form.title.data
        description=form.description.data

        cur=mysql.connection.cursor()
        cur.execute("Insert into projects(name,project_title,roll_no,description) values(%s, %s, %s, %s)",(session[name],title,session[roll],description))
        mysql.connection.commit()
        




# @app.route('/input.html')
# @is_logged_in
# def input():
# 	return render_template('input_data.html')

if __name__=='__main__':
    app.secret_key='123456'
    app.run(debug=True)
