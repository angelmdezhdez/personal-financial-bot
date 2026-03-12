from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode
from datetime import datetime

# Importamos las herramientas que creamos en el paso anterior
from bot.tools import (
    registrar_gasto,
    actualizar_saldos,
    actualizar_presupuesto,
    obtener_saldos
)

# ==========================================
# Primeros settings y definiciones
# ==========================================

tools_clientes = [buscar_cliente, obtener_contacto_cliente]
TOOLS_CLIENTES_NAMES = [tool.name for tool in tools_clientes]
tools_inventario = [consultar_inventario, buscar_articulo]

# tools son herramientas "genéricas" que el agente puede usar
tools = tools_clientes + tools_inventario + [consultar_tabla_bd]

# usamos este modelo de Google Gemini, que es un modelo de propósito general muy capaz para agentes conversacionales 
# y que es rápido y económico. 
llm = ChatGoogleGenerativeAI(model="gemini-3-flash-preview", temperature=0.5)

# "Conectamos" las herramientas al modelo. 
llm_with_tools = llm.bind_tools(tools)

# ==========================================
# Definición de los Nodos del Grafo
# ==========================================

def chatbot_node(state: MessagesState):
    """
    Este nodo es el 'Cerebro'. Toma el historial de mensajes actual, 
    le añade instrucciones de sistema y le pide al LLM que decida el siguiente paso.
    """
    fecha_hoy = datetime.now().strftime("%d de %B de %Y")
    mensajes = [
        SystemMessage(content=f"""Eres un asistente corporativo altamente eficiente. 
        Tienes acceso a bases de datos de inventario y clientes.
        Usa las herramientas a tu disposición para responder a las solicitudes del usuario.
        Si no sabes la respuesta o la herramienta falla, admítelo y pide aclaraciones.
        La fecha actual es {fecha_hoy}.""")
    ] + state["messages"]
    
    # invocamos al modelo con tools
    response = llm_with_tools.invoke(mensajes)
    
    # devolvemos la respuesta del modelo
    return {"messages": [response]}

# Nodo de herramientas principales (cliente, precio, inventario)
tool_node = ToolNode(tools=tools_inventario + [consultar_tabla_bd] + tools_clientes)
# Nodo de herramientas de clientes
clientes_tool_node = ToolNode(tools=tools_clientes)

# ==========================================
# Definimos el flujo
# ==========================================

def route_after_agent(state: MessagesState):
    """
    Decide a qué nodo ir después del agente:
    - Si el LLM no pidió ninguna herramienta -> terminar (END).
    - Si pidió consultar_agenda_dia o agendar_reunion -> nodo "agenda_tools".
    - Si pidió otra herramienta (cliente, precio, inventario) -> nodo "sql_tools".
    """
    ultimo_mensaje = state["messages"][-1]
    herramientas_solicitadas = getattr(ultimo_mensaje, "tool_calls", None)

    # si ya no se solicitan herramientas, terminamos la ejecución (END)
    if not herramientas_solicitadas:
        return END

    # qué herramientas se solicitaron en el último mensaje
    nombres_herramientas = {llamada["name"] for llamada in ultimo_mensaje.tool_calls}

    # Si alguna herramienta solicitada es de clientes -> ir a "tools_clientes"
    # Si no (cliente, precio, inventario) -> ir a "sql_tools"
    is_about_clients = any(
        nombre in TOOLS_CLIENTES_NAMES for nombre in nombres_herramientas
    )
    if is_about_clients:
        return "clientes_tools"
    return "sql_tools"

# definimos el grafo de estados
workflow = StateGraph(MessagesState)

# Agregamos el nodo del agente y los dos nodos de herramientas
workflow.add_node("agent", chatbot_node)
workflow.add_node("sql_tools", tool_node)
workflow.add_node("clientes_tools", clientes_tool_node)

# el nodo inicial es el agente
workflow.add_edge(START, "agent")

# condicionamos el siguiente nodo: según los tool_calls, ir a "sql_tools", "clientes_tools" o END
workflow.add_conditional_edges("agent", route_after_agent,
                               {
        "sql_tools": "sql_tools",
        "clientes_tools": "clientes_tools",
        END: END
    })

# siempre volvemos al agente
workflow.add_edge("sql_tools", "agent")
workflow.add_edge("clientes_tools", "agent")

# ==========================================
# compilamos el grafo para que sea ejecutable
# ==========================================
graph = workflow.compile()