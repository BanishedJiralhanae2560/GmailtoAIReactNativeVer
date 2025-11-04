from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins for development

def load_emails():
    """Load emails from JSON file, create sample data if missing"""
    data_path = os.path.join('data', 'emails.json')
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    if os.path.exists(data_path):
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                emails = json.load(f)
                print(f"✅ Loaded {len(emails)} emails from file")
                return emails
        except Exception as e:
            print(f"❌ Error loading emails: {e}")
            return create_sample_emails(data_path)
    else:
        print("📝 No emails.json found, creating sample data...")
        return create_sample_emails(data_path)

def create_sample_emails(data_path):
    """Create sample email data for testing"""
    sample_emails = [
        {
            "subject": "Meeting tomorrow at 2pm",
            "from": "boss@company.com",
            "snippet": "Don't forget about our project review meeting tomorrow at 2pm in conference room A."
        },
        {
            "subject": "Your order has shipped",
            "from": "orders@amazon.com",
            "snippet": "Good news! Your order #123456 has been shipped and will arrive in 2-3 business days."
        },
        {
            "subject": "Weekly Report Due",
            "from": "manager@company.com",
            "snippet": "Please submit your weekly report by Friday EOD. Include all project updates."
        },
        {
            "subject": "Lunch this Friday?",
            "from": "friend@email.com",
            "snippet": "Hey! Want to grab lunch this Friday? Let me know what works for you."
        },
        {
            "subject": "Invoice for January",
            "from": "billing@service.com",
            "snippet": "Your invoice for January is ready. Total amount due: $99.99. Payment due in 15 days."
        }
    ]
    
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(sample_emails, f, indent=2)
    
    print(f"✅ Created sample emails file with {len(sample_emails)} emails")
    return sample_emails

@app.route('/')
def index():
    return jsonify({
        "status": "running",
        "message": "✅ Gmail AI Backend is running!",
        "endpoints": ["/", "/chat"]
    })

@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat():
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.get_json()
        print("\n" + "="*50)
        print("📩 Received request:", data)
        
        if not data:
            return jsonify({"error": "No JSON data received"}), 400
        
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({"response": "Please enter a valid question."}), 400
        
        # Load emails
        emails = load_emails()
        print(f"📧 Loaded {len(emails)} emails")
        
        # Import search function
        try:
            from analyze_emails import search_emails
            results = search_emails(query, emails)
            print(f"🔎 Found {len(results)} matching emails")
        except ImportError:
            print("⚠️ analyze_emails.py not found, using simple search")
            results = simple_search(query, emails)
        
        if not results:
            return jsonify({"response": "No matching emails found. Try asking about meetings, orders, or reports."})
        
        # Format response
        response_list = [
            {
                "subject": e.get("subject", "No subject"),
                "from": e.get("from", "Unknown sender"),
                "snippet": e.get("snippet", "")
            }
            for e in results
        ]
        
        print(f"✅ Sending {len(response_list)} results")
        print("="*50 + "\n")
        
        return jsonify({"response": response_list})
    
    except Exception as e:
        print(f"❌ Error in /chat: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def simple_search(query, emails):
    """Fallback search if analyze_emails.py is not available"""
    query_lower = query.lower()
    results = []
    
    for email in emails:
        text = f"{email.get('subject', '')} {email.get('from', '')} {email.get('snippet', '')}".lower()
        if any(word in text for word in query_lower.split()):
            results.append(email)
    
    return results[:5]

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🚀 Starting Gmail AI Backend Server")
    print("="*50)
    print("📍 Server will be available at:")
    print("   - http://localhost:5000")
    print("   - http://0.0.0.0:5000")
    print("\n💡 Find your local IP address:")
    print("   - Windows: Run 'ipconfig' in Command Prompt")
    print("   - Mac/Linux: Run 'ifconfig' in Terminal")
    print("   - Android Emulator: Use http://10.0.2.2:5000")
    print("="*50 + "\n")
    
    app.run(host="0.0.0.0", port=5000, debug=True)
