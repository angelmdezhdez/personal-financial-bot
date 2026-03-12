import uuid
import os
import sys
import time
import threading
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
from langchain_core.messages import HumanMessage
from agent.agent import graph



# ==========================================
# Configuración de Archivos y Logs
# ==========================================
CHATS_DIR = "chats"
os.makedirs(CHATS_DIR, exist_ok=True)

def guardar_en_log(session_id, texto):
    """Escribe eventos en el archivo .txt de la sesión"""
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    filename = os.path.join(CHATS_DIR, f"chat_{session_id}.txt")
    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} {texto}\n")

# ==========================================
# Estética de Terminal (Animación)
# ==========================================
class AnimacionPensando:
    def __init__(self):
        self.ejecutando = False
        self.hilo = None

    def _animar(self):
        # Ciclo de puntos suspensivos
        for char in [" .  ", " .. ", " ...", "    "]:
            if not self.ejecutando:
                break
            sys.stdout.write(f"\rPensando{char}")
            sys.stdout.flush()
            time.sleep(0.1)

    def iniciar(self):
        self.ejecutando = True
        self.hilo = threading.Thread(target=self._animar)
        self.hilo.start()

    def detener(self):
        self.ejecutando = False
        if self.hilo:
            self.hilo.join()
        sys.stdout.write("\r" + " " * 20 + "\r") # Limpia la línea de "Pensando..."
        sys.stdout.flush()

# ==========================================
# Lógica Principal del Chat
# ==========================================
def chat_interactivo():
    print("\n" + "="*60)
    print("AGENTE INTERACTIVO DE VENTAS")
    print("="*60)
    print("Escribe 'salir' para terminar.")
    
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    animacion = AnimacionPensando()
    
    guardar_en_log(thread_id, f"--- SESIÓN INICIADA: {thread_id} ---")

    while True:
        try:
            user_input = input("\n👤 Tú: ")
            
            if user_input.lower() in ['salir', 'quit', 'exit']:
                print("\nEncantado de ayudarte. ¡Hasta pronto!")
                guardar_en_log(thread_id, "--- SESIÓN FINALIZADA POR EL USUARIO ---")
                break
            
            if not user_input.strip():
                continue

            guardar_en_log(thread_id, f"USUARIO: {user_input}")
            
            # Iniciamos animación y proceso del grafo
            animacion.iniciar()
            
            mensajes_recibidos = [HumanMessage(content=user_input)]
            
            # Procesamos el stream
            # Guardamos todo el rastro técnico en el log, pero solo la respuesta final en terminal
            respuesta_agente = ""
            
            for event in graph.stream({"messages": mensajes_recibidos}, config, stream_mode="updates"):
                for node_name, node_state in event.items():
                    # Registro técnico en el archivo
                    guardar_en_log(thread_id, f"[NODO: {node_name}]")
                    
                    ultimo_msg = node_state["messages"][-1]
                    
                    # Log de herramientas
                    if hasattr(ultimo_msg, "tool_calls") and ultimo_msg.tool_calls:
                        for tc in ultimo_msg.tool_calls:
                            guardar_en_log(thread_id, f"LLAMADA TOOL: {tc['name']} con {tc['args']}")
                    
                    # Si el nodo es el agente y trae contenido, es la respuesta al usuario
                    if node_name == "agent" and ultimo_msg.content:
                        if isinstance(ultimo_msg.content, str):
                            respuesta_agente = ultimo_msg.content
                        elif isinstance(ultimo_msg.content, list):
                            textos = []
                            for part in ultimo_msg.content:
                                if isinstance(part, dict) and "text" in part:
                                    textos.append(part["text"])
                                elif isinstance(part, str):
                                    textos.append(part)
                            respuesta_agente = "".join(textos)
                    
                    # Si es un nodo de herramientas, logueamos el resultado
                    if "tools" in node_name:
                        guardar_en_log(thread_id, f"RESULTADO TOOL: {ultimo_msg.content[:200]}...")

            animacion.detener()
            
            # Mostrar solo la respuesta limpia
            if respuesta_agente:
                print(f"🤖 Agente: {respuesta_agente}")
                guardar_en_log(thread_id, f"AGENTE: {respuesta_agente}")

        except Exception as e:
            animacion.detener()
            error_msg = f"ERROR: {str(e)}"
            print(f"\n❌ Ups, algo salió mal: {error_msg}")
            guardar_en_log(thread_id, error_msg)

if __name__ == "__main__":
    if not os.getenv("GOOGLE_API_KEY"):
        print("Error: Configura GOOGLE_API_KEY en tu .env")
    else:
        chat_interactivo()