from db import get_db_connection

def get_images(id_nv):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = "SELECT IMAGE_TOP, IMAGE_BOTTOM, IMAGE_LEFT, IMAGE_RIGHT, IMAGE_BETWEEN FROM IMAGE_BASE64_NV WHERE ID_NV = %s"
    cursor.execute(query, (id_nv,))
    result = cursor.fetchone()

    cursor.close()
    connection.close()

    if result:
        return {
            'image_top': result['IMAGE_TOP'],
            'image_bottom': result['IMAGE_BOTTOM'],
            'image_left': result['IMAGE_LEFT'],
            'image_right': result['IMAGE_RIGHT'],
            'image_between': result['IMAGE_BETWEEN']
        }
    else:
        return None