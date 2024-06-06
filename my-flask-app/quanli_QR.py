from flask import Blueprint, request, jsonify
from db import get_db_connection

qr_nv = Blueprint('qr_nv', __name__)

@qr_nv.route('/api/qr_nv', methods=['GET'])
def get_qr_entries():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT * FROM QR_NV')
    entries = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(entries)

@qr_nv.route('/api/qr_nv', methods=['POST'])
def add_qr_entry():
    new_entry = request.json
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute(
        'INSERT INTO QR_NV (ANH_QR) VALUES (%s)',
        (new_entry['ANH_QR'],)
    )
    db.commit()
    new_entry_id = cursor.lastrowid
    cursor.close()
    db.close()
    return jsonify({"MA_QR": new_entry_id, "ANH_QR": new_entry['ANH_QR']}), 201

@qr_nv.route('/api/qr_nv/<int:id>', methods=['PUT'])
def update_qr_entry(id):
    updated_entry = request.json
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute(
        'UPDATE QR_NV SET ANH_QR = %s WHERE MA_QR = %s',
        (updated_entry['ANH_QR'], id)
    )
    db.commit()
    cursor.close()
    db.close()
    return jsonify(updated_entry)

@qr_nv.route('/api/qr_nv/<int:id>', methods=['DELETE'])
def delete_qr_entry(id):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute('DELETE FROM QR_NV WHERE MA_QR = %s', (id,))
    db.commit()
    cursor.close()
    db.close()
    return '', 204
