import psycopg2
from faker import Faker
import random
from datetime import datetime, timedelta

# Initialize Faker
fake = Faker()

# Database connection
conn = psycopg2.connect(
    dbname="warehouse_db",
    user="warehouse_user",
    password="warehouse_password",
    host="db",
    port="5432"
)
cursor = conn.cursor()

# Generate products
products = []
categories = ['Electronics', 'Clothing', 'Home Goods', 'Toys', 'Food', 'Books']
for i in range(100):
    sku = f"SKU-{fake.unique.random_int(min=10000, max=99999)}"
    name = fake.word().capitalize() + ' ' + fake.word().capitalize()
    description = fake.sentence(nb_words=10)
    category = random.choice(categories)
    price = round(random.uniform(10, 1000), 2)
    created_at = fake.date_time_between(start_date='-1y', end_date='now')
    
    cursor.execute(
        "INSERT INTO products (sku, name, description, category, price, created_at) VALUES (%s, %s, %s, %s, %s, %s) RETURNING product_id",
        (sku, name, description, category, price, created_at)
    )
    product_id = cursor.fetchone()[0]
    products.append((product_id, price))

# Generate inventory
warehouses = ['North', 'South', 'East', 'West', 'Central']
for product_id, _ in products:
    quantity = random.randint(0, 1000)
    warehouse_location = random.choice(warehouses)
    last_updated = fake.date_time_between(start_date='-6m', end_date='now')
    
    cursor.execute(
        "INSERT INTO inventory (product_id, quantity, warehouse_location, last_updated) VALUES (%s, %s, %s, %s)",
        (product_id, quantity, warehouse_location, last_updated)
    )

# Generate orders and order items
for _ in range(500):
    customer_name = fake.name()
    order_date = fake.date_time_between(start_date='-1y', end_date='now')
    status = random.choice(['pending', 'processing', 'shipped', 'delivered', 'cancelled'])
    
    cursor.execute(
        "INSERT INTO orders (customer_name, order_date, status) VALUES (%s, %s, %s) RETURNING order_id",
        (customer_name, order_date, status)
    )
    order_id = cursor.fetchone()[0]
    
    # Add items to the order
    num_items = random.randint(1, 5)
    order_products = random.sample(products, num_items)
    
    for product_id, price in order_products:
        quantity = random.randint(1, 10)
        
        cursor.execute(
            "INSERT INTO order_items (order_id, product_id, quantity, price_per_unit) VALUES (%s, %s, %s, %s)",
            (order_id, product_id, quantity, price)
        )
    
    # Create shipment if order is shipped or delivered
    if status in ['shipped', 'delivered']:
        shipment_date = order_date + timedelta(days=random.randint(1, 5))
        carrier = random.choice(['FedEx', 'UPS', 'USPS', 'DHL'])
        tracking_number = fake.bothify(text='??###??######')
        shipment_status = 'delivered' if status == 'delivered' else 'in_transit'
        
        cursor.execute(
            "INSERT INTO shipments (order_id, shipment_date, carrier, tracking_number, status) VALUES (%s, %s, %s, %s, %s)",
            (order_id, shipment_date, carrier, tracking_number, shipment_status)
        )

# Commit changes and close connection
conn.commit()
cursor.close()
conn.close()

print("Mock data has been successfully generated!")
