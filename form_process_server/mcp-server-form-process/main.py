import sqlite3
import json
import base64
import requests
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP Server
mcp = FastMCP("Form Process Server")

DB_FILE = "receipts.db"
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions" # Adjust if your LMStudio port is different

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS receipts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                merchant_name TEXT NOT NULL,
                date TEXT NOT NULL,
                total_amount REAL NOT NULL,
                category TEXT NOT NULL,
                items_blob TEXT
            )
        ''')
        conn.commit()

init_db()

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

@mcp.tool()
def process_receipt_image(image_path: str) -> str:
    """Extract receipt data from a local image file and save it to the database.
    
    This function uses a local LMStudio API to process the image and expects
    a JSON response with merchant_name, date, total_amount, category, and items.
    
    Args:
        image_path: Absolute path to the receipt image file.
    """
    try:
        base64_image = encode_image(image_path)
    except Exception as e:
        return f"Error reading image: {e}"

    prompt = '''
    Analyze this receipt carefully and extract the following information. You MUST respond with ONLY a valid, raw JSON object matching this structure exactly, with no additional markdown formatting, backticks, or explanation text:
    {
        "merchant_name": "Name of the business",
        "date": "YYYY-MM-DD",
        "total_amount": 0.00,
        "category": "Food, Pharmacy, Retail, or General",
        "items": [
            {"name": "item 1", "price": 0.00},
            {"name": "item 2", "price": 0.00}
        ]
    }
    '''

    payload = {
        "model": "local-model", # LM Studio dynamically routes to loaded model
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "temperature": 0.1,
        "response_format": {"type": "json_object"}
    }

    try:
        response = requests.post(LM_STUDIO_URL, json=payload, timeout=60)
        response.raise_for_status()
        
        result_json_str = response.json()["choices"][0]["message"]["content"]
        
        # Parse the JSON from the LLM
        extracted_data = json.loads(result_json_str)
        
        # Save to DB
        merchant_name = extracted_data.get("merchant_name", "Unknown")
        date = extracted_data.get("date", "Unknown")
        total_amount = float(extracted_data.get("total_amount", 0.0))
        category = extracted_data.get("category", "General")
        items_blob = json.dumps(extracted_data.get("items", []))
        
        db_result = add_receipt_to_db(merchant_name, date, total_amount, category, items_blob)
        
        return f"Extraction Successful.\nExtracted JSON: {result_json_str}\nDB Status: {db_result}"

    except json.JSONDecodeError as decode_err:
        return f"Error: LLM returned invalid JSON. Response was: {result_json_str}"
    except Exception as e:
        return f"Error communicating with LMStudio or parsing results: {e}"

@mcp.tool()
def add_receipt_to_db(merchant_name: str, date: str, total_amount: float, category: str, items_blob: str) -> str:
    """Add a new receipt to the database.
    
    Args:
        merchant_name: Name of the merchant.
        date: Date of the receipt in YYYY-MM-DD.
        total_amount: Total amount paid.
        category: Category of the receipt (e.g., Food, Pharmacy, General).
        items_blob: JSON string of items in the receipt.
    """
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO receipts (merchant_name, date, total_amount, category, items_blob) VALUES (?, ?, ?, ?, ?)",
                (merchant_name, date, total_amount, category, items_blob)
            )
            conn.commit()
            return f"Receipt from {merchant_name} added successfully with ID {cursor.lastrowid}."
    except Exception as e:
        return f"Error adding receipt: {e}"

@mcp.tool()
def analyze_spending_by_category() -> str:
    """Analyze total spending aggregated by category."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT category, SUM(total_amount) FROM receipts GROUP BY category")
            results = cursor.fetchall()
            
            if not results:
                return "No receipts found in the database."
                
            report = "Spending by Category:\n"
            for category, total in results:
                report += f"- {category}: ${total:.2f}\n"
            return report
    except Exception as e:
        return f"Error analyzing spending by category: {e}"

@mcp.tool()
def analyze_average_receipt_cost() -> str:
    """Calculate the average cost of all recorded receipts."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT AVG(total_amount) FROM receipts")
            result = cursor.fetchone()[0]
            
            if result is None:
                return "No receipts found in the database."
                
            return f"Average Receipt Cost: ${result:.2f}"
    except Exception as e:
        return f"Error calculating average receipt cost: {e}"

@mcp.tool()
def list_all_receipts() -> str:
    """List all receipts stored in the database."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, merchant_name, date, total_amount, category FROM receipts")
            results = cursor.fetchall()
            
            if not results:
                return "No receipts found in the database."
                
            report = "All Receipts:\n"
            for row in results:
                report += f"[{row[0]}] {row[1]} on {row[2]} - ${row[3]:.2f} ({row[4]})\n"
            return report
    except Exception as e:
        return f"Error listing receipts: {e}"

if __name__ == "__main__":
    mcp.run()
