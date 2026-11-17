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
(paste your terminal output here, or add a screenshot)
```

## Libraries and techniques beyond class material

- **`decimal.Decimal`**: exact money calculations that avoid floating-point rounding errors. https://docs.python.org/3/library/decimal.html
- **f-string alignment (`ljust` / `rjust`)**: used to print the tables in aligned columns without an extra library. https://docs.python.org/3/library/stdtypes.html#str.ljust
