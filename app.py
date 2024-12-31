import os
import sys
import json
from flask import Flask, render_template, request, jsonify, session, Response, stream_with_context
from dotenv import load_dotenv
from flask_cors import CORS
from datetime import datetime

# Set up paths and environment
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ''))
sys.path.append(root_path)
load_dotenv()

# Configure template and static folders
template_path = os.path.join(root_path, '', 'templates')
static_path = os.path.join(root_path, '', 'static')
print(f"Using template folder: {template_path}")
print(f"Using static folder: {static_path}")

# Initialize Flask app
app = Flask(__name__, template_folder=template_path, static_folder=static_path)
app.secret_key = os.getenv('FRONT_END_SECRET_KEY')

# Enable CORS for development
CORS(app, origins=os.getenv('ALLOWED_ORIGINS', '*').split(','))

# Import and initialize LLMProcessor
from backend.llm.response_generation import LLMProcessor
llm_processor = LLMProcessor()

# Constants
QUESTION_LIMIT = 50
MAX_CHAT_HISTORY = 20

@app.route('/')
def index():
    """
    Render the main page and reset the session.
    """
    session.clear()
    session['question_count'] = 0
    session['chat_history'] = []
    return render_template('index.html')

@app.route('/get_answer', methods=['POST'])
def get_answer():
    """
    Process user questions and stream AI-generated answers.
    """
    # Uncomment the following lines to enforce question limit
    # if session['question_count'] >= QUESTION_LIMIT:
    #     return jsonify({'answer': 'You have reached the chat limit of this session. Please refresh the page to start a new session.'})

    data = request.get_json()
    question = data.get('question', '')
    chat_history = session.get('chat_history', [])

    return Response(stream_with_context(generate_answer(question, chat_history)), content_type='text/event-stream')

def generate_answer(question, chat_history):
    """
    Generator function to stream AI responses and update session data.
    """
    full_answer = ""
    for partial_answer in llm_processor.get_answer_with_sources(question, chat_history):
        if partial_answer:
            full_answer = partial_answer
            yield f"data: {json.dumps({'partial_answer': partial_answer})}\n\n"
    
    # Update chat history and session data
    update_session(question, full_answer, chat_history)
    
    yield f"data: {json.dumps({'complete': True, 'chat_history': chat_history, 'question_count': session['question_count']})}\n\n"

def update_session(question, answer, chat_history):
    """
    Update the session with new chat history and question count.
    """
    chat_history.append({"question": question, "answer": answer})
    if len(chat_history) > MAX_CHAT_HISTORY:
        chat_history.pop(0)
    session['chat_history'] = chat_history
    session['question_count'] = session.get('question_count', 0) + 1

@app.route("/store_feedback", methods=["POST"])
def store_feedback():
    data = request.json
    question = data.get("question")
    answer = data.get("answer")
    feedback = data.get("feedback")

    if not all([question, answer, feedback]) or feedback not in ["positive", "negative"]:
        return jsonify({"success": False, "error": "Missing or invalid data"}), 400

    feedback_data = {
        "question": question,
        "answer": answer,
        "feedback": feedback,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    feedback_file = "feedback.json"
    
    try:
        if os.path.exists(feedback_file):
            with open(feedback_file, "r+") as f:
                existing_data = json.load(f)
                existing_data.append(feedback_data)
                f.seek(0)
                f.truncate()
                json.dump(existing_data, f, indent=2)
        else:
            with open(feedback_file, "w") as f:
                json.dump([feedback_data], f, indent=2)
        
        return jsonify({"success": True}), 200
    except Exception as e:
        print(f"Error storing feedback: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/view_feedback", methods=["GET"])
def view_feedback():
    """
    Render the feedback viewer page.
    """
    try:
        feedback_file = "feedback.json"
        if os.path.exists(feedback_file):
            with open(feedback_file, "r") as f:
                feedback_data = json.load(f)
                # Sort feedback data by timestamp in reverse order (latest first)
                feedback_data.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        else:
            feedback_data = []
        return render_template('feedback.html', feedback=feedback_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0')
