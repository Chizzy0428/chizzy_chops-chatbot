import mysql.connector

cnx = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="root",
    password="Chi0428@zaram",
    database="chizzy_chops"
)

def insert_order_item(food_item, quantity, order_id):
    cursor = cnx.cursor()
    cursor.execute("SELECT item_id FROM food_items WHERE name = %s", (food_item,))
    result = cursor.fetchone()
    if not result:
        print(f"{food_item} not found.")
        return -1

    item_id = result[0]
    cursor.execute("INSERT INTO orders (order_id, item_id, quantity) VALUES (%s, %s, %s)",
                   (order_id, item_id, quantity))
    cnx.commit()
    cursor.close()
    return 1

def insert_order_tracking(order_id, status):
    cursor = cnx.cursor()
    cursor.execute("INSERT INTO order_tracking (order_id, status) VALUES (%s, %s)", (order_id, status))
    cnx.commit()
    cursor.close()

def get_total_order_price(order_id):
    cursor = cnx.cursor()
    query = """
        SELECT SUM(fi.price * o.quantity)
        FROM orders o
        JOIN food_items fi ON o.item_id = fi.item_id
        WHERE o.order_id = %s
    """
    cursor.execute(query, (order_id,))
    result = cursor.fetchone()[0]
    cursor.close()
    return result or 0

def get_next_order_id():
    cursor = cnx.cursor()
    cursor.execute("SELECT MAX(order_id) FROM orders")
    result = cursor.fetchone()[0]
    cursor.close()
    return 1 if result is None else result + 1

def get_order_status(order_id):
    cursor = cnx.cursor()
    cursor.execute("SELECT status FROM order_tracking WHERE order_id = %s", (order_id,))
    result = cursor.fetchone()
    cursor.close()
    return result[0] if result else None
