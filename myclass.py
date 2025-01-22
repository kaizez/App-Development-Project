
# Define the Order class
class Order:
    """Class to represent an order"""
    def __init__(self, order_id, items, total, customer_info, order_date, rental_dates=None):
        """Initialize the order"""
        self.order_id = order_id  # Changed from private to public
        self.items = items
        self.total = total
        self.customer_info = customer_info
        self.order_date = order_date
        self.rental_dates = rental_dates if rental_dates is not None else {}

    def get_order_id(self):
        """Get the order id"""
        return self.order_id

    def get_items(self):
        """Get the order items"""
        return self.items

    def get_total(self):
        """Get the order total"""
        return self.total

    def get_customer_info(self):
        """Get the customer information"""
        return self.customer_info

    def get_order_date(self):
        """Get the order date"""
        return self.order_date
    
    def get_rental_dates(self):
        """Get the rental dates"""
        return self.rental_dates
    
class Product:
    """Class to represent a product"""
    def __init__(self, product_id, name, price, description, stock, image="default.jpg"):
        """Initialize the product"""
        self.__product_id = product_id
        self.__name = name
        self.__price = price
        self.__description = description
        self.__image = image
        self.__stock = stock  # Total bikes we have
        self.__rental = 0 

    def get_product_id(self):
        """Get the product id"""
        return self.__product_id

    def get_name(self):
        """Get the product name"""
        return self.__name

    def get_price(self):
        """Get the product price"""
        return self.__price

    def get_description(self):
        """Get the product description"""
        return self.__description

    def get_image(self):
        """Get the product image"""
        return self.__image

    def get_stock(self):
        """Get total stock"""
        return self.__stock

    def get_stock(self):
        """Get total stock"""
        return self.__stock

    def get_rental(self):
        """Get number of rentals"""
        return self.__rental

    def increase_rental(self):
        """Increase rental count when bike is unlocked"""
        if self.__stock > 0:
            self.__stock -= 1
            self.__rental += 1
            return True
        return False

    def decrease_rental(self):
        """Decrease rental count when bike is locked"""
        if self.__rental > 0:
            self.__rental -= 1
            self.__stock += 1
            return True
        return False
    
class BikeID:
    def __init__(self, id_string, bike_name, status="available"):
        self.__id = id_string
        self.__bike_name = bike_name
        self.__current_user = None  # Track who has unlocked the bike

    def get_id(self):
        return self.__id

    def get_bike_name(self):
        return self.__bike_name

    def get_current_user(self):
        return self.__current_user

    def unlock_bike(self, user_email):
        """Unlock the bike and assign it to a user"""
        if self.__status == 'available':
            self.__status = 'unlocked'
            self.__current_user = user_email
            return True
        return False

    def return_bike(self):
        """Return the bike to available status"""
        if self.__status == 'unlocked':
            self.__status = 'available'
            self.__current_user = None
            return True
        return False
        
carparks = {
    1: ["Orchard Central Carpark", 1.3016, 103.8396],
    2: ["ION Orchard Carpark", 1.3040, 103.8318],
    3: ["Marina Bay Sands Carpark", 1.2833, 103.8606],
    4: ["Gardens by the Bay Carpark", 1.2816, 103.8636],
    5: ["VivoCity Carpark", 1.2646, 103.8238],
    6: ["Yio Chu Kang MRT Carpark", 1.3812, 103.8444],
    7: ["Toa Payoh Central Carpark", 1.3324, 103.8484],
    8: ["Bishan Junction 8 Carpark", 1.3508, 103.8485],
    9: ["Yishun MRT Carpark", 1.4291, 103.8357],
    10: ["Khatib MRT Carpark", 1.4172, 103.8335],
    11: ["HDB Carpark Blk 570 Ang Mo Kio Ave 3", 1.3725, 103.8498],
    12: ["HDB Carpark Blk 562 Ang Mo Kio Ave 3", 1.3723, 103.8490],
    13: ["HDB Carpark Blk 550 Ang Mo Kio Ave 3", 1.3717, 103.8501],
    14: ["HDB Carpark Blk 547 Ang Mo Kio Ave 10", 1.3720, 103.8507],
    15: ["HDB Carpark Blk 501 Ang Mo Kio Ave 3", 1.3734, 103.8516],
    16: ["HDB Carpark Blk 556 Ang Mo Kio Ave 3", 1.3729, 103.8493],
    17: ["NYP Campus Carpark A", 1.3771, 103.8485],
    18: ["NYP Campus Carpark B", 1.3768, 103.8500],
    19: ["HDB Carpark Blk 511 Ang Mo Kio Ave 8", 1.3765, 103.8483],
    20: ["HDB Carpark Blk 544 Ang Mo Kio Ave 10", 1.3716, 103.8510],
    21: ["Plaza Singapura Carpark", 1.3009, 103.8451],
    22: ["Bugis Junction Carpark", 1.2990, 103.8550],
    23: ["Clarke Quay Central Carpark", 1.2885, 103.8486],
    24: ["East Coast Park Carpark", 1.3032, 103.9068],
    25: ["Tampines Mall Carpark", 1.3537, 103.9456],
    26: ["JCube Carpark", 1.3331, 103.7401],
    27: ["Bukit Panjang Plaza Carpark", 1.3782, 103.7642],
    28: ["IMM Building Carpark", 1.3342, 103.7463],
    29: ["City Square Mall Carpark", 1.3117, 103.8565],
    30: ["Paya Lebar Quarter Carpark", 1.3174, 103.8934]
}
