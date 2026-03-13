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
    obtener_saldos,
    actualizar_deuda
)

# ==========================================
# Primeros settings y definiciones
# ==========================================

tools_compras = [registrar_gasto, actualizar_presupuesto, actualizar_deuda]
TOOLS_COMPRAS_NAMES = [tool.name for tool in tools_compras]
tools_saldos = [obtener_saldos, actualizar_saldos]

# tools son herramientas "genéricas" que el agente puede usar
tools = tools_compras + tools_saldos

# usamos este modelo de Google Gemini, que es un modelo de propósito general muy capaz para agentes conversacionales 
# y que es rápido y económico. 
llm = ChatGoogleGenerativeAI(model="gemini-3-flash-preview", temperature=0.3)

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
        SystemMessage(content=f"""Eres un asistente de contabilidad altamente eficiente. 
        Tienes acceso a bases de datos de gastos, saldos y presupuesto.
        Usa las herramientas a tu disposición para responder a las solicitudes del usuario.
        Si no sabes la respuesta o la herramienta falla, admítelo y pide aclaraciones.
        La fecha actual es {fecha_hoy}.""")
    ] + state["messages"]
    
    # invocamos al modelo con tools
    response = llm_with_tools.invoke(mensajes)
    
    # devolvemos la respuesta del modelo
    return {"messages": [response]}

# Nodo de herramientas principales más usadas para compras (registro de gastos, actualización de presupuesto y deuda)
tool_node = ToolNode(tools=tools_compras)
# Nodo de herramientas de saldos y presupuesto
saldos_tool_node = ToolNode(tools=tools_saldos)

# ==========================================
# Definimos el flujo
# ==========================================

def route_after_agent(state: MessagesState):
    """
    Decide a qué nodo ir después del agente:
    - Si el LLM no pidió ninguna herramienta -> terminar (END).
    - Si se registró un gasto -> nodo "sql_tools".
    - Si pidió actualizar o saber saldos -> nodo "saldos".
    """
    ultimo_mensaje = state["messages"][-1]
    herramientas_solicitadas = getattr(ultimo_mensaje, "tool_calls", None)

    # si ya no se solicitan herramientas, terminamos la ejecución (END)
    if not herramientas_solicitadas:
        return END

    # qué herramientas se solicitaron en el último mensaje
    nombres_herramientas = {llamada["name"] for llamada in ultimo_mensaje.tool_calls}

    # Si se registró un gasto -> nodo "sql_tools".
    # Si pidió actualizar o saber saldos -> nodo "saldos".
    is_about_compras = any(
        nombre in TOOLS_COMPRAS_NAMES for nombre in nombres_herramientas
    )
    if is_about_compras:
        return "sql_tools"
    return "saldos_tool_node"

# definimos el grafo de estados
workflow = StateGraph(MessagesState)

# Agregamos el nodo del agente y los dos nodos de herramientas
workflow.add_node("agent", chatbot_node)
workflow.add_node("sql_tools", tool_node)
workflow.add_node("saldos_tool_node", saldos_tool_node)

# el nodo inicial es el agente
workflow.add_edge(START, "agent")

# condicionamos el siguiente nodo: según los tool_calls, ir a "sql_tools", "saldos_tool_node" o END
workflow.add_conditional_edges("agent", route_after_agent,
                               {
        "sql_tools": "sql_tools",
        "saldos_tool_node": "saldos_tool_node",
        END: END
    })

# siempre volvemos al agente
workflow.add_edge("sql_tools", "agent")
workflow.add_edge("saldos_tool_node", "agent")

# ==========================================
# compilamos el grafo para que sea ejecutable
# ==========================================
graph = workflow.compile()