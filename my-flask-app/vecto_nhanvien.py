from flask import Blueprint, request, jsonify
from db import get_db_connection

vecto1 = Blueprint('vecto1', __name__)

@vecto1.route('/api/show', methods=['GET'])
def get_vecto():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT * FROM VECTO_ANH')
    entries = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(entries)
