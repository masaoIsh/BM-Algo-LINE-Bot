import os
import json
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    JoinEvent, LeaveEvent, GroupSummary
)
from dotenv import load_dotenv
from bot_logic import GroupDecisionBot

# Load environment variables
load_dotenv()

app = Flask(__name__)

# LINE Bot credentials
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

# Initialize the bot logic
decision_bot = GroupDecisionBot()

@app.route("/callback", methods=['POST'])
def callback():
    """Handle LINE webhook events"""
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    
    return 'OK'

@handler.add(JoinEvent)
def handle_join(event):
    """Handle when bot is added to a group"""
    welcome_message = (
        "👋 Hi! I'm the Fair Assignment Bot!\n\n"
        "I help groups make fair decisions using the Bogomolnaia-Moulin algorithm.\n\n"
        "To start a fair assignment session, type:\n"
        "• 'start assignment' followed by your items\n"
        "• Example: 'start assignment Research, Writing, Presentation'\n\n"
        "Type 'help' for more commands!"
    )
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=welcome_message))

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """Handle text messages"""
    user_id = event.source.user_id
    group_id = event.source.group_id if hasattr(event.source, 'group_id') else None
    text = event.message.text.strip()
    
    # Handle different commands
    if text.lower().startswith('start assignment'):
        handle_start_assignment(event, text, group_id)
    elif text.lower() == 'help':
        handle_help(event)
    elif text.lower() == 'status':
        handle_status(event, group_id)
    elif text.lower() == 'run algorithm':
        handle_run_algorithm(event, group_id)
    elif text.lower() == 'make assignments':
        handle_make_assignments(event, group_id)
    elif text.lower() == 'cancel':
        handle_cancel(event, group_id)
    elif text.lower().startswith('rank'):
        handle_ranking(event, text, user_id, group_id)
    else:
        # Check if this might be a ranking
        if group_id and decision_bot.is_ranking_format(text, None):  # Don't check length here, let submit_ranking handle it
            handle_ranking(event, text, user_id, group_id)
        else:
            handle_unknown_command(event)

def handle_start_assignment(event, text, group_id):
    """Start a new assignment session"""
    if not group_id:
        line_bot_api.reply_message(
            event.reply_token, 
            TextSendMessage(text="This command only works in group chats!")
        )
        return
    
    # Extract items from command
    items_text = text.replace('start assignment', '').strip()
    if not items_text:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="Please specify items! Example: 'start assignment Research, Writing, Presentation'")
        )
        return
    
    items = [item.strip() for item in items_text.split(',')]
    if len(items) < 2:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="Please provide at least 2 items to assign!")
        )
        return
    
    # Start the session
    success = decision_bot.start_session(group_id, items)
    if success:
        items_list = '\n'.join([f"{i+1}. {item}" for i, item in enumerate(items)])
        message = (
            f"🎯 Starting fair assignment session!\n\n"
            f"Items to assign:\n{items_list}\n\n"
            f"Please rank the items by replying with numbers separated by commas.\n"
            f"Example: '3,1,2' means item 3 is your top choice.\n\n"
            f"Type 'status' to see current progress."
        )
    else:
        message = "❌ A session is already in progress. Type 'cancel' to end it first."
    
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))

def handle_help(event):
    """Show help information"""
    help_text = (
        "🤖 Fair Assignment Bot Commands:\n\n"
        "• 'start assignment item1, item2, item3' - Start new session\n"
        "• 'rank 3,1,2' - Submit your ranking\n"
        "• 'status' - Check current progress\n"
        "• 'run algorithm' - Execute fair assignment\n"
        "• 'make assignments' - Get final assignments\n"
        "• 'cancel' - Cancel current session\n"
        "• 'help' - Show this help\n\n"
        "The bot uses the Bogomolnaia-Moulin algorithm to ensure fair, envy-free assignments!"
    )
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=help_text))

def handle_status(event, group_id):
    """Show current session status"""
    if not group_id:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="This command only works in group chats!")
        )
        return
    
    status = decision_bot.get_status(group_id)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=status))

def handle_run_algorithm(event, group_id):
    """Run the Bogomolnaia-Moulin algorithm"""
    if not group_id:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="This command only works in group chats!")
        )
        return
    
    result = decision_bot.run_algorithm(group_id)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=result))

def handle_make_assignments(event, group_id):
    """Make final assignments"""
    if not group_id:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="This command only works in group chats!")
        )
        return
    
    result = decision_bot.make_final_assignments(group_id)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=result))

def handle_cancel(event, group_id):
    """Cancel current session"""
    if not group_id:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="This command only works in group chats!")
        )
        return
    
    success = decision_bot.cancel_session(group_id)
    if success:
        message = "✅ Session cancelled."
    else:
        message = "❌ No active session to cancel."
    
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))

def handle_ranking(event, text, user_id, group_id):
    """Handle preference ranking submission"""
    if not group_id:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="This command only works in group chats!")
        )
        return
    
    # Extract ranking from text
    if text.lower().startswith('rank'):
        ranking_text = text.replace('rank', '').strip()
    else:
        ranking_text = text
    
    success, message = decision_bot.submit_ranking(group_id, user_id, ranking_text)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))

def handle_unknown_command(event):
    """Handle unknown commands"""
    message = (
        "🤔 I didn't understand that command.\n\n"
        "Type 'help' to see available commands, or try submitting a ranking with numbers separated by commas."
    )
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000) 