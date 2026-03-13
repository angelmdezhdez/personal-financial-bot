import sqlite3
import os
import datetime as dt
from langchain_core.tools import tool

# ==========================================
# Tool 1.
# ==========================================
@tool
def registrar_gasto(concepto: str, monto: float, medio: str) -> str:
    """
    Registra un nuevo gasto en la base de datos local.
    Es la herramienta principal para llevar el control de gastos personal.
    
    Args:
        concepto (str): Una breve descripción del gasto (ej. 'Compra de materiales', 'Pago de servicios').
        monto (float): El monto del gasto en dólares.
        medio (str): El medio de pago utilizado (ej. 'Tarjeta de crédito', 'Efectivo').
    """
    
    db_path = 'data/finanzas.db'
    
    if not os.path.exists(db_path):
        return "Error: La base de datos no existe. Por favor, ejecuta el script de configuración primero."
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        fecha_actual = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("INSERT INTO gastos (Concepto, Monto, Medio, Fecha) VALUES (?, ?, ?, ?)", 
                       (concepto, monto, medio, fecha_actual))
        conn.commit()
        conn.close()
        
        return f"Gasto registrado exitosamente: {concepto} por ${monto} pagado con {medio} el {fecha_actual}. Recuerda responder con el dinero disponible para la semana."
    
    except sqlite3.Error as e:
        return f"Error al registrar el gasto en la base de datos: {str(e)}"


# ==========================================
# Tool 2.
# ==========================================
@tool
def actualizar_saldos(nuevos_saldos: dict) -> str:
    """
    Actualiza los saldos de las cuentas en la base de datos local.
    Útil para mantener un control actualizado de los fondos disponibles en cada cuenta.
    
    Args:
        nuevos_saldos (dict): Un diccionario con el nombre de la cuenta como clave y el nuevo saldo como valor. 
                              Ejemplo: {'Cuenta Ahorros': 1500.00, 'Cuenta Corriente': 500.00}
    """
    
    db_path = 'data/finanzas.db'
    
    if not os.path.exists(db_path):
        return "Error: La base de datos no existe. Por favor, ejecuta el script de configuración primero."
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        fecha_actual = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for cuenta, saldo in nuevos_saldos.items():
            cursor.execute("UPDATE saldos SET Saldo = ? WHERE Nombre = ?", (saldo, cuenta))
        
        conn.commit()
        conn.close()
        
        return "Saldos actualizados exitosamente en la base de datos el " + fecha_actual + "."
    
    except sqlite3.Error as e:
        return f"Error al actualizar los saldos en la base de datos: {str(e)}"

# ==========================================
# Tool 3.
# ==========================================
@tool
def actualizar_presupuesto(monto: float) -> str:
    """
    Actualiza el presupuesto semanal en la base de datos local.
    Es útil para ajustar el presupuesto disponible después de registrar gastos o cambios en los ingresos.
    
    Args:
        monto (float): El nuevo monto del presupuesto semanal en dólares.
    """
    
    db_path = 'data/finanzas.db'
    
    if not os.path.exists(db_path):
        return "Error: La base de datos no existe. Por favor, ejecuta el script de configuración primero."
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        fecha_actual = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("UPDATE presupuesto SET Monto = ? WHERE Id = 1", (monto,))
        
        conn.commit()
        conn.close()
        
        return f"Presupuesto semanal actualizado exitosamente a ${monto} el {fecha_actual}."
    
    except sqlite3.Error as e:
        return f"Error al actualizar el presupuesto en la base de datos: {str(e)}"

    

# ==========================================
# Tool 4.
# ==========================================
@tool
def obtener_saldos() -> dict:
    """
    Obtiene los saldos actuales de las cuentas desde la base de datos local.
    Es útil para mostrar al usuario el estado actual de sus finanzas antes de registrar nuevos gastos o ajustar el presupuesto.
    
    Returns:
        dict: Un diccionario con el nombre de la cuenta como clave y el saldo actual como valor. 
              Ejemplo: {'Cuenta Ahorros': 1500.00, 'Cuenta Corriente': 500.00}
    """
    
    db_path = 'data/finanzas.db'
    
    if not os.path.exists(db_path):
        return {"error": "La base de datos no existe. Por favor, ejecuta el script de configuración primero."}
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT Nombre, Saldo FROM saldos")
        resultados = cursor.fetchall()
        conn.close()
        
        saldos = {nombre: saldo for nombre, saldo in resultados}
        return saldos
    
    except sqlite3.Error as e:
        return {"error": f"Error al obtener los saldos de la base de datos: {str(e)}"}
    
# ==========================================
# Tool 5.
# ==========================================
@tool
def actualizar_deuda(monto: float, medio: str) -> str:
    """
    Actualiza el monto de la deuda actual en la base de datos local.
    Es útil para mantener un control actualizado de las deudas pendientes después de realizar pagos o incurrir en nuevas deudas.
    
    Args:
        monto (float): El nuevo monto total de la deuda en dólares.
        medio (str): El medio relacionado con la deuda (ej. 'Tarjeta de crédito', 'Préstamo personal').
    """
    
    db_path = 'data/finanzas.db'
    
    if not os.path.exists(db_path):
        return "Error: La base de datos no existe. Por favor, ejecuta el script de configuración primero."
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        fecha_actual = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("UPDATE deudas SET Monto = ? WHERE Medio = ?", (monto, medio))
        
        conn.commit()
        conn.close()
        
        return f"Deuda actualizada exitosamente a ${monto} para {medio} el {fecha_actual}."
    
    except sqlite3.Error as e:
        return f"Error al actualizar la deuda en la base de datos: {str(e)}"