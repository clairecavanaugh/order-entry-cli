"""
database.py - Every Supabase API call used by order_entry.py.

Each function raises DatabaseError with a friendly message if the request
fails, so the main program can explain the problem without crashing or
showing credentials.
"""

from supabase import create_client

from config import SUPABASE_KEY, SUPABASE_URL


class DatabaseError(Exception):
    """A Supabase request failed. The message is safe to print."""


_client = None


def get_client():
    """Create the Supabase client once and reuse it."""
    global _client
    if _client is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise DatabaseError(
                "Supabase credentials are missing. Copy .env.example to .env "
                "and fill in SUPABASE_URL and SUPABASE_KEY."
            )
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _client


def run_query(build_query, action):
    """Run a query and turn any failure into a safe DatabaseError.

    build_query is a function that receives the client and returns a query.
    """
    try:
        return build_query(get_client()).execute().data
    except DatabaseError:
        raise
    except Exception as exc:
        # Supabase's short explanation (e.g. "Invalid API key") never
        # contains the URL or the key, so it is safe to show.
        detail = getattr(exc, "message", None)
        detail = f" Supabase said: {detail}" if detail else ""
        raise DatabaseError(
            f"Could not {action}. ({type(exc).__name__}){detail}"
        ) from exc


def get_customers():
    """Return all customers, ordered by ID."""
    return run_query(
        lambda c: c.table("customers").select("customer_id, name").order("customer_id"),
        "load customers",
    )


def get_products():
    """Return all products with their current prices, ordered by ID."""
    return run_query(
        lambda c: c.table("products")
        .select("product_id, product_name, price")
        .order("product_id"),
        "load products",
    )


def get_product(product_id):
    """Return one product (with its current price) or None if not found."""
    rows = run_query(
        lambda c: c.table("products")
        .select("product_id, product_name, price")
        .eq("product_id", product_id),
        "look up the product",
    )
    return rows[0] if rows else None


def insert_order(order):
    """Insert one order and return the row Supabase sends back.

    order_id is not included - the database generates it.
    """
    rows = run_query(lambda c: c.table("orders").insert(order), "save the order")
    if not rows:
        raise DatabaseError("Supabase did not confirm the insertion.")
    return rows[0]


def get_order(order_id):
    """Run a NEW query for one order by its ID. Returns None if not found."""
    rows = run_query(
        lambda c: c.table("orders").select("*").eq("order_id", order_id),
        "retrieve the saved order",
    )
    return rows[0] if rows else None
