
from flask import Flask, request, render_template, jsonify
import mysql.connector
import os

app = Flask(__name__)

db_config = {
    'host': os.environ.get('DB_HOST', 'db-master'),
    'user': 'root',
    'password': 'password',
    'database': 'inventario'
}

def get_db():
    return mysql.connector.connect(**db_config)

@app.route('/')
def index():
    return render_template('index.html')

# --- LOGIN ---
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE username=%s AND password=%s",
                   (data['username'], data['password']))
    user = cursor.fetchone()
    if user:
        return jsonify({'success': True, 'message': 'Login exitoso'})
    else:
        return jsonify({'success': False, 'message': 'Credenciales incorrectas'}), 401

# --- AGREGAR PRODUCTO ---
@app.route('/productos', methods=['POST'])
def agregar_producto():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM productos WHERE codigo = %s", (data['codigo'],))
    if cursor.fetchone()[0] > 0:
        return jsonify({'error': 'Código duplicado'}), 400

    cursor.execute("INSERT INTO productos (nombre, codigo, descripcion, unidad, categoria) VALUES (%s, %s, %s, %s, %s)",
                   (data['nombre'], data['codigo'], data['descripcion'], data['unidad'], data['categoria']))
    conn.commit()
    return jsonify({'message': 'Producto agregado'}), 201

# --- OBTENER TODOS LOS PRODUCTOS ---
@app.route('/productos', methods=['GET'])
def obtener_productos():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM productos")
    return jsonify(cursor.fetchall())

# --- CONSULTAR PRODUCTO POR CÓDIGO ---
@app.route('/producto/<codigo>', methods=['GET'])
def consultar_producto(codigo):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM productos WHERE codigo = %s", (codigo,))
    producto = cursor.fetchone()
    if producto:
        return jsonify(producto)
    else:
        return jsonify({'message': 'Producto no encontrado'}), 404

# --- EDITAR PRODUCTO ---
@app.route('/productos/<int:id>', methods=['PUT'])
def editar_producto(id):
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE productos SET nombre=%s, codigo=%s, descripcion=%s, unidad=%s, categoria=%s 
        WHERE id=%s
    """, (data['nombre'], data['codigo'], data['descripcion'], data['unidad'], data['categoria'], id))
    conn.commit()
    return jsonify({'message': 'Producto actualizado'})

# --- ELIMINAR PRODUCTO ---
@app.route('/productos/<int:id>', methods=['DELETE'])
def eliminar_producto(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos WHERE id = %s", (id,))
    conn.commit()
    return jsonify({'message': 'Producto eliminado'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
