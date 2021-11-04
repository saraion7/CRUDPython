from logging import debug
from flask import Flask
from flask import render_template,request,redirect,url_for
from flask import send_from_directory
from flaskext.mysql import MySQL
from datetime import datetime
import os


inicio= Flask(__name__)

mysql= MySQL()
inicio.config['MYSQL_DATABASE_HOST']='localhost'
inicio.config['MYSQL_DATABASE_USER']='root'
inicio.config['MYSQL_DATABASE_PASSWORD']=''
inicio.config['MYSQL_DATABASE_DB']='system'
mysql.init_app(inicio)

FOLDER= os.path.join('uploads')
inicio.config['FOLDER']=FOLDER

@inicio.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
    return send_from_directory(inicio.config['FOLDER'],nombreFoto)

@inicio.route('/')
def index():

    sql = "SELECT * FROM usuarios;"
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql)
    
    usuarios= cursor.fetchall()
    print(usuarios)

    conn.commit()
    return render_template('usuarios/index.html', usuarios=usuarios) 

@inicio.route('/destroy/<int:id>')
def destroy(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT Perfil FROM usuarios WHERE id=%s", id)
    fila=cursor.fetchall()

    os.remove(os.path.join(inicio.config['FOLDER'], fila[0][0]))

    cursor.execute("DELETE FROM usuarios WHERE id=%s",(id))
    conn.commit()
    return redirect('/')

@inicio.route('/edit/<int:id>')
def edit(id):

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id=%s", (id))
    usuarios= cursor.fetchall()
    conn.commit()
    print(usuarios)
 
    return render_template('usuarios/edit.html', usuarios=usuarios)

@inicio.route('/update', methods=['POST'])
def update():

    _nombre=request.form['txtNombres']
    _correo=request.form['txtCorreo']
    _foto=request.files['txtFoto']
    id=request.form['txtId']

    sql ="UPDATE usuarios SET nombres=%s, correo=%s WHERE id=%s;"
    
    datos=(_nombre,_correo,id)

    conn = mysql.connect()
    cursor = conn.cursor()

    now= datetime.now()
    _time=now.strftime("%Y%H%M%S")

    if _foto.filename!='':
        nuevoNombreFoto=_time+_foto.filename
        _foto.save("uploads/"+nuevoNombreFoto)

        cursor.execute("SELECT Perfil FROM usuarios WHERE id=%s", id)
        fila=cursor.fetchall()

        os.remove(os.path.join(inicio.config['FOLDER'], fila[0][0]))
        cursor.execute("UPDATE usuarios SET Perfil=%s WHERE id=%s", (nuevoNombreFoto, id))
        conn.commit()

    cursor.execute(sql,datos)

    conn.commit()

    return redirect('/')

@inicio.route('/create')
def create():
    return render_template('usuarios/create.html')

@inicio.route('/store', methods=['POST'])
def storage():
    _nombre=request.form['txtNombres']
    _correo=request.form['txtCorreo']

    _foto=request.files['txtFoto']

    now= datetime.now()
    _time=now.strftime("%Y%H%M%S")

    if _foto.filename!='':
        nuevoNombreFoto=_time+_foto.filename
        _foto.save("uploads/"+nuevoNombreFoto)
    

    sql ="INSERT INTO `usuarios` (`id`, `nombres`, `correo`, `perfil`) VALUES (NULL,%s,%s,%s);"
    
    datos=(_nombre,_correo,nuevoNombreFoto)

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql,datos)
    conn.commit()
    return redirect('/')


if __name__ == '__main__':
    inicio.run(debug=True)
