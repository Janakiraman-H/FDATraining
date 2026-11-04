from flask import Flask, request, jsonify, send_from_directory
from backend.order_tracker import (
    OrderTracker,
    OrderAlreadyExistsError,
    OrderNotFoundError,
    InvalidStatusError,
    InvalidOrderDataError,
)
from backend.in_memory_storage import InMemoryStorage

app = Flask(__name__, static_folder='../frontend')
in_memory_storage = InMemoryStorage()
order_tracker = OrderTracker(in_memory_storage)


@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)


@app.route('/api/orders', methods=['POST'])
def add_order_api():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be a valid JSON object."}), 400

    order_id = data.get("order_id")
    item_name = data.get("item_name")
    quantity = data.get("quantity")
    customer_id = data.get("customer_id")
    status = data.get("status")
    if status is None:
        status = "pending"

    try:
        new_order = order_tracker.add_order(
            order_id=order_id,
            item_name=item_name,
            quantity=quantity,
            customer_id=customer_id,
            status=status,
        )
        return jsonify(new_order), 201
    except OrderAlreadyExistsError as e:
        return jsonify({"error": str(e)}), 409
    except (InvalidOrderDataError, InvalidStatusError, ValueError, TypeError) as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/orders/<string:order_id>', methods=['GET'])
def get_order_api(order_id):
    order = order_tracker.get_order_by_id(order_id)
    if not order:
        return jsonify({"error": f"Order with ID '{order_id}' not found."}), 404
    return jsonify(order), 200


@app.route('/api/orders/<string:order_id>/status', methods=['PUT'])
def update_order_status_api(order_id):
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or "new_status" not in data:
        return jsonify({"error": "Field 'new_status' is required in request body."}), 400

    new_status = data.get("new_status")

    try:
        updated_order = order_tracker.update_order_status(order_id, new_status)
        return jsonify(updated_order), 200
    except OrderNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except (InvalidStatusError, ValueError) as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/orders', methods=['GET'])
def list_orders_api():
    status = request.args.get('status')
    if status:
        try:
            orders = order_tracker.list_orders_by_status(status)
        except (InvalidStatusError, ValueError) as e:
            return jsonify({"error": str(e)}), 400
    else:
        orders = order_tracker.list_all_orders()
    return jsonify(orders), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
