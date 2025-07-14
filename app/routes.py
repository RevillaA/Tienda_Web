# app/routes.py
from flask import Blueprint, render_template, request, redirect, session, flash
from . import mysql
from flask import flash

main = Blueprint('main', __name__)

# ---------- PROTECCIÓN DE RUTAS ----------
def login_required(view_func):
    def wrapper(*args, **kwargs):
        if 'usuario' not in session:
            return redirect('/login')
        return view_func(*args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper

# ---------- LOGIN / LOGOUT ----------
@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['username']
        clave = request.form['password']

        cur = mysql.connection.cursor()
        # Consulta vulnerable a inyección SQL intencionalmente
        cur.execute(f"SELECT * FROM usuarios WHERE username = '{usuario}' AND password = '{clave}'")
        user = cur.fetchone()
        cur.close()

        if user:
            session['usuario'] = usuario
            return redirect('/productos')

        flash('Credenciales inválidas')
        return redirect('/login')

    return render_template('login.html')

@main.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# ---------- INDEX ----------
@main.route('/')
def index():
    return redirect('/productos')

# ---------- CATEGORÍAS ----------
@main.route('/categorias')
@login_required
def listar_categorias():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM categorias")
    categorias = cur.fetchall()
    cur.close()
    return render_template('categorias.html', categorias=categorias, request=request)

@main.route('/categorias/agregar', methods=['POST'])
@login_required
def agregar_categoria():
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']

    cur = mysql.connection.cursor()
    cur.execute(f"""
        INSERT INTO categorias (nombre, descripcion)
        VALUES ('{nombre}', '{descripcion}')
    """)
    mysql.connection.commit()
    cur.close()
    return redirect('/categorias')

@main.route('/categorias/eliminar/<int:id>')
def eliminar_categoria(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute(f"DELETE FROM categorias WHERE id = {id}")
        mysql.connection.commit()
        cur.close()
    except Exception as e:
        flash("No se puede eliminar la categoría porque tiene productos asociados.")
        return redirect('/categorias')
    return redirect('/categorias')

@main.route('/categorias/editar/<int:id>', methods=['POST'])
def editar_categoria(id):
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    cur = mysql.connection.cursor()
    cur.execute(f"""
        UPDATE categorias SET nombre = '{nombre}', descripcion = '{descripcion}'
        WHERE id = {id}
    """)
    mysql.connection.commit()
    cur.close()
    return redirect('/categorias')

# ---------- PRODUCTOS ----------
@main.route('/productos')
@login_required
def listar_productos():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM categorias")
    categorias = cur.fetchall()

    cur.execute("""
        SELECT p.id, p.nombre, p.descripcion, p.precio, p.stock, c.nombre
        FROM productos p
        JOIN categorias c ON p.categoria_id = c.id
    """)
    productos = cur.fetchall()
    cur.close()
    return render_template('productos.html', productos=productos, categorias=categorias, request=request)

@main.route('/productos/agregar', methods=['POST'])
@login_required
def agregar_producto():
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    precio = request.form['precio']
    stock = request.form['stock']
    categoria_id = request.form['categoria_id']

    cur = mysql.connection.cursor()
    cur.execute(f"""
        INSERT INTO productos (nombre, descripcion, precio, stock, categoria_id)
        VALUES ('{nombre}', '{descripcion}', {precio}, {stock}, {categoria_id})
    """)
    mysql.connection.commit()
    cur.close()
    return redirect('/productos')

@main.route('/productos/eliminar/<int:id>')
@login_required
def eliminar_producto(id):
    cur = mysql.connection.cursor()
    cur.execute(f"DELETE FROM productos WHERE id = {id}")
    mysql.connection.commit()
    cur.close()
    return redirect('/productos')

@main.route('/productos/editar/<int:id>', methods=['POST'])
@login_required
def editar_producto(id):
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    precio = request.form['precio']
    stock = request.form['stock']
    categoria_id = request.form['categoria_id']

    cur = mysql.connection.cursor()
    cur.execute(f"""
        UPDATE productos
        SET nombre='{nombre}', descripcion='{descripcion}', precio={precio}, stock={stock}, categoria_id={categoria_id}
        WHERE id={id}
    """)
    mysql.connection.commit()
    cur.close()
    return redirect('/productos')
