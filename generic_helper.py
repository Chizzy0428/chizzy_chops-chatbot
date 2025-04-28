import re

# Convert food dict to readable string
def get_str_from_food_dict(food_dict: dict):
    return ", ".join([f"{int(qty)} {item}" for item, qty in food_dict.items()])

# Extract the session ID from the Dialogflow session context string
def extract_session_id(session_str: str):
    match = re.search(r"/sessions/([^/]+)/contexts/", session_str)
    if match:
        return match.group(1)  # This is the actual session ID
    return ""

