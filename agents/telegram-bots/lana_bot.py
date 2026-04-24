#!/usr/bin/env python3
# Telegram Bot für Lana-KI Multi-Agent Platform

import os
import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import httpx

# Logging Setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Agent URLs
AGENTS = {
    "gemini": "http://127.0.0.1:8011",
    "copilot": "http://127.0.0.1:8012", 
    "gems": "http://127.0.0.1:8013"
}

class LanaTelegramBot:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found")
        
        self.app = Application.builder().token(self.token).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        # Commands
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("agents", self.agents_command))
        self.app.add_handler(CommandHandler("status", self.status_command))
        
        # Callback queries (inline buttons)
        self.app.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Messages
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [InlineKeyboardButton("🤖 Gemini Enterprise", callback_data="agent_gemini")],
            [InlineKeyboardButton("🏢 Copilot Studio", callback_data="agent_copilot")],
            [InlineKeyboardButton("💎 Gemini Gems", callback_data="agent_gems")],
            [InlineKeyboardButton("📊 Status", callback_data="status")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = """
🌟 Willkommen bei Lana-KI Multi-Agent Platform!

Ich bin dein Zugang zu verschiedenen KI-Agenten:

🤖 **Gemini Enterprise** - Fortgeschrittene KI-Funktionen
🏢 **Copilot Studio** - Microsoft-Integration  
💎 **Gemini Gems** - Spezialisierte KI-Persönlichkeiten

Wähle einen Agenten oder sende mir eine Nachricht!
        """
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = """
🆘 **Lana-KI Bot Hilfe**

**Befehle:**
/start - Bot starten
/help - Diese Hilfe anzeigen
/agents - Verfügbare Agenten auflisten
/status - System-Status prüfen

**Verwendung:**
1. Wähle einen Agenten über die Buttons
2. Sende deine Nachricht
3. Erhalte Antworten vom gewählten Agenten

**Agenten:**
• Gemini Enterprise - Für komplexe Aufgaben
• Copilot Studio - Für Business-Integration
• Gemini Gems - Für spezialisierte Antworten
        """
        await update.message.reply_text(help_text)
    
    async def agents_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        status_text = "🤖 **Verfügbare Agenten:**\n\n"
        
        async with httpx.AsyncClient() as client:
            for name, url in AGENTS.items():
                try:
                    response = await client.get(f"{url}/health", timeout=5)
                    if response.status_code == 200:
                        status_text += f"✅ {name.title()}: Online\n"
                    else:
                        status_text += f"⚠️ {name.title()}: Probleme\n"
                except:
                    status_text += f"❌ {name.title()}: Offline\n"
        
        await update.message.reply_text(status_text)
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.agents_command(update, context)
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        if query.data.startswith("agent_"):
            agent_name = query.data.replace("agent_", "")
            context.user_data["selected_agent"] = agent_name
            
            agent_names = {
                "gemini": "Gemini Enterprise",
                "copilot": "Copilot Studio", 
                "gems": "Gemini Gems"
            }
            
            await query.edit_message_text(
                f"🤖 **{agent_names[agent_name]}** ausgewählt!\n\n"
                f"Sende mir jetzt deine Nachricht und ich leite sie an {agent_names[agent_name]} weiter."
            )
        
        elif query.data == "status":
            await self.agents_command(update, context)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_message = update.message.text
        selected_agent = context.user_data.get("selected_agent", "gemini")
        
        # Show typing indicator
        await update.message.chat.send_action("typing")
        
        try:
            async with httpx.AsyncClient() as client:
                agent_url = AGENTS[selected_agent]
                
                # Prepare request based on agent type
                if selected_agent == "gems":
                    payload = {
                        "message": user_message,
                        "gem_type": "companion",
                        "style": "friendly",
                        "language": "de"
                    }
                elif selected_agent == "copilot":
                    payload = {
                        "message": user_message,
                        "user_id": str(update.effective_user.id)
                    }
                else:  # gemini
                    payload = {
                        "message": user_message,
                        "character_id": "companion",
                        "temperature": 0.7
                    }
                
                response = await client.post(
                    f"{agent_url}/chat",
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    agent_response = result.get("response", "Keine Antwort erhalten")
                    
                    # Add agent indicator
                    agent_names = {
                        "gemini": "🤖 Gemini Enterprise",
                        "copilot": "🏢 Copilot Studio",
                        "gems": "💎 Gemini Gems"
                    }
                    
                    full_response = f"{agent_names[selected_agent]}:\n\n{agent_response}"
                    await update.message.reply_text(full_response)
                else:
                    await update.message.reply_text(
                        f"❌ Fehler beim Kontaktieren von {selected_agent}: {response.status_code}"
                    )
        
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await update.message.reply_text(
                f"❌ Fehler bei der Verarbeitung: {str(e)}"
            )
    
    async def run(self):
        logger.info("🚀 Starting Lana-KI Telegram Bot...")
        await self.app.run_polling()

if __name__ == "__main__":
    bot = LanaTelegramBot()
    asyncio.run(bot.run())

