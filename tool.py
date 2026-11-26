import wikipedia
from pathlib import Path
import sqlite3

def get_research(topic: str) -> str:
    try:
        search_results = wikipedia.search(topic)
        page = wikipedia.page(search_results[0])
        return page.content[0:500]
    except Exception as e:
        return f'Error searching web: {e}'

get_research_tool ={
    "name": "get_research",
    "description": "search wikipedia for a given search term and returns the article content. Use this when the user asks for factual information or wants to research a topic",
    "input_schema": {
        "type": "object",
        "properties": {
            "topic": {
            "type": "string",
            "description": "the topic to research"}
        }, 
        "required": ["topic"]
    }

}

TOOLS =[]
TOOLS.append(get_research_tool)

DB_PATH = Path(__file__).resolve().parent / "shop.db"


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_user(key, value):
    if key in {"email", "phone", "username"}:
        with _connect() as conn:
            row = conn.execute(
                f"SELECT * FROM customers WHERE {key} = ?",
                (value,)
            ).fetchone()
            return dict(row) if row else f"Couldn't find a user with {key} of {value}"
    raise ValueError(f"Invalid key: {key}")


def get_order_by_id(order_id):
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM orders WHERE id = ?",
            (order_id,)
        ).fetchone()
        return dict(row) if row else None


def get_customer_orders(customer_id):
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM orders WHERE customer_id = ?",
            (customer_id,)
        ).fetchall()
        return [dict(r) for r in rows]


def cancel_order(order_id):
    order = get_order_by_id(order_id)
    if order:
        if order["status"] == "Processing":
            with _connect() as conn:
                conn.execute(
                    "UPDATE orders SET status = 'Cancelled' WHERE id = ?",
                    (order_id,)
                )
                conn.commit()
            return "Cancelled the order"
        return f"Order status is '{order['status']}'. Can't cancel it."
    return "Can't find that order!"

get_user_tool = {
    "name": "get_user",
    "description": "Looks up a customer in the shop database by email, phone, or username.",
    "input_schema": {
        "type": "object",
        "properties": {
            "key": {
                "type": "string",
                "enum": ["email", "phone", "username"],
                "description": "The attribute to search by (email, phone, or username)."
            },
            "value": {
                "type": "string",
                "description": "The value to match for the specified attribute."
            }
        },
        "required": ["key", "value"]
    }
}

get_order_by_id_tool = {
    "name": "get_order_by_id",
    "description": "Retrieves details of a specific order by its order ID (product, quantity, price, status).",
    "input_schema": {
        "type": "object",
        "properties": {
            "order_id": {
                "type": "string",
                "description": "The unique identifier for the order."
            }
        },
        "required": ["order_id"]
    }
}

get_customer_orders_tool = {
    "name": "get_customer_orders",
    "description": "Retrieves all orders belonging to a customer using their customer_id.",
    "input_schema": {
        "type": "object",
        "properties": {
            "customer_id": {
                "type": "string",
                "description": "The customer_id belonging to the customer."
            }
        },
        "required": ["customer_id"]
    }
}

cancel_order_tool = {
    "name": "cancel_order",
    "description": "Cancels an order by order_id. Only orders with status 'Processing' can be cancelled.",
    "input_schema": {
        "type": "object",
        "properties": {
            "order_id": {
                "type": "string",
                "description": "The order_id of the order to cancel."
            }
        },
        "required": ["order_id"]
    }
}

TOOLS.extend([get_user_tool, get_order_by_id_tool, get_customer_orders_tool, cancel_order_tool])

def process_tool_call(tool_name, tool_input):
    if tool_name == "get_research":
        return get_research(tool_input["topic"])
    elif tool_name == "get_user":
        return get_user(tool_input["key"], tool_input["value"])
    elif tool_name == "get_order_by_id":
        return get_order_by_id(tool_input["order_id"])
    elif tool_name == "get_customer_orders":
        return get_customer_orders(tool_input["customer_id"])
    elif tool_name == "cancel_order":
        return cancel_order(tool_input["order_id"])
    else:
        return f"Unknown tool: {tool_name}"