import pytest
from unittest.mock import Mock
from ..order_tracker import (
    OrderTracker,
    OrderAlreadyExistsError,
    OrderNotFoundError,
    InvalidStatusError,
    InvalidOrderDataError,
)

# --- Fixtures for Unit Tests ---

@pytest.fixture
def mock_storage():
    """
    Provides a mock storage object for tests.
    This mock will be configured to simulate various storage behaviors.
    """
    mock = Mock()
    # By default, mock get_order to return None (no order found)
    mock.get_order.return_value = None
    # By default, mock get_all_orders to return an empty dict
    mock.get_all_orders.return_value = {}
    return mock

@pytest.fixture
def order_tracker(mock_storage):
    """
    Provides an OrderTracker instance initialized with the mock_storage.
    """
    return OrderTracker(mock_storage)



# Unit Tests for add_order
def test_add_order_successfully_default_status(order_tracker, mock_storage):
    order = order_tracker.add_order("ORD001", "Laptop", 1, "CUST001")

    expected_order = {
        "order_id": "ORD001",
        "item_name": "Laptop",
        "quantity": 1,
        "customer_id": "CUST001",
        "status": "pending",
    }
    mock_storage.save_order.assert_called_once_with("ORD001", expected_order)
    assert order == expected_order


def test_add_order_with_custom_valid_status(order_tracker, mock_storage):
    order = order_tracker.add_order("ORD002", "Mouse", 2, "CUST002", status="processing")

    expected_order = {
        "order_id": "ORD002",
        "item_name": "Mouse",
        "quantity": 2,
        "customer_id": "CUST002",
        "status": "processing",
    }
    mock_storage.save_order.assert_called_once_with("ORD002", expected_order)
    assert order == expected_order


def test_add_order_raises_error_if_exists(order_tracker, mock_storage):
    mock_storage.get_order.return_value = {
        "order_id": "ORD_EXISTING",
        "item_name": "Old Item",
        "quantity": 1,
        "customer_id": "CUST001",
        "status": "pending",
    }

    with pytest.raises(ValueError, match="Order with ID 'ORD_EXISTING' already exists."):
        order_tracker.add_order("ORD_EXISTING", "New Item", 1, "CUST001")

    mock_storage.save_order.assert_not_called()


@pytest.mark.parametrize(
    "order_id,item_name,quantity,customer_id",
    [
        ("", "Laptop", 1, "CUST001"),          # empty order_id
        (None, "Laptop", 1, "CUST001"),        # None order_id
        ("ORD001", "", 1, "CUST001"),          # empty item_name
        ("ORD001", None, 1, "CUST001"),        # None item_name
        ("ORD001", "Laptop", 0, "CUST001"),    # zero quantity
        ("ORD001", "Laptop", -5, "CUST001"),   # negative quantity
        ("ORD001", "Laptop", "one", "CUST001"),# non-integer quantity
        ("ORD001", "Laptop", 1, ""),           # empty customer_id
        ("ORD001", "Laptop", 1, None),         # None customer_id
    ],
)
def test_add_order_raises_error_on_missing_or_invalid_fields(
    order_tracker, mock_storage, order_id, item_name, quantity, customer_id
):
    with pytest.raises(ValueError):
        order_tracker.add_order(order_id, item_name, quantity, customer_id)

    mock_storage.save_order.assert_not_called()


def test_add_order_raises_error_on_invalid_status(order_tracker, mock_storage):
    with pytest.raises(ValueError, match="Invalid status 'unsupported_status'"):
        order_tracker.add_order("ORD003", "Keyboard", 1, "CUST003", status="unsupported_status")

    mock_storage.save_order.assert_not_called()



# Unit Tests for get_order_by_id
def test_get_order_by_id_existing(order_tracker, mock_storage):
    stored_order = {
        "order_id": "ORD100",
        "item_name": "Monitor",
        "quantity": 1,
        "customer_id": "CUST100",
        "status": "pending",
    }
    mock_storage.get_order.return_value = stored_order

    result = order_tracker.get_order_by_id("ORD100")

    mock_storage.get_order.assert_called_once_with("ORD100")
    assert result == stored_order


def test_get_order_by_id_nonexistent(order_tracker, mock_storage):
    mock_storage.get_order.return_value = None

    result = order_tracker.get_order_by_id("NONEXISTENT_ID")

    mock_storage.get_order.assert_called_once_with("NONEXISTENT_ID")
    assert result is None


def test_get_order_by_id_invalid_or_empty(order_tracker, mock_storage):
    assert order_tracker.get_order_by_id("") is None
    assert order_tracker.get_order_by_id(None) is None
    mock_storage.get_order.assert_not_called()



# Unit Tests for update_order_status
def test_update_order_status_success(order_tracker, mock_storage):
    existing_order = {
        "order_id": "ORD200",
        "item_name": "Tablet",
        "quantity": 1,
        "customer_id": "CUST200",
        "status": "pending",
    }
    mock_storage.get_order.return_value = existing_order

    updated = order_tracker.update_order_status("ORD200", "shipped")

    expected_order = {
        "order_id": "ORD200",
        "item_name": "Tablet",
        "quantity": 1,
        "customer_id": "CUST200",
        "status": "shipped",
    }
    mock_storage.save_order.assert_called_once_with("ORD200", expected_order)
    assert updated["status"] == "shipped"


def test_update_order_status_does_not_mutate_original_dict(order_tracker, mock_storage):
    original_order = {
        "order_id": "ORD200",
        "item_name": "Tablet",
        "quantity": 1,
        "customer_id": "CUST200",
        "status": "pending",
    }
    mock_storage.get_order.return_value = original_order

    updated = order_tracker.update_order_status("ORD200", "shipped")

    assert original_order["status"] == "pending"
    assert updated["status"] == "shipped"
    assert updated is not original_order


def test_update_order_status_invalid_status(order_tracker, mock_storage):
    existing_order = {
        "order_id": "ORD200",
        "item_name": "Tablet",
        "quantity": 1,
        "customer_id": "CUST200",
        "status": "pending",
    }
    mock_storage.get_order.return_value = existing_order

    with pytest.raises(ValueError, match="Invalid status 'returned'"):
        order_tracker.update_order_status("ORD200", "returned")

    mock_storage.save_order.assert_not_called()


def test_update_order_status_nonexistent_order_id(order_tracker, mock_storage):
    mock_storage.get_order.return_value = None

    with pytest.raises(OrderNotFoundError):
        order_tracker.update_order_status("UNKNOWN_ORD", "shipped")

    mock_storage.save_order.assert_not_called()


@pytest.mark.parametrize("invalid_id", ["", None, "   "])
def test_update_order_status_empty_order_id(order_tracker, mock_storage, invalid_id):
    with pytest.raises(OrderNotFoundError):
        order_tracker.update_order_status(invalid_id, "shipped")

    mock_storage.save_order.assert_not_called()



# Unit Tests for list_all_orders and list_orders_by_status
def test_list_all_orders_empty_storage(order_tracker, mock_storage):
    mock_storage.get_all_orders.return_value = {}

    result = order_tracker.list_all_orders()

    mock_storage.get_all_orders.assert_called_once()
    assert result == []


def test_list_all_orders_with_data(order_tracker, mock_storage):
    orders_data = {
        "O1": {"order_id": "O1", "item_name": "A", "quantity": 1, "customer_id": "C1", "status": "pending"},
        "O2": {"order_id": "O2", "item_name": "B", "quantity": 2, "customer_id": "C2", "status": "shipped"},
    }
    mock_storage.get_all_orders.return_value = orders_data

    result = order_tracker.list_all_orders()

    assert len(result) == 2
    assert orders_data["O1"] in result
    assert orders_data["O2"] in result


def test_list_orders_by_status_empty_storage(order_tracker, mock_storage):
    mock_storage.get_all_orders.return_value = {}

    result = order_tracker.list_orders_by_status("pending")

    assert result == []


def test_list_orders_by_status_filtering_accuracy(order_tracker, mock_storage):
    orders_data = {
        "O1": {"order_id": "O1", "item_name": "A", "quantity": 1, "customer_id": "C1", "status": "pending"},
        "O2": {"order_id": "O2", "item_name": "B", "quantity": 2, "customer_id": "C2", "status": "shipped"},
        "O3": {"order_id": "O3", "item_name": "C", "quantity": 3, "customer_id": "C3", "status": "pending"},
    }
    mock_storage.get_all_orders.return_value = orders_data

    pending_orders = order_tracker.list_orders_by_status("pending")
    assert len(pending_orders) == 2
    assert all(o["status"] == "pending" for o in pending_orders)

    shipped_orders = order_tracker.list_orders_by_status("shipped")
    assert len(shipped_orders) == 1
    assert shipped_orders[0]["order_id"] == "O2"


def test_list_orders_by_status_no_matches(order_tracker, mock_storage):
    orders_data = {
        "O1": {"order_id": "O1", "item_name": "A", "quantity": 1, "customer_id": "C1", "status": "pending"},
    }
    mock_storage.get_all_orders.return_value = orders_data

    result = order_tracker.list_orders_by_status("processing")
    assert result == []


def test_list_orders_by_status_invalid_status(order_tracker, mock_storage):
    with pytest.raises(InvalidStatusError, match="Invalid status 'unsupported'"):
        order_tracker.list_orders_by_status("unsupported")

    mock_storage.get_all_orders.assert_not_called()


def test_order_tracker_init_sets_storage():
    dummy_storage = object()
    tracker = OrderTracker(dummy_storage)
    assert tracker.storage is dummy_storage




