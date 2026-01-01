import gradio as gr
import requests
from datetime import datetime

API_URL = "http://127.0.0.1:8003/execute"

def process_query(user_id, query, history):
    """
    Process the user query and return the response.
    
    Args:
        user_id: Patient ID number
        query: User's appointment query
        history: Chat history
    
    Returns:
        Tuple of (chat history, empty string for input box, status message)
    """
    if not user_id or not query:
        return history, query, "⚠️ Please provide both ID number and query."
    
    try:
        # Validate user_id is numeric
        user_id_int = int(user_id)
        
        # Initialize history if None
        history = history or []
        
        # Add user message to history
        history.append({"role": "user", "content": query})
        
        # Make API request
        response = requests.post(
            API_URL,
            json={
                'messages': query,
                'id_number': user_id_int
            },
            verify=False,
            timeout=30
        )
        
        if response.status_code == 200:
            response_data = response.json()
            response_text = response_data.get("response", "No response from server.")
            
            # Add assistant response to history
            history.append({"role": "assistant", "content": response_text})
            
            status = f"✅ Response received at {datetime.now().strftime('%H:%M:%S')}"
            return history, "", status
        else:
            error_msg = f"Server returned error {response.status_code}"
            history.append({"role": "assistant", "content": f"❌ {error_msg}"})
            return history, query, f"❌ {error_msg}"
            
    except ValueError:
        return history, query, "⚠️ ID number must be numeric."
    except requests.exceptions.Timeout:
        return history, query, "⏱️ Request timed out. Please try again."
    except requests.exceptions.ConnectionError:
        return history, query, "🔌 Cannot connect to server. Please check if the API is running."
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        return history, query, f"❌ {error_msg}"

def clear_conversation():
    """Clear the chat history and input fields."""
    return [], "", "", "Conversation cleared."

def load_example(example_text):
    """Load an example query."""
    return example_text

# Custom CSS
custom_css = """
    .header {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .footer {
        text-align: center;
        margin-top: 20px;
        padding: 10px;
        color: #666;
        font-size: 0.9em;
    }
    .example-btn {
        margin: 5px 0;
    }
"""

# Create the Gradio interface
with gr.Blocks(title="Doctor Appointment System") as demo:
    
    gr.HTML(custom_css)
    
    # Header
    gr.HTML("""
        <div class="header">
            <h1>🩺 Doctor Appointment System</h1>
            <p>Schedule and manage your medical appointments with ease</p>
        </div>
    """)
    
    with gr.Row():
        with gr.Column(scale=1):
            # Patient Information Section
            with gr.Group():
                gr.Markdown("### 👤 Patient Information")
                user_id_input = gr.Textbox(
                    label="Patient ID Number",
                    placeholder="Enter your ID number (e.g., 12345)",
                    max_lines=1
                )
            
            # Example Queries Section
            with gr.Group():
                gr.Markdown("### 💡 Example Queries")
                
                example_1 = gr.Button("📋 Check dentist availability", size="sm")
                example_2 = gr.Button("📋 Book cardiologist appointment", size="sm")
                example_3 = gr.Button("📋 Check available time slots", size="sm")
                example_4 = gr.Button("📋 Cancel my appointment", size="sm")
                example_5 = gr.Button("📋 Show upcoming appointments", size="sm")
        
        with gr.Column(scale=2):
            # Chat Interface Section
            chatbot = gr.Chatbot(
                label="Conversation",
                height=400
            )
            
            query_input = gr.Textbox(
                label="Your Query",
                placeholder="Type your appointment request here...",
                lines=2,
                max_lines=5
            )
            
            with gr.Row():
                submit_btn = gr.Button("🚀 Submit Query", variant="primary")
                clear_btn = gr.Button("🗑️ Clear Chat", variant="secondary")
            
            status_output = gr.Textbox(
                label="Status",
                interactive=False
            )
    
    # Footer
    gr.HTML("""
        <div class="footer">
            <p>💼 Professional Healthcare Management System | Powered by AI</p>
            <p>⚕️ For emergencies, please call 911 or visit the nearest emergency room</p>
        </div>
    """)
    
    # Event handlers for submit
    submit_btn.click(
        fn=process_query,
        inputs=[user_id_input, query_input, chatbot],
        outputs=[chatbot, query_input, status_output]
    )
    
    query_input.submit(
        fn=process_query,
        inputs=[user_id_input, query_input, chatbot],
        outputs=[chatbot, query_input, status_output]
    )
    
    # Event handler for clear
    clear_btn.click(
        fn=clear_conversation,
        inputs=None,
        outputs=[chatbot, query_input, user_id_input, status_output]
    )
    
    # Event handlers for example buttons
    example_1.click(
        fn=lambda: "Can you check if a dentist is available tomorrow at 10 AM?",
        inputs=None,
        outputs=query_input
    )
    
    example_2.click(
        fn=lambda: "I need to book an appointment with a cardiologist next week",
        inputs=None,
        outputs=query_input
    )
    
    example_3.click(
        fn=lambda: "What are the available time slots for Dr. Smith on Friday?",
        inputs=None,
        outputs=query_input
    )
    
    example_4.click(
        fn=lambda: "Cancel my appointment scheduled for tomorrow",
        inputs=None,
        outputs=query_input
    )
    
    example_5.click(
        fn=lambda: "Show me all my upcoming appointments",
        inputs=None,
        outputs=query_input
    )

# Launch the application
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🩺 Doctor Appointment System Starting...")
    print("="*60)
    print(f"📍 Local URL: http://127.0.0.1:7860")
    print(f"📍 Network URL: http://localhost:7860")
    print("="*60 + "\n")
    
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        show_error=True,
        inbrowser=True  # Automatically opens browser
    )