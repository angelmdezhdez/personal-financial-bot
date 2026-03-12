import sqlite3
import csv
import random

def create_csv_data():
    prices = [[1200, 1500, 1600, 1700], [300, 350, 400, 450], [150, 180, 200, 220], [200, 250, 300, 350]]
    products = ['Laptop', 'Monitor', 'Silla', 'Escritorio']
    brands = ['Marca A', 'Marca B', 'Marca C', 'Marca D']
    departments = ['Electrónica', 'Oficina', 'Hogar']

    with open("data/products.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Nombre", "Marca", "Departamento", "Precio", "Stock"])
        for i in range(len(products)):
            for j in range(len(brands)):
                for k in range(len(departments)):
                    writer.writerow([f"{products[i]}", brands[j], departments[k], prices[i][j], random.randint(5, 20) + i + j + k])

    clients = [
                ('Ana Lopez', 'TechCorp', 'ana@techcorp.com', '555-0101'),
                ('Carlos Ruiz', 'Soluciones Globales', 'carlos@sglobal.com', '555-0202'),
                ('Carlos Slim', 'Telmex', 'carlos@telmex.com', '555-9999'), 
                ('Maria Gomez', 'Innovación SA', 'maria@innovacion.mx', '555-0303'),
                ('Luis Fernandez', 'TechCorp', 'luis@techcorp.com', '555-0404'),
                ('Sofia Martinez', 'Soluciones Globales', 'sofia@sglobal.com', '555-0505'),
                ('Jorge Ramirez', 'Telmex', 'jorge@telmex.com', '555-0606'),
                ('Laura Sanchez', 'Innovación SA', 'laura@innovacion.mx', '555-0707'),
                ('Pedro Gonzalez', 'TechCorp', 'pedro@techcorp.com', '555-0808'),
                ('Lucia Torres', 'Soluciones Globales', 'lucia@sglobal.com', '555-0909'),
                ('Diego Flores', 'Telmex', 'diego@telmex.com', '555-1010')
    ]
    with open("data/clients.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Nombre", "Empresa", "Email", "Telefono"])
        writer.writerows(clients)
    print('Csv files "products.csv" and "clients.csv" created successfully.')


def configurar_base_datos(products_csv="data/products.csv", clients_csv="data/clients.csv"):
    conn = sqlite3.connect("data/inventario.db")
    cursor = conn.cursor()

    productos = []
    with open(products_csv, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            productos.append((row["Nombre"], row["Departamento"], float(row["Precio"]), int(row["Stock"])))
    clientes = []
    with open(clients_csv, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            clientes.append((row["Nombre"], row["Empresa"], row["Email"], row["Telefono"]))
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS productos 
                      (id INTEGER PRIMARY KEY, nombre TEXT, categoria TEXT, precio REAL, stock INTEGER)''')

    cursor.executemany('INSERT INTO productos (nombre, categoria, precio, stock) VALUES (?, ?, ?, ?)', productos)

    cursor.execute('''CREATE TABLE IF NOT EXISTS clientes 
                      (id INTEGER PRIMARY KEY, nombre TEXT, empresa TEXT, email TEXT, telefono TEXT)''')

    cursor.executemany('INSERT INTO clientes (nombre, empresa, email, telefono) VALUES (?, ?, ?, ?)', clientes)
    
    conn.commit()
    conn.close()
    print("Database 'inventario.db' created and populated successfully.")



if __name__ == "__main__":
    create_csv_data()
    configurar_base_datos()