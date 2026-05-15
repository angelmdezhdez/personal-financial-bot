from dotenv import load_dotenv
load_dotenv()  
import sqlite3
import os
import datetime as dt
from langchain_core.tools import tool

db_path = os.getenv("DB_PATH")

# Funciones auxiliares

def _actualizar_presupuesto_logic(monto_a_restar: float) -> str:
    """Lógica interna para restar del presupuesto semanal"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Primero obtenemos el presupuesto actual para restarle
        cursor.execute("SELECT Monto FROM presupuesto")
        actual = cursor.fetchone()[0]
        nuevo_monto = actual - monto_a_restar
        
        cursor.execute("UPDATE presupuesto SET Monto = ?", (nuevo_monto,))
        conn.commit()
        conn.close()
        return f"Presupuesto actualizado. Restante: ${nuevo_monto}."
    except Exception as e:
        return f"Error al actualizar presupuesto: {e}"
    
def _actualizar_adeudos_logic(monto_a_sumar: float, medio: str) -> str:
    """Lógica interna para sumar al monto de una deuda específica"""
    if not os.path.exists(db_path):
        return "Error: DB no existe."
    
    # Validamos el medio para evitar alucinaciones
    if medio.lower().__contains__('bbva'):
        medio = 'BBVA Crédito'
    elif medio.lower().__contains__('nu'):
        medio = 'Nu Crédito'
    elif medio.lower().__contains__('stori'):
        medio = 'Stori Crédito'
    elif medio.lower().__contains__('mp'):
        medio = 'MP Crédito'
    else:
        return f"Error: Medio '{medio}' no reconocido. Por favor, usa un medio válido como 'BBVA Crédito', 'Nu Crédito', 'Stori Crédito' o 'MP Crédito'."

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Primero obtenemos el monto actual de la deuda para sumarle
        cursor.execute("SELECT Monto FROM deudas WHERE Medio = ?", (medio,))
        resultado = cursor.fetchone()
        if resultado is None:
            return f"Error: No se encontró una deuda con el medio '{medio}'."
        
        actual = resultado[0]
        nuevo_monto = actual + monto_a_sumar
        
        cursor.execute("UPDATE deudas SET Monto = ? WHERE Medio = ?", (nuevo_monto, medio))
        conn.commit()
        conn.close()
        return f"Deuda '{medio}' actualizada. Nuevo monto: ${nuevo_monto}."
    except Exception as e:
        return f"Error al actualizar deuda: {e}"
    

def reestablecer_presupuesto_semanal(presupuesto_inicial: float) -> str:
    """
    Reestablece el presupuesto semanal al monto inicial definido en la base de datos local.
    Esta función se ejecuta automáticamente cada semana para asegurar que el presupuesto se reinicie y el usuario pueda comenzar con un nuevo ciclo de gastos.
    Args:
        presupuesto_inicial (float): El monto inicial del presupuesto semanal definido por el usuario
    """
    
    db_path = os.getenv("DB_PATH")
    
    if not os.path.exists(db_path):
        return "Error: La base de datos no existe. Por favor, ejecuta el script de configuración primero."
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # actualizar el presupuesto semanal al monto inicial
        cursor.execute("UPDATE presupuesto SET Monto = ?", (presupuesto_inicial,))
        conn.commit()
        conn.close()
        return f"Presupuesto semanal reestablecido exitosamente a ${presupuesto_inicial} el {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}."    
    except sqlite3.Error as e:
        return f"Error al reestablecer el presupuesto en la base de datos: {str(e)}"


# ==========================================
# Tool 1.
# ==========================================
@tool
def registrar_gasto(concepto: str, monto: float, medio: str) -> str:
    """Registra un gasto y descuenta del presupuesto semanal."""
    if not os.path.exists(db_path):
        return "Error: DB no existe."
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        fecha_actual = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO gastos (Concepto, Monto, Medio, Fecha) VALUES (?, ?, ?, ?)", 
                       (concepto, monto, medio, fecha_actual))
        conn.commit()
        conn.close()

        # LLAMAMOS A LA LÓGICA, NO A LA TOOL
        res_presupuesto = _actualizar_presupuesto_logic(monto)
        if medio.lower().__contains__('transferencia') or medio.lower().__contains__('efectivo'):
            res_adeudo = "Por ser un gasto en efectivo o transferencia, no se actualizan adeudos."
        else:
            res_adeudo = _actualizar_adeudos_logic(monto, medio)

        return f"Gasto guardado: {concepto} (${monto}). {res_presupuesto} {res_adeudo}"
    except sqlite3.Error as e:
        return f"Error DB: {str(e)}"
    
# ==========================================
# Tool 2.
# ==========================================
@tool
def actualizar_saldos(nuevos_saldos: dict) -> str:
    """
    Actualiza los saldos de las cuentas en la base de datos local.
    """
    db_path = os.getenv("DB_PATH")
    if not os.path.exists(db_path):
        return "Error: La base de datos no existe."

    # Diccionario de palabras clave -> Nombre real en DB
    mapeo_cuentas = {
        "nu": "Nu Turbo", "turbo": "Nu Turbo",
        "bbva": "BBVA Débito",
        "stori": "Stori Inversion",
        "ahorro": "MP Ahorros",
        "dentista": "MP Dentista",
        "terapia": "MP Terapia",
        "gastos": "MP Gastos Fijos"
    }

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        fecha_actual = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cuentas_actualizadas = []

        for cuenta_input, saldo in nuevos_saldos.items():
            nombre_input_clean = cuenta_input.lower()
            cuenta_real = None

            # Buscamos si alguna palabra clave coincide
            for clave, nombre_db in mapeo_cuentas.items():
                if clave in nombre_input_clean:
                    cuenta_real = nombre_db
                    break 

            if not cuenta_real:
                return f"Error: No reconocí la cuenta '{cuenta_input}'. Intenta con nombres claros."

            # IMPORTANTE: Usamos 'cuenta_real' en el WHERE
            cursor.execute("UPDATE saldos SET Saldo = ? WHERE Nombre = ?", (saldo, cuenta_real))
            
            if cursor.rowcount == 0:
                return f"Error: La cuenta '{cuenta_real}' no existe en la tabla 'saldos'."
            
            cuentas_actualizadas.append(cuenta_real)

        conn.commit()
        conn.close()
        
        return f"Saldos actualizados ({', '.join(cuentas_actualizadas)}) el {fecha_actual}."
    
    except sqlite3.Error as e:
        return f"Error de base de datos: {str(e)}"

# ==========================================
# Tool 3.
# ==========================================
@tool
def actualizar_presupuesto(monto_total: float) -> str:
    """Establece un nuevo monto TOTAL para el presupuesto semanal."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE presupuesto SET Monto = ?", (monto_total,))
        conn.commit()
        conn.close()
        return f"Presupuesto total ajustado a ${monto_total}."
    except sqlite3.Error as e:
        return f"Error: {e}"
    

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
    
    db_path = os.getenv("DB_PATH")
    
    if not os.path.exists(db_path):
        return {"error": "La base de datos no existe. Por favor, ejecuta el script de configuración primero."}
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT Nombre, Saldo FROM saldos")
        resultados = cursor.fetchall()
        cursor.execute("SELECT Monto FROM presupuesto")
        presupuesto_result = cursor.fetchone()
        if presupuesto_result:
            presupuesto_actual = presupuesto_result[0]
            resultados.append(("Presupuesto Semanal", presupuesto_actual))
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
    
    db_path = os.getenv("DB_PATH")
    
    if not os.path.exists(db_path):
        return "Error: La base de datos no existe. Por favor, ejecuta el script de configuración primero."
    
    # Vamos a prevenir alucionaciones validando el medio
    if medio.lower().__contains__('bbva'):
        medio = 'BBVA Crédito'
    elif medio.lower().__contains__('nu'):
        medio = 'Nu Crédito'
    elif medio.lower().__contains__('stori'):
        medio = 'Stori Crédito'
    elif medio.lower().__contains__('mp'):
        medio = 'MP Crédito'
    else:
        return f"Error: Medio '{medio}' no reconocido. Por favor, usa un medio válido como 'BBVA Crédito', 'Nu Crédito', 'Stori Crédito' o 'MP Crédito'."
    
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
    
# ==========================================
# Tool 6.
# ==========================================
@tool
def obtener_deudas() -> dict:
    """
    Obtiene los montos actuales de las deudas desde la base de datos local.
    Es útil para mostrar al usuario el estado actual de sus deudas antes de realizar pagos o incurrir en nuevas deudas.
    
    Returns:
        dict: Un diccionario con el medio como clave y el monto de la deuda como valor. 
              Ejemplo: {'Tarjeta de crédito': 2000.00, 'Préstamo personal': 5000.00}
    """
    
    db_path = os.getenv("DB_PATH")
    
    if not os.path.exists(db_path):
        return {"error": "La base de datos no existe. Por favor, ejecuta el script de configuración primero."}
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT Medio, Monto FROM deudas")
        resultados = cursor.fetchall()
        conn.close()
        
        deudas = {medio: monto for medio, monto in resultados}
        return deudas
    
    except sqlite3.Error as e:
        return {"error": f"Error al obtener las deudas de la base de datos: {str(e)}"}