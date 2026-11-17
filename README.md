# Customer Order Entry (Python + Supabase)

DATA 4000 — Python with AI · Fairfield University

A terminal program that creates new orders for existing customers. It shows customers and products from Supabase, validates the user's input, saves the order through the Supabase API, and then queries the database again to verify that the order was saved.

## Files

| File | Purpose |
|---|---|
| `order_entry.py` | Main program: displays tables, collects and validates input, confirms, saves and verifies orders |
| `database.py` | All Supabase API calls (load customers/products, look up a price, insert an order, retrieve an order) |
| `config.py` | Loads `SUPABASE_URL` and `SUPABASE_KEY` from `.env` |
| `requirements.txt` | Required packages |
| `.env.example` | Template for your credentials (placeholders only) |
| `.gitignore` | Keeps `.env` and other local files out of GitHub |

## Setup

1. Clone the repository and open the folder in VS Code.
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate        # Windows: .venv\Scripts\activate
   ```
3. Install the packages:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and fill in your Supabase project URL and secret key:
   ```
   SUPABASE_URL=https://your-project-ref.supabase.co
   SUPABASE_KEY=your-supabase-secret-key
   ```

The program expects the class tables `customers` (`customer_id`, `name`), `products` (`product_id`, `product_name`, `price`) and `orders` (`order_id`, `customer_id`, `product_id`, `quantity`, `order_date`, `unit_price`).

## How to run

```bash
python order_entry.py
```

## How it works

- **Display:** On startup, the program retrieves customers and products from Supabase and prints them as tables, with prices formatted to two decimal places.
- **Validation:** Each input has its own function that loops until the value is valid. `int()` inside `try/except ValueError` rejects text and decimals. IDs are checked against the records loaded from Supabase, and the quantity must be greater than zero.
- **Confirmation:** A summary shows the customer, product, quantity, current unit price and total. `Y`/`y` saves the order, `N`/`n` cancels it, and any other answer is asked again.
- **Saving:** The unit price is looked up in Supabase just before the summary, so the user never types a price. The insert sends `customer_id`, `product_id`, `quantity`, today's `order_date` and `unit_price`. The `order_id` is left out so the database generates it. A success message appears only after Supabase returns the inserted row.
- **Verification:** The program takes the new `order_id` from the insert response, runs a separate query for that order, and prints it in a table. The total is calculated from the stored `unit_price`. If that query fails or finds nothing, the program says verification could not be completed and does not insert the order again.
- **Errors:** API failures are caught and reported as "The order was NOT saved" with a short reason. Credentials are never printed.
- **Extra credit:** After each order or cancellation, the program asks whether to enter another order. All order details are local variables inside `create_order()`, so nothing carries over from one order to the next.

## Testing results

| Test | Input | Expected | Result |
|---|---|---|---|
| Text instead of customer ID | `hello` | Helpful message; asks again | |
| Customer ID that does not exist | `99` | Rejects; asks again | |
| Product ID that does not exist | `42` | Rejects; asks again | |
| Quantity 0 | `0` | Rejects; asks again | |
| Quantity -2 | `-2` | Rejects; asks again | |
| Quantity 1.5 | `1.5` | Rejects; asks again | |
| Quantity text | `hello` | Rejects; asks again | |
| Cancel at confirmation | `N` | No order inserted | |
| Confirm a valid order | `Y` | Exactly one order inserted | |
| Retrieve the new order | — | Saved order appears in verification table | |
| Extra credit: another order | `Y` then `N` | New order starts fresh; program exits on `N` | |

### Terminal output: successful insertion and verification

```
=== Campus Store Order Entry ===

CUSTOMERS
Customer ID | Customer Name
------------+--------------
          1 | Avery Morgan 
          2 | Jordan Patel 
          3 | Taylor Chen  
          4 | Casey Rivera 
          5 | Riley Brooks 
          6 | Morgan Lee   
          7 | Jamie Wilson 
          8 | Alex Kim     
          9 | Cameron Davis
         10 | Quinn Garcia 
         11 | Sam Parker   
         12 | Drew Johnson 
         13 | Skyler Reed  
         14 | Reese Martin 
         15 | Rowan Lewis  
         16 | Peyton Clark 
         17 | Finley Hall  
         18 | Emerson Young
         19 | Dakota Allen 
         20 | Harper Scott 

PRODUCTS
Product ID | Product Name   |  Price
-----------+----------------+-------
         1 | Notebook       |  $4.50
         2 | Pen Set        |  $6.00
         3 | Backpack       | $45.00
         4 | Water Bottle   | $18.00
         5 | Hoodie         | $39.00
         6 | T-Shirt        | $19.00
         7 | USB Drive      | $12.50
         8 | Wireless Mouse | $24.00
         9 | Desk Lamp      | $29.00
        10 | Coffee Mug     | $10.00
        11 | Planner        | $15.00
        12 | Laptop Stand   | $35.00

--- NEW ORDER ---
Enter the customer ID: hello          
  'hello' is not a valid customer ID. Please enter a whole number from the customer table.
Enter the customer ID: 99
  There is no customer with ID 99. Please choose an ID from the customertable.
Enter the customer ID: 1
Enter the product ID: 42
  There is no product with ID 42. Please choose an ID from the product table.
Enter the product ID: 7
Enter the quantity: 0
  Quantity must be greater than zero.
Enter the quantity: 2

ORDER SUMMARY
  Customer:   Avery Morgan
  Product:    USB Drive
  Quantity:   2
  Unit price: $12.50
  Total:      $25.00

Confirm this purchase? (Y/N): 3
  Please enter Y for yes or N for no.

Confirm this purchase? (Y/N): n
Order cancelled. Nothing was saved.

Would you like to enter another order? (Y/N): y

CUSTOMERS
Customer ID | Customer Name
------------+--------------
          1 | Avery Morgan 
          2 | Jordan Patel 
          3 | Taylor Chen  
          4 | Casey Rivera 
          5 | Riley Brooks 
          6 | Morgan Lee   
          7 | Jamie Wilson 
          8 | Alex Kim     
          9 | Cameron Davis
         10 | Quinn Garcia 
         11 | Sam Parker   
         12 | Drew Johnson 
         13 | Skyler Reed  
         14 | Reese Martin 
         15 | Rowan Lewis  
         16 | Peyton Clark 
         17 | Finley Hall  
         18 | Emerson Young
         19 | Dakota Allen 
         20 | Harper Scott 

PRODUCTS
Product ID | Product Name   |  Price
-----------+----------------+-------
         1 | Notebook       |  $4.50
         2 | Pen Set        |  $6.00
         3 | Backpack       | $45.00
         4 | Water Bottle   | $18.00
         5 | Hoodie         | $39.00
         6 | T-Shirt        | $19.00
         7 | USB Drive      | $12.50
         8 | Wireless Mouse | $24.00
         9 | Desk Lamp      | $29.00
        10 | Coffee Mug     | $10.00
        11 | Planner        | $15.00
        12 | Laptop Stand   | $35.00

--- NEW ORDER ---
Enter the customer ID: 4
Enter the product ID: 7
Enter the quantity: 6

ORDER SUMMARY
  Customer:   Casey Rivera
  Product:    USB Drive
  Quantity:   6
  Unit price: $12.50
  Total:      $75.00

Confirm this purchase? (Y/N): y

Success! Order 1002 was saved to Supabase.

VERIFIED ORDER (retrieved from Supabase)
Order ID | Customer     | Product   | Quantity | Unit Price |  Total | Order Date
---------+--------------+-----------+----------+------------+--------+-----------
    1002 | Casey Rivera | USB Drive |        6 |     $12.50 | $75.00 | 2026-11-17

Would you like to enter another order? (Y/N): n
Goodbye!
(.venv) clairecavanaugh@claires-air order-entry-cli % 

```

## Libraries and techniques beyond class material

- **`decimal.Decimal`**: exact money calculations that avoid floating-point rounding errors. https://docs.python.org/3/library/decimal.html
- **f-string alignment (`ljust` / `rjust`)**: used to print the tables in aligned columns without an extra library. https://docs.python.org/3/library/stdtypes.html#str.ljust
