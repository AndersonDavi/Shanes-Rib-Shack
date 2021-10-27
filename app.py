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
import re
from flask.helpers import flash
from flask.wrappers import Request
# from flask_mysqldb import MySQL
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = '7110c8ae51a4b5af97be6534caef90e4bb9bdcb3380af008f90b23a5d1616bf319bc298105da20fe'


# Comprobar inputs
def es_correo_valido(correo):
    expresion_regular = r"(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"
    return re.match(expresion_regular, correo) is not None

def RegisterValidate(name,lastname,email,password,password2):
        RegisterBool = ""
        if len(name)<1:
                RegisterBool = "Rellene todos los campos"
        elif len(lastname)<1:
                RegisterBool = "Rellene todos los campos"
        elif len(email)<1:
                RegisterBool = "Rellene todos los campos"
        elif es_correo_valido(email) == False:
                RegisterBool = "Digite un correo válido"
        elif len(password)<1:
                RegisterBool = "Rellene todos los campos"
        elif len(password)<6:
                RegisterBool = "La contraseña debe ser mínimo de 6 caracteres"
        elif password2 != password:
                RegisterBool = "Las contraseñas no coinciden"
        return RegisterBool


@app.route('/ShanesRibShack', methods = ['GET','POST'])
def index():
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

                connection = sqlite3.connect("shanesribdb.db")
                cur = connection.cursor()
                query = "SELECT * FROM users WHERE email='{s}'".format( s = email)
                cur.execute(query)
                result = cur.execute(query)
                result = result.fetchall()
                userinfo = result
                connection.commit()
                if len(userinfo)!=0:
                        if password == userinfo[0][3]:
                                if(userinfo[0][5]==1 or userinfo[0][5]=="1"):
                                        session['user'] = userinfo[0][1]
                                        return redirect(url_for('menu'))
                                elif(userinfo[0][5]==2 or userinfo[0][5]=="2"):
                                        session['user'] = userinfo[0][1]
                                        return redirect(url_for('Adminmenu'))      
                        else:
                                flash("Usuarrio y/o contraseña incorrecta")
                                return redirect(url_for('index'))
                flash("Usuarrio y/o contraseña incorrecta")
                return redirect(url_for('index'))
        else:
                return redirect(url_for('index'))

@app.route('/ShanesRibShack/menu')
def menu():
        if g.user:
                return render_template('menu.html',user=session['user'])
        return redirect(url_for('index'))

@app.route('/ShanesRibShack/AdminDashboard')
def Adminmenu():
        if g.user:
                return render_template('AdminMenu.html',user=session['user'])
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
        else:
                return redirect(url_for('index'))
        


@app.route('/ShanesRibShack/register/')
def userRegister():
        if g.user:
                return redirect(url_for('index'))
        return render_template('userregister.html')

@app.route('/add_user',methods=['GET','POST'])
def addUser():
        if request.method == 'POST':
                name = request.form['name']
                lastname = request.form['lastname']
                email = request.form['email']
                password = request.form['password']
                password2 = request.form['password2']
                ErrorMessage = RegisterValidate(name,lastname,email,password,password2)
                if RegisterValidate(name,lastname,email,password,password2)!="":
                        flash(ErrorMessage)
                        return redirect(url_for('userRegister'))
                else:
                        connection = sqlite3.connect("shanesribdb.db")
                        cur = connection.cursor()
                        query = "SELECT * FROM users WHERE email='{s}'".format( s = email)
                        cur.execute(query)
                        result = cur.execute(query)
                        result = result.fetchall()
                        if len(result)<1:
                                cur = connection.cursor()
                                query = "INSERT INTO users (name, lastname, email, password) VALUES ('{a}','{b}','{c}','{d}')".format( a = name, b = lastname, c=email,d=password)
                                cur.execute(query)
                                connection.commit()

                                flash('Registrado correctamente')
                                return redirect(url_for('Login'))
                        else:
                                flash('El correo ya se encuentra registrado')
                                return redirect(url_for('userRegister'))  
        else:
                return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(port = 3000, debug=True)
