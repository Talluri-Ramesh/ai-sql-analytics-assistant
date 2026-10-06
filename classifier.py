import json
from groq import Groq
from config import GROQ_API_KEY

def classify_question(question: str) -> tuple[str, float]:
    """
    Classifies whether a user question should be handled via:
    - 'CASE_A': Database-related query (needs SQL generation & execution)
    - 'CASE_B': Unrelated to the database (general assistant chat)
    
    Returns:
        - route: 'CASE_A' or 'CASE_B'
        - confidence: float between 0.0 and 1.0
    """
    q_lower = question.lower()
    
    # 1. Fast Keyword / Entity Pre-check
    # Known business entities / keywords linked to the E-Commerce database
    db_keywords = [
        "customer", "customers", "employee", "employees", "category", "categories",
        "supplier", "suppliers", "product", "products", "order", "orders",
        "orderitem", "orderitems", "payment", "payments", "shipper", "shippers",
        "return", "returns", "sales", "revenue", "price", "stock", "salary",
        "department", "city", "state", "shipdate", "joindate", "status", "revenue",
        "top", "total", "average", "count", "list", "show", "display", "find"
    ]
    
    # Exclude common false-positive general knowledge triggers containing overlapping words
    false_positive_phrases = ["price of gold", "price of bitcoin", "weather", "president", "capital of"]
    if any(phrase in q_lower for phrase in false_positive_phrases):
        return "CASE_B", 0.95

    # Count how many database keywords appear in the question
    matches = sum(1 for kw in db_keywords if kw in q_lower)
    
    # Heuristic thresholds for fast-path routing
    if matches >= 2:
        # High confidence it's database-related
        return "CASE_A", 0.90
    elif matches == 0:
        # High confidence it's general chat
        return "CASE_B", 0.90
        
    # 2. Ambiguous case (e.g., exactly 1 matching keyword): Fallback to LLM classification
    client = Groq(api_key=GROQ_API_KEY)
    
    system_prompt = (
        "You are a router for an E-Commerce PostgreSQL analytics app.\n"
        "Classify the user's question into one of two categories:\n"
        "1. 'CASE_A': The question asks about data, metrics, records, or entities present in an e-commerce database (Customers, Employees, Categories, Suppliers, Products, Orders, OrderItems, Payments, Shippers, Returns).\n"
        "2. 'CASE_B': The question is general knowledge, coding help, casual conversation, or entirely unrelated to this e-commerce database.\n\n"
        "Respond strictly in JSON format with two keys: 'route' (either 'CASE_A' or 'CASE_B') and 'confidence' (a float between 0.0 and 1.0)."
    )

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        
        result = json.loads(response.choices[0].message.content)
        route = result.get("route", "CASE_B")
        confidence = float(result.get("confidence", 0.5))
        
        # Ensure strict adherence to allowed routes
        if route not in ["CASE_A", "CASE_B"]:
            route = "CASE_B"
            
        return route, confidence

    except Exception:
        # Fallback safe default if LLM json parsing fails
        return "CASE_B", 0.5

if __name__ == "__main__":
    print("--- Classifier Test ---")
    
    test_questions = [
        ("Display products priced above 500", "CASE_A"),
        ("What is the capital of France?", "CASE_B"),
        ("Show me total revenue by category", "CASE_A"),
        ("How do I write a Python function?", "CASE_B"),
        ("What's the price of gold today?", "CASE_B") # Testing false positive guard
    ]
    
    for q, expected in test_questions:
        route, conf = classify_question(q)
        status = "PASSED" if route == expected else "FAILED"
        print(f"[{status}] Q: '{q}' -> Route: {route} (Confidence: {conf}) | Expected: {expected}")