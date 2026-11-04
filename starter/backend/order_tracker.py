# This module contains the OrderTracker class, which encapsulates the core
# business logic for managing orders.


class OrderTrackerError(Exception):
    pass


class OrderAlreadyExistsError(ValueError, OrderTrackerError):
    pass


class OrderNotFoundError(KeyError, ValueError, OrderTrackerError):
    def __str__(self):
        return self.args[0] if self.args else ""


class InvalidStatusError(ValueError, OrderTrackerError):
    pass


class InvalidOrderDataError(ValueError, OrderTrackerError):
    pass


class OrderTracker:
    VALID_STATUSES = {"pending", "processing", "shipped"}

    def __init__(self, storage):
        self.storage = storage

    def add_order(self, order_id: str, item_name: str, quantity: int, customer_id: str, status: str = "pending"):
        if not order_id or not isinstance(order_id, str) or not order_id.strip():
            raise InvalidOrderDataError("Order ID is required and must be a non-empty string.")
        if not item_name or not isinstance(item_name, str) or not item_name.strip():
            raise InvalidOrderDataError("Item name is required and must be a non-empty string.")
        if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity <= 0:
            raise InvalidOrderDataError("Quantity must be a positive integer.")
        if not customer_id or not isinstance(customer_id, str) or not customer_id.strip():
            raise InvalidOrderDataError("Customer ID is required and must be a non-empty string.")

        if status not in self.VALID_STATUSES:
            raise InvalidStatusError(
                f"Invalid status '{status}'. Valid statuses are: {', '.join(sorted(self.VALID_STATUSES))}."
            )

        if self.storage.get_order(order_id):
            raise OrderAlreadyExistsError(f"Order with ID '{order_id}' already exists.")

        order = {
            "order_id": order_id,
            "item_name": item_name,
            "quantity": quantity,
            "customer_id": customer_id,
            "status": status,
        }
        self.storage.save_order(order_id, order)
        return order

    def get_order_by_id(self, order_id: str):
        if not order_id or not isinstance(order_id, str):
            return None
        return self.storage.get_order(order_id)

    def update_order_status(self, order_id: str, new_status: str):
        if not order_id or not isinstance(order_id, str) or not order_id.strip():
            raise OrderNotFoundError("Order ID is required.")

        if new_status not in self.VALID_STATUSES:
            raise InvalidStatusError(
                f"Invalid status '{new_status}'. Valid statuses are: {', '.join(sorted(self.VALID_STATUSES))}."
            )

        order = self.storage.get_order(order_id)
        if not order:
            raise OrderNotFoundError(f"Order with ID '{order_id}' not found.")

        updated_order = order.copy()
        updated_order["status"] = new_status
        self.storage.save_order(order_id, updated_order)
        return updated_order

    def list_all_orders(self):
        orders_dict = self.storage.get_all_orders()
        return list(orders_dict.values())

    def list_orders_by_status(self, status: str):
        if status not in self.VALID_STATUSES:
            raise InvalidStatusError(
                f"Invalid status '{status}'. Valid statuses are: {', '.join(sorted(self.VALID_STATUSES))}."
            )
        orders_dict = self.storage.get_all_orders()
        return [order for order in orders_dict.values() if order.get("status") == status]
