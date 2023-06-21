from flask import Flask, request, render_template
from pymongo import MongoClient

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["ecommerce"]
products_collection = db["products"]
orders_collection = db["orders"]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/add_product", methods=["POST"])
def add_product():
    name = request.form.get("name")
    price = float(request.form.get("price"))
    quantity = int(request.form.get("quantity"))

    product = {
        "name": name,
        "price": price,
        "quantity": quantity
    }
    products_collection.insert_one(product)
    return "Product added successfully."


@app.route("/update_product_quantity", methods=["POST"])
def update_product_quantity():
    name = request.form.get("name")
    quantity_change = int(request.form.get("quantity_change"))

    product = products_collection.find_one({"name": name})
    if product:
        new_quantity = product["quantity"] + quantity_change
        if new_quantity >= 0:
            products_collection.update_one({"name": name}, {"$set": {"quantity": new_quantity}})
            return "Product quantity updated successfully."
        else:
            return "Error: Quantity cannot be negative."
    else:
        return "Error: Product not found."


@app.route("/get_product_details", methods=["GET"])
def get_product_details():
    name = request.args.get("name")

    product = products_collection.find_one({"name": name})
    if product:
        return f"Product Name: {product['name']}\nPrice: {product['price']}\nQuantity: {product['quantity']}"
    else:
        return "Error: Product not found."


@app.route("/place_order", methods=["POST"])
def place_order():
    customer_name = request.form.get("customer_name")
    product_name = request.form.get("product_name")
    quantity = int(request.form.get("quantity"))

    product = products_collection.find_one({"name": product_name})
    if product:
        if product["quantity"] >= quantity:
            order = {
                "customer_name": customer_name,
                "product_name": product_name,
                "quantity": quantity
            }
            orders_collection.insert_one(order)
            new_quantity = product["quantity"] - quantity
            products_collection.update_one({"name": product_name}, {"$set": {"quantity": new_quantity}})
            return "Order placed successfully."
        else:
            return "Error: Ordered quantity is more than available quantity."
    else:
        return "Error: Product not found."


@app.route("/generate_sales_report", methods=["GET"])
def generate_sales_report():
    pipeline = [
        {"$group": {"_id": "$product_name", "total_sales": {"$sum": "$quantity"}}}
    ]
    sales_report = orders_collection.aggregate(pipeline)
    report = "Sales Report:\n"
    for item in sales_report:
        report += f"Product: {item['_id']}\n\nTotal Sales: {item['total_sales']}\n\n"
    return report


if __name__ == "__main__":
    app.run(debug=True)
