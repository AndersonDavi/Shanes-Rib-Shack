from flask import (
        Flask, 
        render_template,
        request, 
        redirect,
        url_for,
        session,
        g
)
import os
from flask.helpers import flash
from flask.wrappers import Request
# from flask_login import LoginManager
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['MYSQL_HOST']= '127.0.0.1'
app.config['MYSQL_USER']= 'root'
app.config['MYSQL_PASSWORD']= ''
app.config['MYSQL_DB']= 'shanesribdb'
mysql = MySQL(app)
app.config['SECRET_KEY'] = '7110c8ae51a4b5af97be6534caef90e4bb9bdcb3380af008f90b23a5d1616bf319bc298105da20fe'


# @app.route('/')
# def index():
#         return 'a'

# @app.route('/ShanesRibShack')
# def index():
#         return render_template('index.html')

@app.route('/ShanesRibShack', methods = ['GET','POST'])
def index():
        # login_form = forms 
        if g.user:
                 return redirect(url_for('menu'))
        else:
                if request.method == 'POST':
                        return redirect(url_for('Login'))        
                else:
                        return render_template('index.html')

@app.route('/login',methods=['GET','POST'])
def Login():
        if request.method=='POST':
                session.pop('user', None)
                email = request.form['email']
                password = request.form['password']

                cur = mysql.connection.cursor()
                cur.execute("SELECT * FROM users WHERE email=%s",(email,))
                userinfo = cur.fetchone()
                cur.close()
                if userinfo is not None:

                        if password == userinfo[4]:
                                session['user'] = userinfo[1]
                                print("inicio")
                                return redirect(url_for('menu'))
                        else:
                                return redirect(url_for('index'))
                                # return render_template('index.html')
                return redirect(url_for('index'))
        else:
                return redirect(url_for('index'))

@app.route('/ShanesRibShack/menu')
def menu():
        if g.user:
                return render_template('menu.html',user=session['user'])
        return redirect(url_for('index'))

@app.before_request
def before_request():
        g.user = None

        if 'user' in session:
                g.user = session['user']


@app.route('/ShanesRibShack/logout',methods=['GET','POST'])
def DropSession():
        if request.method=='POST':
                session.pop('user',None)
                return redirect(url_for('index'))
                # return render_template('index.html')
        else:
                return redirect(url_for('index'))
        


@app.route('/ShanesRibShack/register/')
def userRegister():
        if g.user:
                return redirect(url_for('index'))
        return render_template('userregister.html')
        # return render_template('index.html')

@app.route('/add_user',methods=['GET','POST'])
def addUser():
        if request.method == 'POST':
                name = request.form['name']
                lastname = request.form['lastname']
                email = request.form['email']
                password = request.form['password']
                cur = mysql.connection.cursor()
                cur.execute('INSERT INTO users (name, lastname, email, password) VALUES (%s,%s,%s,%s)', (name,lastname,email,password))
                mysql.connection.commit()
                flash('Registrado correctamente')
                # session['user'] = name

                return redirect(url_for('Login'))
        else:
                return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(port = 3000, debug = True)