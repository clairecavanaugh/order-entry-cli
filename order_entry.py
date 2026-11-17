"""
order_entry.py - Create and verify customer orders in Supabase.

Run with:  python order_entry.py

Flow for each order:
  1. Show customers and products (loaded from Supabase).
  2. Ask for a customer ID, product ID and quantity, re-asking until valid.
  3. Look up the product's CURRENT price in Supabase and show a summary.
  4. Ask the user to confirm (Y/N). N cancels without saving.
  5. Insert the order, then run a NEW query by its order_id to verify it.
  6. Ask whether to enter another order (extra credit).
"""

import sys
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

import database as db


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------
def money(value):
    """Convert a price to a Decimal rounded to cents (avoids float errors)."""
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def format_money(value):
    return f"${money(value):,.2f}"


def print_table(title, headers, rows, right_align=()):
    """Print rows as a table with column headings.

    right_align is a set of column numbers to right-align (numbers, prices).
    """
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))

    def format_row(cells):
        parts = []
        for i, cell in enumerate(cells):
            text = str(cell)
            parts.append(text.rjust(widths[i]) if i in right_align else text.ljust(widths[i]))
        return " | ".join(parts)

    print(f"\n{title}")
    print(format_row(headers))
    print("-+-".join("-" * w for w in widths))
    for row in rows:
        print(format_row(row))


def show_customers(customers):
    rows = [(c["customer_id"], c["name"]) for c in customers]
    print_table("CUSTOMERS", ["Customer ID", "Customer Name"], rows, right_align={0})


def show_products(products):
    rows = [(p["product_id"], p["product_name"], format_money(p["price"])) for p in products]
    print_table("PRODUCTS", ["Product ID", "Product Name", "Price"], rows, right_align={0, 2})


# ---------------------------------------------------------------------------
# Input validation - each function keeps asking until the input is valid
# ---------------------------------------------------------------------------
def ask_for_id(prompt, valid_records, label):
    """Ask for an integer ID that exists in valid_records (a dict keyed by ID)."""
    while True:
        text = input(prompt).strip()
        try:
            record_id = int(text)
        except ValueError:
            print(f"  '{text}' is not a valid {label} ID. Please enter a whole number "
                  f"from the {label} table.")
            continue
        if record_id not in valid_records:
            print(f"  There is no {label} with ID {record_id}. Please choose an ID "
                  f"from the {label} table.")
            continue
        return record_id


def ask_for_quantity():
    """Ask for a positive whole number (rejects text, 0, negatives, decimals)."""
    while True:
        text = input("Enter the quantity: ").strip()
        try:
            quantity = int(text)
        except ValueError:
            print(f"  '{text}' is not a whole number. Please enter a quantity such as 1, 2 or 3.")
            continue
        if quantity <= 0:
            print("  Quantity must be greater than zero.")
            continue
        return quantity


def ask_yes_no(prompt):
    """Return True for Y/y and False for N/n. Re-ask for anything else."""
    while True:
        answer = input(prompt).strip().upper()
        if answer == "Y":
            return True
        if answer == "N":
            return False
        print("  Please enter Y for yes or N for no.")


# ---------------------------------------------------------------------------
# Order steps
# ---------------------------------------------------------------------------
def show_summary(customer_name, product_name, quantity, unit_price):
    total = unit_price * quantity
    print("\nORDER SUMMARY")
    print(f"  Customer:   {customer_name}")
    print(f"  Product:    {product_name}")
    print(f"  Quantity:   {quantity}")
    print(f"  Unit price: {format_money(unit_price)}")
    print(f"  Total:      {format_money(total)}")


def verify_order(order_id, customers_by_id, products_by_id):
    """Query Supabase again for the saved order and display it."""
    try:
        saved = db.get_order(order_id)
    except db.DatabaseError as error:
        print(f"\nThe order was saved, but verification could not be completed. {error}")
        return
    if saved is None:
        print(f"\nThe order was saved, but order {order_id} could not be found "
              "when verifying. Verification could not be completed.")
        return

    unit_price = money(saved["unit_price"])  # use the STORED price
    total = unit_price * saved["quantity"]
    customer = customers_by_id.get(saved["customer_id"], {}).get(
        "name", f"ID {saved['customer_id']}")
    product = products_by_id.get(saved["product_id"], {}).get(
        "product_name", f"ID {saved['product_id']}")

    print_table(
        "VERIFIED ORDER (retrieved from Supabase)",
        ["Order ID", "Customer", "Product", "Quantity", "Unit Price", "Total", "Order Date"],
        [(saved["order_id"], customer, product, saved["quantity"],
          format_money(unit_price), format_money(total), saved["order_date"])],
        right_align={0, 3, 4, 5},
    )


def create_order(customers_by_id, products_by_id):
    """Run one complete order: input, confirm, save, verify.

    All order details are local variables, so nothing carries over
    from one order to the next.
    """
    print("\n--- NEW ORDER ---")
    customer_id = ask_for_id("Enter the customer ID: ", customers_by_id, "customer")
    product_id = ask_for_id("Enter the product ID: ", products_by_id, "product")
    quantity = ask_for_quantity()

    # Get the product's current price from the database (not from the user)
    try:
        product = db.get_product(product_id)
    except db.DatabaseError as error:
        print(f"\nThe order was NOT saved. {error}")
        return
    if product is None:
        print("\nThat product no longer exists. The order was NOT saved.")
        return
    unit_price = money(product["price"])

    show_summary(customers_by_id[customer_id]["name"], product["product_name"],
                 quantity, unit_price)

    if not ask_yes_no("\nConfirm this purchase? (Y/N): "):
        print("Order cancelled. Nothing was saved.")
        return

    new_order = {
        "customer_id": customer_id,
        "product_id": product_id,
        "quantity": quantity,
        "order_date": date.today().isoformat(),
        "unit_price": float(unit_price),
        # order_id is left out on purpose - the database generates it
    }
    try:
        saved = db.insert_order(new_order)
    except db.DatabaseError as error:
        print(f"\nThe order was NOT saved. {error}")
        return

    order_id = saved.get("order_id")
    print(f"\nSuccess! Order {order_id} was saved to Supabase.")
    verify_order(order_id, customers_by_id, products_by_id)


# ---------------------------------------------------------------------------
# Main program
# ---------------------------------------------------------------------------
def main():
    print("=== Campus Store Order Entry ===")
    try:
        customers = db.get_customers()
        products = db.get_products()
    except db.DatabaseError as error:
        print(f"Unable to start: {error}")
        sys.exit(1)

    # Dictionaries keyed by ID make it easy to check whether an ID exists
    customers_by_id = {c["customer_id"]: c for c in customers}
    products_by_id = {p["product_id"]: p for p in products}

    keep_going = True
    while keep_going:
        show_customers(customers)
        show_products(products)
        create_order(customers_by_id, products_by_id)
        keep_going = ask_yes_no("\nWould you like to enter another order? (Y/N): ")

    print("Goodbye!")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nProgram stopped by user. Goodbye!")
