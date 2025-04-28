from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import re
import logging

import generic_helper

app = FastAPI()
logging.basicConfig(level=logging.INFO)

# Session-based order tracking
chizzy_orders = {}

# ✅ Converts food dict to readable string
def get_str_from_food_dict(food_dict: dict):
    return ", ".join([f"{int(qty)} {item}" for item, qty in food_dict.items()])

# ✅ Extract session ID from context string
def extract_session_id(session_str: str):
    match = re.search(r"/sessions/([^/]+)/contexts/", session_str)
    return match.group(1) if match else "unknown"

# ✅ FastAPI webhook handler
@app.post("/")
async def webhook(request: Request):
    body = await request.json()
    intent = body["queryResult"]["intent"]["displayName"]
    parameters = body["queryResult"].get("parameters", {})
    output_contexts = body["queryResult"].get("outputContexts", [])
    session_id = extract_session_id(output_contexts[0]["name"]) if output_contexts else "unknown"

    logging.info(f"Intent: {intent}, Session: {session_id}, Params: {parameters}")

    if intent.lower() in ["new.order", "start.order"]:
        chizzy_orders[session_id] = {}  # Start fresh order
        return JSONResponse(content={"fulfillmentText": "Great! What would you like to order?"})

    elif intent.lower() == "order.add":
        return add_to_order(parameters, session_id)

    elif intent.lower() == "order.complete":
        return complete_order(session_id)

    elif intent.lower() == "track.order":
        return JSONResponse(content={"fulfillmentText": "Please provide your order ID to track it."})

    else:
        return JSONResponse(content={
            "fulfillmentText": "I don't understand. Please say 'New Order' or 'Track Order'."
        })

def add_to_order(parameters: dict, session_id: str):
    food_items = parameters.get("food_items") or parameters.get("food-item") or []
    quantities = parameters.get("number", [])

    # Fallback: Dialogflow may pass single values instead of lists
    if isinstance(food_items, str):
        food_items = [food_items]
    if isinstance(quantities, int):
        quantities = [quantities]

    # Handle if one quantity is given for multiple items
    if len(food_items) > 1 and len(quantities) == 1:
        quantities = [quantities[0]] + [1] * (len(food_items) - 1)

    # Match item-quantity length
    if len(food_items) != len(quantities):
        return JSONResponse(content={
            "fulfillmentText": (
                "Could you confirm how many of each item you'd like? For example: "
                "'2 Jollof Rice and 1 Smoothie'"
            )
        })

    # Initialize or update order
    session_order = chizzy_orders.get(session_id, {})
    for item, qty in zip(food_items, quantities):
        session_order[item] = session_order.get(item, 0) + int(qty)

    chizzy_orders[session_id] = session_order
    order_summary = generic_helper.get_str_from_food_dict(session_order)

    return JSONResponse(content={
        "fulfillmentText": f"So far, you've ordered: {order_summary}. Anything else?"
    })
# ✅ Complete the order
def complete_order(session_id: str):
    if session_id not in chizzy_orders or not chizzy_orders[session_id]:
        return JSONResponse(content={"fulfillmentText": "You have not added any items yet. Please start a new order."})

    summary = get_str_from_food_dict(chizzy_orders[session_id])
    order_id = session_id[-5:]  # Just a placeholder for demo
    del chizzy_orders[session_id]

    return JSONResponse(content={
        "fulfillmentText": f"Thanks! Your order #{order_id} has been placed: {summary}. You’ll get a notification when it’s ready!"
    })
