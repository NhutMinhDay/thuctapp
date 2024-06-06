# thoigian_diemdanh.py
from flask import Blueprint, request, jsonify
from db import get_db_connection

thoigian_diemdanh = Blueprint('thoigian_diemdanh', __name__)

@thoigian_diemdanh.route('/api/thoigian_diemdanh', methods=['GET'])
def get_entries():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT * FROM THOIGIAN_DIEMDANH')
    entries = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(entries)

@thoigian_diemdanh.route('/api/thoigian_diemdanh', methods=['POST'])
def add_entry():
    new_entry = request.json
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute(
        'INSERT INTO THOIGIAN_DIEMDANH (DD_SANGDAU, DD_SANGCUOI, DD_CHIEUDAU, DD_CHIEUCUOI) VALUES (%s, %s, %s, %s)',
        (new_entry['DD_SANGDAU'], new_entry['DD_SANGCUOI'], new_entry['DD_CHIEUDAU'], new_entry['DD_CHIEUCUOI'])
    )
    db.commit()
    cursor.close()
    db.close()
    return jsonify(new_entry), 201


@thoigian_diemdanh.route('/api/thoigian_diemdanh/<id>', methods=['PUT'])
def update_entry(id):
    updated_entry = request.json
    db = get_db_connection()
    cursor = db.cursor()
    print("ID for update:", id)

    cursor.execute(
        'UPDATE THOIGIAN_DIEMDANH SET DD_SANGDAU = %s, DD_SANGCUOI = %s, DD_CHIEUDAU = %s, DD_CHIEUCUOI = %s WHERE ID_TGDD = %s',
        (updated_entry['DD_SANGDAU'], updated_entry['DD_SANGCUOI'], updated_entry['DD_CHIEUDAU'], updated_entry['DD_CHIEUCUOI'], id)
    )
    
    db.commit()
    cursor.close()
    db.close()
    return jsonify(updated_entry)


@thoigian_diemdanh.route('/api/thoigian_diemdanh/<id>', methods=['DELETE'])
def delete_entry(id):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute('DELETE FROM THOIGIAN_DIEMDANH WHERE ID_TGDD = %s', (id,))
    db.commit()
    cursor.close()
    db.close()
    return '', 204
