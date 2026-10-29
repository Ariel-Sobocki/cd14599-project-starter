# This module contains the OrderTracker class, which encapsulates the core
# business logic for managing orders.

VALID_STATUSES = ("pending", "processing", "shipped")


class OrderNotFoundError(ValueError):
    """Raised when an operation targets an order that does not exist."""


class OrderTracker:
    """
    Manages customer orders, providing functionalities to add, update,
    and retrieve order information.
    """
    def __init__(self, storage):
        required_methods = ['save_order', 'get_order', 'get_all_orders']
        for method in required_methods:
            if not hasattr(storage, method) or not callable(getattr(storage, method)):
                raise TypeError(f"Storage object must implement a callable '{method}' method.")
        self.storage = storage

    def add_order(self, order_id: str, item_name: str, quantity: int, customer_id: str, status: str = "pending"):
        self._validate_status(status)
        if self.storage.get_order(order_id):
            raise ValueError(f"Order with ID '{order_id}' already exists.")
        order = {
            "order_id": order_id,
            "item_name": item_name,
            "quantity": quantity,
            "customer_id": customer_id,
            "status": status
        }
        self.storage.save_order(order_id, order)

    def get_order_by_id(self, order_id: str):
        return self.storage.get_order(order_id)

    def update_order_status(self, order_id: str, new_status: str):
        order = self.get_order_by_id(order_id)
        if not order:
            raise OrderNotFoundError(f"Order with ID '{order_id}' does not exist.")
        self._validate_status(new_status)
        order["status"] = new_status
        self.storage.save_order(order_id, order)
        return order

    def list_all_orders(self):
        return list(self.storage.get_all_orders().values())

    def list_orders_by_status(self, status: str):
        result = []
        for order in self.list_all_orders():
            if order["status"] == status:
                result.append(order)
        return result

    def _validate_status(self, status: str):
        if status not in VALID_STATUSES:
            raise ValueError(f"Invalid status '{status}'. Valid statuses are: {', '.join(VALID_STATUSES)}.")
