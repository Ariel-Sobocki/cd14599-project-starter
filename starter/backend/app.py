from flask import Flask, request, jsonify, send_from_directory
from backend.order_tracker import OrderTracker, OrderNotFoundError
from backend.in_memory_storage import InMemoryStorage

app = Flask(__name__, static_folder='../frontend')
in_memory_storage = InMemoryStorage()
order_tracker = OrderTracker(in_memory_storage)

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

def get_json_body(required_fields):
    """Returns (data, None) if the body is a JSON object with all required fields, else (None, error response)."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None, (jsonify({"error": "Request body must be a JSON object."}), 400)
    missing = [field for field in required_fields if field not in data]
    if missing:
        return None, (jsonify({"error": f"Missing required field(s): {', '.join(missing)}."}), 400)
    return data, None

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/api/orders', methods=['POST'])
def add_order_api():
    data, error = get_json_body(["order_id", "item_name", "quantity", "customer_id"])
    if error:
        return error
    try:
        order_tracker.add_order(
            data["order_id"],
            data["item_name"],
            data["quantity"],
            data["customer_id"],
            data.get("status", "pending")
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify(order_tracker.get_order_by_id(data["order_id"])), 201

@app.route('/api/orders/<string:order_id>', methods=['GET'])
def get_order_api(order_id):
    order = order_tracker.get_order_by_id(order_id)
    if order is None:
        return jsonify({"error": f"Order with ID '{order_id}' not found."}), 404
    return jsonify(order), 200

@app.route('/api/orders/<string:order_id>/status', methods=['PUT'])
def update_order_status_api(order_id):
    data, error = get_json_body(["new_status"])
    if error:
        return error
    try:
        updated_order = order_tracker.update_order_status(order_id, data["new_status"])
    except OrderNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify(updated_order), 200

@app.route('/api/orders', methods=['GET'])
def list_orders_api():
    status = request.args.get("status")
    if status:
        orders = order_tracker.list_orders_by_status(status)
    else:
        orders = order_tracker.list_all_orders()
    return jsonify(orders), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
