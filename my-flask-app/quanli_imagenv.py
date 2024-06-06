from flask import Blueprint, request, jsonify
from db import get_db_connection

image_base64_nv = Blueprint('image_base64_nv', __name__)

@image_base64_nv.route('/api/image_base64_nv', methods=['GET'])
def get_images():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT * FROM IMAGE_BASE64_NV')
    images = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(images)

@image_base64_nv.route('/api/image_base64_nv', methods=['POST'])
def add_image():
    new_image = request.json
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute(
        'INSERT INTO IMAGE_BASE64_NV (ID_NV, IMAGE_TOP, IMAGE_BOTTOM, IMAGE_LEFT, IMAGE_RIGHT, IMAGE_BETWEEN) VALUES (%s, %s, %s, %s, %s, %s)',
        (new_image['ID_NV'], new_image['IMAGE_TOP'], new_image['IMAGE_BOTTOM'], 
         new_image['IMAGE_LEFT'], new_image['IMAGE_RIGHT'], new_image['IMAGE_BETWEEN'])
    )
    db.commit()
    new_image_id = cursor.lastrowid
    cursor.close()
    db.close()
    new_image['ID_IMAGE'] = new_image_id
    return jsonify(new_image), 201


@image_base64_nv.route('/api/nhanvien', methods=['GET'])
def get_nhanvien():
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute('SELECT ID_NV, TEN_NV FROM NHANVIEN')
    nhanvien_list = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(nhanvien_list)


@image_base64_nv.route('/api/image_base64_nv/<int:id>', methods=['PUT'])
def update_image(id):
    updated_image_data = request.json
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute(
        'UPDATE IMAGE_BASE64_NV SET ID_NV=%s, IMAGE_TOP=%s, IMAGE_BOTTOM=%s, IMAGE_LEFT=%s, IMAGE_RIGHT=%s, IMAGE_BETWEEN=%s WHERE ID_IMAGE=%s',
        (updated_image_data['ID_NV'], updated_image_data['IMAGE_TOP'], updated_image_data['IMAGE_BOTTOM'], 
         updated_image_data['IMAGE_LEFT'], updated_image_data['IMAGE_RIGHT'], 
         updated_image_data['IMAGE_BETWEEN'], id)
    )
    db.commit()
    cursor.close()
    db.close()
    return jsonify(updated_image_data), 200



@image_base64_nv.route('/api/image_base64_nv/<int:id>', methods=['DELETE'])
def delete_image(id):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute('DELETE FROM IMAGE_BASE64_NV WHERE ID_IMAGE = %s', (id,))
    db.commit()
    cursor.close()
    db.close()
    return '', 204


