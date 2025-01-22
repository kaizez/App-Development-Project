import shelve
from datetime import datetime

class Order:
    def __init__(self, order_id, items, total, customer_info, order_date, rental_dates=None):
        self.order_id = order_id
        self.items = items
        self.total = total
        self.customer_info = customer_info
        self.order_date = order_date
        self.rental_dates = rental_dates if rental_dates is not None else {}

    def get_order_id(self):
        return self.order_id

    def get_items(self):
        return self.items

    def get_total(self):
        return self.total

    def get_customer_info(self):
        return self.customer_info

    def get_order_date(self):
        return self.order_date
        
    def get_rental_dates(self):
        return self.rental_dates

class Product:
    def __init__(self, product_id, name, price, description, image="default.jpg"):
        self.__product_id = product_id
        self.__name = name
        self.__price = price
        self.__description = description
        self.__image = image

    def get_product_id(self):
        return self.__product_id

    def get_name(self):
        return self.__name

    def get_price(self):
        return self.__price

    def get_description(self):
        return self.__description

    def get_image(self):
        return self.__image

if __name__ == "__main__":
    try:
        with shelve.open('orders.db', 'r') as db:
            orders = db.get('orders', {})
            if not orders:
                print("No orders found.")
            else:
                for order_id, order in orders.items():
                    print("\nOrder Details:")
                    print(f"Order ID: {order.get_order_id()}")
                    print(f"Order Date: {order.get_order_date()}")
                    print(f"Total: ${order.get_total():.2f}")
                    
                    if order.get_rental_dates():
                        print("Rental Information:")
                        rental_dates = order.get_rental_dates()
                        print(f"  Start Date: {rental_dates['start_date']}")
                        print(f"  End Date: {rental_dates['end_date']}")
                        print(f"  Duration: {rental_dates['days']} days")
                    
                    print("Customer Information:")
                    customer_info = order.get_customer_info()
                    print(f"  Full Name: {customer_info['full_name']}")
                    print(f"  Email: {customer_info['email']}")
                    print(f"  Address: {customer_info['address']}")
                    print(f"  City: {customer_info['city']}")
                    print(f"  Postal Code: {customer_info['postal_code']}")
                    
                    print("Order Items:")
                    for item_id, item in order.get_items().items():
                        product = item['product']
                        quantity = item['quantity']
                        print(f"  - Product: {product.get_name()}")
                        print(f"    Quantity: {quantity}")
                        print(f"    Price per Item: ${product.get_price():.2f}")
                        print(f"    Subtotal: ${product.get_price() * quantity:.2f}")
    except Exception as e:
        print(f"Error: {e}")