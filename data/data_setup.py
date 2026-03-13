import sqlite3
import csv
import datetime as dt

def create_csv_data():
    with open("data/gastos.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Fecha", "Concepto", "Monto", "Medio"])
        writer.writerow([dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Compra inicial", 0.0, "BBVA Crédito"])


    with open("data/saldos.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Nombre", "Saldo"])
        writer.writerow(["BBVA Débito", 3000])
        writer.writerow(["Nu Turbo", 25000])
        writer.writerow(["Stori Inversion", 5000])
        writer.writerow(["MP Ahorros", 9116])
        writer.writerow(["MP Dentista", 2500])
        writer.writerow(["MP Terapia", 900])
        writer.writerow(["MP Gastos Fijos", 2240])

    with open("data/presupuesto.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Monto"])
        writer.writerow([400])

    with open("data/deudas.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Medio", "Monto"])
        writer.writerow(["BBVA Crédito", 0])
        writer.writerow(["Nu Crédito", 0])
        writer.writerow(["Stori Crédito", 0])
        writer.writerow(["MP Crédito", 0])


def configurar_base_datos(gastos_csv="data/gastos.csv", saldos_csv="data/saldos.csv", presupuesto_csv="data/presupuesto.csv"):
    conn = sqlite3.connect("data/finanzas.db")
    cursor = conn.cursor()

    gastos = []
    with open(gastos_csv, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            gastos.append((row["Fecha"], row["Concepto"], float(row["Monto"]), row["Medio"]))
    saldos = []
    with open(saldos_csv, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            saldos.append((row["Nombre"], float(row["Saldo"])))
    presupuesto = []
    with open(presupuesto_csv, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            presupuesto.append((float(row["Monto"]),))
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS gastos 
                      (id INTEGER PRIMARY KEY, Fecha TEXT, Concepto TEXT, Monto REAL, Medio TEXT)''')

    cursor.executemany('INSERT INTO gastos (Fecha, Concepto, Monto, Medio) VALUES (?, ?, ?, ?)', gastos)

    cursor.execute('''CREATE TABLE IF NOT EXISTS saldos 
                      (id INTEGER PRIMARY KEY, Nombre TEXT, Saldo REAL)''')
    
    cursor.executemany('INSERT INTO saldos (Nombre, Saldo) VALUES (?, ?)', saldos)

    cursor.execute('''CREATE TABLE IF NOT EXISTS presupuesto 
                      (id INTEGER PRIMARY KEY, Monto REAL)''')

    cursor.executemany('INSERT INTO presupuesto (Monto) VALUES (?)', presupuesto)

    cursor.execute('''CREATE TABLE IF NOT EXISTS deudas 
                      (id INTEGER PRIMARY KEY, Medio TEXT, Monto REAL)''')
    
    cursor.executemany('INSERT INTO deudas (Medio, Monto) VALUES (?, ?)', [("BBVA Crédito", 0), ("Nu Crédito", 0), ("Stori Crédito", 0), ("MP Crédito", 0)])
    conn.commit()
    conn.close()
    print("Database 'finanzas.db' created and populated successfully.")



if __name__ == "__main__":
    create_csv_data()
    configurar_base_datos()