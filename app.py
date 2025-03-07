from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": 
"http://localhost:3000"}})

def get_db():
    conn = sqlite3.connect('camiones.db')
    conn.row_factory = sqlite3.Row
    return conn

# Crear la tabla solo si no existe
with get_db() as conn:
    conn.execute('''CREATE TABLE IF NOT EXISTS camiones
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     año INTEGER NOT NULL,
                     marca TEXT NOT NULL,
                     modelo TEXT NOT NULL,
                     vin TEXT NOT NULL,
                     placa TEXT NOT NULL,
                     dueño TEXT NOT NULL)''')

@app.route('/api/camiones', methods=['GET'])
def get_camiones():
    with get_db() as conn:
        camiones = conn.execute('SELECT * FROM camiones').fetchall()
        return jsonify([dict(row) for row in camiones])

@app.route('/api/camiones', methods=['POST'])
def add_camion():
    data = request.json
    required_fields = ['año', 'marca', 'modelo', 'vin', 'placa', 
'dueño']
    if not all(data.get(field) for field in required_fields):
        return jsonify({"message": "Todos los campos son 
obligatorios"}), 400
    with get_db() as conn:
        existing = conn.execute('SELECT * FROM camiones WHERE placa 
= ? OR vin = ?',
                                (data['placa'], 
data['vin'])).fetchone()
        if existing:
            return jsonify({"message": "La placa o VIN ya existe"}), 
409
        cursor = conn.execute('INSERT INTO camiones (año, marca, 
modelo, vin, placa, dueño) VALUES (?, ?, ?, ?, ?, ?)',
                              (data['año'], data['marca'], 
data['modelo'], data['vin'], data['placa'], data['dueño']))
        conn.commit()
        data['id'] = cursor.lastrowid
    return jsonify({"message": "Camión agregado", "camion": data}), 
201

@app.route('/api/camiones/<int:id>', methods=['DELETE'])
def delete_camion(id):
    with get_db() as conn:
        cursor = conn.execute('DELETE FROM camiones WHERE id = ?', 
(id,))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"message": "Camión no encontrado"}), 404
        return jsonify({"message": "Camión eliminado"}), 200

@app.route('/api/camiones/<int:id>', methods=['PUT'])
def update_camion(id):
    data = request.json
    required_fields = ['año', 'marca', 'modelo', 'vin', 'placa', 
'dueño']
    if not all(data.get(field) for field in required_fields):
        return jsonify({"message": "Todos los campos son 
obligatorios"}), 400
    with get_db() as conn:
        existing = conn.execute('SELECT * FROM camiones WHERE (placa 
= ? OR vin = ?) AND id != ?',
                                (data['placa'], data['vin'], 
id)).fetchone()
        if existing:
            return jsonify({"message": "La placa o VIN ya existe"}), 
409
        cursor = conn.execute('UPDATE camiones SET año = ?, marca = 
?, modelo = ?, vin = ?, placa = ?, dueño = ? WHERE id = ?',
                              (data['año'], data['marca'], 
data['modelo'], data['vin'], data['placa'], data['dueño'], id))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"message": "Camión no encontrado"}), 404
        return jsonify({"message": "Camión actualizado", "camion": 
{**data, "id": id}}), 200

if __name__ == '__main__':
    app.run(debug=True)
