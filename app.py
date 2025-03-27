import tkinter as tk
from tkinter import ttk, messagebox
from pymongo import MongoClient
import json
from tkinter import filedialog

# Conectar a MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["biblioteca"]

# Crear índices para optimizar búsquedas
db.libros.create_index([("titulo", 1)])
db.usuarios.create_index([("nombre", 1)])

# Función para cargar libros (con filtro opcional)
def cargar_libros(filtro=None):
    for row in tree_libros.get_children():
        tree_libros.delete(row)

    query = {} if filtro is None else {"titulo": {"$regex": filtro, "$options": "i"}}
    libros = db.libros.find(query, {"_id": 0, "titulo": 1, "autor": 1, "genero": 1, "disponible": 1})

    for libro in libros:
        disponible = "Sí" if libro.get("disponible", False) else "No"
        tree_libros.insert("", "end", values=(libro["titulo"], libro["autor"], libro["genero"], disponible))

def hacer_respaldo():
    # Obtener todos los libros y usuarios
    libros = list(db.libros.find({}, {"_id": 0}))  # Excluir el campo _id
    usuarios = list(db.usuarios.find({}, {"_id": 0}))

    # Crear el diccionario con los datos
    respaldo = {
        "libros": libros,
        "usuarios": usuarios
    }

    # Abrir el cuadro de diálogo para elegir dónde guardar el archivo
    archivo = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("Archivos JSON", "*.json")],
        title="Guardar Respaldo"
    )

    if archivo:
        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(respaldo, f, ensure_ascii=False, indent=4)

        messagebox.showinfo("Respaldo Completo", "El respaldo se ha guardado correctamente.")

# Función para buscar libros por título
def buscar_libros():
    filtro = entry_buscar_libro.get().strip()
    cargar_libros(filtro)

# Función para cargar usuarios (con filtro opcional)
def cargar_usuarios(filtro=None):
    for row in tree_usuarios.get_children():
        tree_usuarios.delete(row)

    query = {} if filtro is None else {"nombre": {"$regex": filtro, "$options": "i"}}
    usuarios = db.usuarios.find(query, {"_id": 0, "nombre": 1, "correo": 1, "prestamos": 1})

    for usuario in usuarios:
        tree_usuarios.insert("", "end", values=(
            usuario.get("nombre", "Desconocido"),
            usuario.get("correo", "Sin correo"),
            len(usuario.get("prestamos", []))
        ))

# Función para buscar usuarios por nombre
def buscar_usuarios():
    filtro = entry_buscar_usuario.get().strip()
    cargar_usuarios(filtro)

# Función para agregar un nuevo usuario
def agregar_usuario():
    nombre = entry_nombre.get().strip()
    correo = entry_correo.get().strip()

    if not nombre or not correo:
        messagebox.showwarning("Campos vacíos", "Por favor, ingresa un nombre y un correo.")
        return

    if db.usuarios.find_one({"correo": correo}):
        messagebox.showerror("Error", "Este correo ya está registrado.")
        return

    nuevo_usuario = {"nombre": nombre, "correo": correo, "prestamos": []}
    db.usuarios.insert_one(nuevo_usuario)

    messagebox.showinfo("Usuario Creado", f"Cuenta creada para {nombre}.")
    entry_nombre.delete(0, tk.END)
    entry_correo.delete(0, tk.END)
    cargar_usuarios()

# Función para agregar un nuevo libro
def agregar_libro():
    titulo = entry_titulo.get().strip()
    autor = entry_autor.get().strip()
    genero = entry_genero.get().strip()
    disponible = var_disponible.get()

    if not titulo or not autor or not genero:
        messagebox.showwarning("Campos vacíos", "Completa todos los campos.")
        return

    nuevo_libro = {"titulo": titulo, "autor": autor, "genero": genero, "disponible": disponible}
    db.libros.insert_one(nuevo_libro)

    messagebox.showinfo("Libro Agregado", f"Libro '{titulo}' agregado correctamente.")
    entry_titulo.delete(0, tk.END)
    entry_autor.delete(0, tk.END)
    entry_genero.delete(0, tk.END)
    var_disponible.set(False)
    cargar_libros()

# Función para mostrar índices en la base de datos
def mostrar_indices():
    indices_libros = db.libros.index_information()
    indices_usuarios = db.usuarios.index_information()

    mensaje = "📚 Índices en Libros:\n" + str(indices_libros) + "\n\n👤 Índices en Usuarios:\n" + str(indices_usuarios)
    messagebox.showinfo("Índices en la Base de Datos", mensaje)

# Interfaz gráfica con Tkinter
root = tk.Tk()
root.title("Gestión de Biblioteca")
root.geometry("800x600")

notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both")

# ---- PESTAÑA LIBROS ----
frame_libros = ttk.Frame(notebook)
notebook.add(frame_libros, text="Libros")

# Buscador de libros
frame_busqueda_libros = ttk.LabelFrame(frame_libros, text="Buscar Libro")
frame_busqueda_libros.pack(pady=10, padx=10, fill="x")

ttk.Label(frame_busqueda_libros, text="Título:").grid(row=0, column=0, padx=5, pady=5)
entry_buscar_libro = ttk.Entry(frame_busqueda_libros)
entry_buscar_libro.grid(row=0, column=1, padx=5, pady=5)
ttk.Button(frame_busqueda_libros, text="Buscar", command=buscar_libros).grid(row=0, column=2, padx=5, pady=5)

tree_libros = ttk.Treeview(frame_libros, columns=("Título", "Autor", "Género", "Disponible"), show="headings")
for col in ("Título", "Autor", "Género", "Disponible"):
    tree_libros.heading(col, text=col)
tree_libros.pack(pady=10, padx=10, fill="both", expand=True)

# Formulario para agregar libros
frame_agregar_libro = ttk.LabelFrame(frame_libros, text="Agregar Nuevo Libro")
frame_agregar_libro.pack(pady=10, padx=10, fill="x")

ttk.Label(frame_agregar_libro, text="Título:").grid(row=0, column=0, padx=5, pady=5)
entry_titulo = ttk.Entry(frame_agregar_libro)
entry_titulo.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(frame_agregar_libro, text="Autor:").grid(row=1, column=0, padx=5, pady=5)
entry_autor = ttk.Entry(frame_agregar_libro)
entry_autor.grid(row=1, column=1, padx=5, pady=5)

ttk.Label(frame_agregar_libro, text="Género:").grid(row=2, column=0, padx=5, pady=5)
entry_genero = ttk.Entry(frame_agregar_libro)
entry_genero.grid(row=2, column=1, padx=5, pady=5)

var_disponible = tk.BooleanVar()
chk_disponible = ttk.Checkbutton(frame_agregar_libro, text="Disponible", variable=var_disponible)
chk_disponible.grid(row=3, columnspan=2, pady=5)

ttk.Button(frame_agregar_libro, text="Agregar Libro", command=agregar_libro).grid(row=4, columnspan=2, pady=5)

# ---- PESTAÑA USUARIOS ----
frame_usuarios = ttk.Frame(notebook)
notebook.add(frame_usuarios, text="Usuarios")

frame_busqueda_usuarios = ttk.LabelFrame(frame_usuarios, text="Buscar Usuario")
frame_busqueda_usuarios.pack(pady=10, padx=10, fill="x")

ttk.Label(frame_busqueda_usuarios, text="Nombre:").grid(row=0, column=0, padx=5, pady=5)
entry_buscar_usuario = ttk.Entry(frame_busqueda_usuarios)
entry_buscar_usuario.grid(row=0, column=1, padx=5, pady=5)
ttk.Button(frame_busqueda_usuarios, text="Buscar", command=buscar_usuarios).grid(row=0, column=2, padx=5, pady=5)

tree_usuarios = ttk.Treeview(frame_usuarios, columns=("Nombre", "Correo", "Préstamos"), show="headings")
for col in ("Nombre", "Correo", "Préstamos"):
    tree_usuarios.heading(col, text=col)
tree_usuarios.pack(pady=10, padx=10, fill="both", expand=True)

ttk.Button(root, text="Ver Índices", command=mostrar_indices).pack(pady=10)
ttk.Button(root, text="Hacer Respaldo", command=hacer_respaldo).pack(pady=5)

cargar_libros()
cargar_usuarios()
root.mainloop()
