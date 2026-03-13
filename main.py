import os
import uuid
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from langchain_core.messages import HumanMessage
load_dotenv()
from bot.bot import graph  

# Configuración de logs para ver qué pasa en AWS
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
#MI_TELEGRAM_ID = int(os.getenv("MI_TELEGRAM_ID", "0")) # Pon tu ID en el .env

async def procesar_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    ## Bot privado
    #if update.effective_user.id != MI_TELEGRAM_ID:
    #    await update.message.reply_text("⛔ Acceso denegado. Este es un bot privado.")
    #    return

    user_input = update.message.text
    config = {"configurable": {"thread_id": str(update.effective_chat.id)}}
    
    # Enviamos una señal de "escribiendo..."
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        mensajes_recibidos = [HumanMessage(content=user_input)]
        respuesta_agente = ""

        async for event in graph.astream({"messages": mensajes_recibidos}, config, stream_mode="updates"):
            for node_name, node_state in event.items():
                ultimo_msg = node_state["messages"][-1]

                if node_name == "agent" and ultimo_msg.content:
                    # Limpiamos el contenido (Lógica para Gemini 3)
                    if isinstance(ultimo_msg.content, str):
                        respuesta_agente = ultimo_msg.content
                    elif isinstance(ultimo_msg.content, list):
                        respuesta_agente = "".join([part["text"] for part in ultimo_msg.content if isinstance(part, dict) and "text" in part])

        if respuesta_agente:
            await update.message.reply_text(respuesta_agente)
        else:
            await update.message.reply_text("El agente no devolvió una respuesta clara.")

    except Exception as e:
        logging.error(f"Error procesando mensaje: {e}")
        await update.message.reply_text(f"❌ Ocurrió un error: {str(e)}")

def main():

    if not TELEGRAM_BOT_TOKEN:
        print("Error: No se encontró TELEGRAM_BOT_TOKEN")
        return

    # Construir la aplicación (Solo una vez)
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Añadir el manejador de mensajes de texto
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, procesar_mensaje))

    # Iniciar el bot (Polling)
    print("🚀 Bot de Finanzas en marcha...")
    application.run_polling()

if __name__ == "__main__":
    if not os.getenv("GOOGLE_API_KEY"):
        print("Error: Configura GOOGLE_API_KEY en tu .env")
    else:
        main()