import tkinter as tk
from tkinter import messagebox, ttk
import mariadb
import bcrypt
from tkcalendar import DateEntry
from datetime import datetime
import re


# --- Configuración de la Base de Datos ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '', # ¡Cambia esto a con la contraseña de acceso a MariaDB!
    'database': 'crud_db'
}

# --- Funciones de la Base de Datos ---
def get_db_connection():
    try:
        conn = mariadb.connect(**DB_CONFIG)
        return conn
    except mariadb.Error as e:
        messagebox.showerror("Error de Conexión a DB", f"Error al conectar a MariaDB: {e}")
        return None

def create_table():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    tipo_identificacion ENUM('CC', 'NIT', 'PAS', 'CE') NOT NULL,
                    numero_identificacion VARCHAR(255) NOT NULL,
                    nombre VARCHAR(255) NOT NULL,
                    apellido VARCHAR(255) NOT NULL,
                    direccion VARCHAR(255),
                    fecha_nacimiento DATE,
                    correo VARCHAR(255) NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    telefono VARCHAR(40)
                );
            """)
            conn.commit()
            print("Tabla 'users' creada o ya existe.")
        except mariadb.Error as e:
            print(f"Error al crear la tabla: {e}")
        finally:
            cursor.close()
            conn.close()

def hash_password(password):
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')

def validar_obligatorio(valor, campo):
    if not valor:
        messagebox.showerror("Error", f"El campo '{campo}' es obligatorio.")
        return False
    return True

def validar_telefono(numero):
    patron = r'^(\+\d{1,3}\s?)?\d{7,15}(\s?(ext\.?|extensión)\s?\d+)?$'
    return re.match(patron, numero) is not None

def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def validar_correo(correo):
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(patron, correo) is not None

def insert_user(tipo_identificacion, numero_identificacion,nombre, apellido, correo, password, direccion=None,  fecha_nacimiento=None, telefono=None):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            hashed_password = hash_password(password) 
            
            # Sentencia SQL           
            cursor.execute("""
                INSERT INTO users (
                    tipo_identificacion,
                    numero_identificacion,
                    nombre,
                    apellido,
                    direccion,
                    fecha_nacimiento,
                    correo,
                    password_password_hash,
                    telefono
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (tipo_identificacion, numero_identificacion, nombre, apellido, direccion, telefono, fecha_nacimiento, correo, hashed_password))
                
            conn.commit()
            messagebox.showinfo("Éxito", "Usuario insertado correctamente.")
            return True
        except mariadb.Error as e:
            messagebox.showerror("Error", f"Error al insertar usuario: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

def get_users():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, tipo_identificacion, numero_identificacion, nombre, apellido FROM users")
            users = cursor.fetchall()
            return users
        except mariadb.Error as e:
            messagebox.showerror("Error", f"Error al obtener usuarios: {e}")
            return []
        finally:
            cursor.close()
            conn.close()            

def get_user_by_id(user_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, tipo_identificacion, numero_identificacion, nombre, apellido FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            return user
        except mariadb.Error as e:
            messagebox.showerror("Error", f"Error al obtener usuario por ID: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

def get_user_by_identification(tipo_identificacion, numero_identificacion):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor() 
        try:
            cursor.execute("""
                SELECT id, fecha_nacimiento, correo, password_hash
                FROM users
                WHERE tipo_identificacion = ? AND numero_identificacion = ?
            """, (tipo_identificacion, numero_identificacion))
            usuario = cursor.fetchone()
            return usuario
        except mariadb.Error as e:
            messagebox.showerror('Error', f'Error al obtener usuario: {e}')
            return None
        finally:
            cursor.close()
            conn.close()

def update_user(user_id, tipo_identificacion, numero_identificacion, nombre, apellido, correo, 
                direccion=None, telefono=None, fecha_nacimiento=None, password=None):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            if password:
                hashed_password = hash_password(password)
                cursor.execute("""
                    UPDATE users SET 
                        tipo_identificacion = ?,
                        numero_identificacion = ?,
                        nombre = ?,
                        apellido = ?,
                        direccion = ?,
                        telefono = ?,
                        fecha_nacimiento = ?,
                        correo = ?,
                        password_hash = ?
                    WHERE id = ?
                """, (tipo_identificacion, numero_identificacion, nombre, apellido, 
                      direccion, telefono, fecha_nacimiento, correo, hashed_password, user_id))
            else:                
                cursor.execute("""
                    UPDATE users SET 
                        tipo_identificacion = ?,
                        numero_identificacion = ?,
                        nombre = ?,
                        apellido = ?,
                        direccion = ?, 
                        fecha_nacimiento = ?,
                        correo = ?, 
                    WHERE id = ?
                    """, (tipo_identificacion, numero_identificacion, nombre, apellido, direccion, fecha_nacimiento, correo, user_id))
            conn.commit()
            messagebox.showinfo("Éxito", "Usuario actualizado correctamente.")
            return True
        except mariadb.Error as e:
            messagebox.showerror("Error", f"Error al actualizar usuario: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
          
def change_password(user_id, new_password) -> bool:
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            hashed_password = hash_password(new_password)
            cursor.execute(
                "UPDATE users SET password_hash = ? WHERE id = ?",
                (hashed_password, user_id)
            )
            conn.commit()
            messagebox.showinfo('Éxito', 'Contraseña actualizada correctamente.')
            return True
        except mariadb.Error as e:
            messagebox.showerror('Error', f'Error al cambiar contraseña: {e}')
            return False
        finally:
            cursor.close()
            conn.close()
def authenticate_user(correo, password):
    """Autentica un usuario por correo y contraseña"""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT id, password_hash, nombre, apellido FROM users WHERE correo = ?",
                (correo,)
            )
            user = cursor.fetchone()
            
            if user:
                user_id, password_hash, nombre, apellido = user
                if verify_password(password, password_hash):
                    return {
                        'id': user_id,
                        'nombre': nombre,
                        'apellido': apellido,
                        'correo': correo
                    }
            return None
        except mariadb.Error as e:
            messagebox.showerror('Error', f'Error al autenticar: {e}')
            return None
        finally:
            cursor.close()
            conn.close()
def delete_user(user_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            messagebox.showinfo("Éxito", "Usuario eliminado correctamente.")
            return True
        except mariadb.Error as e:
            messagebox.showerror("Error", f"Error al eliminar usuario: {e}")
            return False
        finally:
            cursor.close()
            conn.close()


# --- Interfaz Gráfica con Tkinter ---
class LoginWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Iniciar Sesión")
        self.master.geometry("400x300")
        self.master.resizable(False, False)
        
        self.center_window()
        self.user_data = None
        self.create_widgets()
    
    def center_window(self):
        self.master.update_idletasks()
        width = self.master.winfo_width()
        height = self.master.winfo_height()
        x = (self.master.winfo_screenwidth() // 2) - (width // 2)
        y = (self.master.winfo_screenheight() // 2) - (height // 2)
        self.master.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        # Frame principal
        main_frame = tk.Frame(self.master, padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')
        
        # Título
        title_label = tk.Label(
            main_frame,
            text="SISTEMA DE GESTIÓN DE USUARIOS",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Frame de formulario
        form_frame = tk.Frame(main_frame)
        form_frame.pack(expand=True)
        
        # Correo
        tk.Label(form_frame, text="Correo Electrónico:", font=("Arial", 10)).grid(
            row=0, column=0, pady=10, sticky="w"
        )
        self.correo_entry = tk.Entry(form_frame, width=30, font=("Arial", 10))
        self.correo_entry.grid(row=0, column=1, pady=10, padx=10)
        self.correo_entry.focus()
        
        # Contraseña
        tk.Label(form_frame, text="Contraseña:", font=("Arial", 10)).grid(
            row=1, column=0, pady=10, sticky="w"
        )
        self.password_entry = tk.Entry(form_frame, width=30, font=("Arial", 10), show="*")
        self.password_entry.grid(row=1, column=1, pady=10, padx=10)
        
        # Botones
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        tk.Button(
            button_frame,
            text="Iniciar Sesión",
            command=self.login,
            width=15,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold")
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Salir",
            command=self.master.quit,
            width=15,
            bg="#f44336",
            fg="white",
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=5)
    
    def login(self):
        # TODO: implementar
        pass
class UserApp:
    def __init__(self, master):
        self.master = master
        master.title("CRUD de Usuarios")
        master.geometry("800x600")

        self.create_widgets()
        self.load_users()

    def create_widgets(self):
        # Frame para entrada de datos
        input_frame = tk.LabelFrame(self.master, text="Gestión de Usuarios", padx=10, pady=10)
        input_frame.pack(padx=10, pady=10, fill="x")

        tk.Label(input_frame, text="ID (Solo para actualizar/eliminar):").grid(row=0, column=0, pady=5, sticky="w")
        self.id_entry = tk.Entry(input_frame)
        self.id_entry.grid(row=0, column=1, pady=5, sticky="ew")
        
        opciones_indentificaciones = ['CC', 'NIT', 'PAS', 'CE']

        tk.Label(input_frame, text="Tipo de identificación:").grid(row=1, column=0, pady=5, sticky="w")
        
        self.tipo_identificacion_var = tk.StringVar(self.master)
        self.tipo_identificacion_var.set(opciones_indentificaciones[0])

        self.tipo_identificacion_select = tk.OptionMenu(
            input_frame,
            self.tipo_identificacion_var,
            *opciones_indentificaciones
        )
        
        self.tipo_identificacion_select.grid(row=1, column=1, pady=5, sticky="ew", padx=10)
        
        input_frame.grid_columnconfigure(1, weight=1)
        
        tk.Button(self.master, text="Mostrar Selección", command=self.obtener_valor).pack(pady=10)
        
        tk.Label(input_frame, text="Número de identificación:").grid(row=2, column=0, pady=5, sticky="w")
        self.numero_identificacion_entry = tk.Entry(input_frame)
        self.numero_identificacion_entry.grid(row=2, column=1, pady=5, sticky="ew")
        
        tk.Label(input_frame, text="Nombre:").grid(row=3, column=0, pady=5, sticky="w")
        self.nombre_entry = tk.Entry(input_frame)
        self.nombre_entry.grid(row=3, column=1, pady=1, sticky="ew")
        
        tk.Label(input_frame, text="Apellido:").grid(row=4, column=0, pady=5, sticky="w")
        self.apellido_entry = tk.Entry(input_frame)
        self.apellido_entry.grid(row=4, column=1, pady=5, sticky="ew")

        tk.Label(input_frame, text="Fecha de Nacimiento:").grid(row=6, column=0, pady=5, sticky="w")
        self.fecha_nacimiento_entry = DateEntry(input_frame, selectmode='day', date_pattern='yyyy-mm-dd')
        self.fecha_nacimiento_entry.grid(row=6, column=1, pady=5, sticky="ew")

        tk.Label(input_frame, text="Correo:").grid(row=7, column=0, pady=5, sticky="w")
        self.correo_entry = tk.Entry(input_frame)
        self.correo_entry.grid(row=7, column=1, pady=5, sticky="ew")

        tk.Label(input_frame, text="Contraseña:").grid(row=8, column=0, pady=5, sticky="w")
        self.password_entry = tk.Entry(input_frame, show="*") # Oculta la contraseña
        self.password_entry.grid(row=8, column=1, pady=5, sticky="ew")
        
        tk.Label(input_frame, text="Telefono:").grid(row=9, column=0, pady=5, sticky="w")
        self.telefono_entry = tk.Entry(input_frame) 
        self.telefono_entry.grid(row=9, column=1, pady=5, sticky="ew")

        # Botones de acción
        button_frame = tk.Frame(input_frame)
        button_frame.grid(row=10, column=0, columnspan=2, pady=10)

        tk.Button(button_frame, text="Crear Usuario", command=self.add_user).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Actualizar Usuario", command=self.update_selected_user).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Eliminar Usuario", command=self.delete_selected_user).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Limpiar Campos", command=self.clear_fields).pack(side=tk.LEFT, padx=5)
        # --- Botón para salir ---
        tk.Button(button_frame, text="Salir", command=self.master.destroy, bg="red", fg="white").pack(side=tk.RIGHT, padx=15)


        # Treeview para mostrar usuarios
        self.tree = ttk.Treeview(self.master, columns=("ID", "Nombre", "Fecha de Nacimiento"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Fecha de Nacimiento", text="Fecha de Nacimiento")

        # Configuración de columnas (ancho)
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Nombre", width=200)
        self.tree.column("Fecha de Nacimiento", width=150, anchor="center")

        self.tree.pack(padx=10, pady=10, fill="both", expand=True)
        self.tree.bind("<ButtonRelease-1>", self.on_tree_select)

    def load_users(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        users = get_users()
        for user in users:
            self.tree.insert("", "end", values=user)
            
    def obtener_valor(self):
        # Función para obtener el valor seleccionado usando .get()
        valor = self.tipo_identificacion_var.get()
        print(f"El tipo de identificación seleccionado es: {valor}")
        
        return valor

    def add_user(self):
        tipo_identificacion = self.tipo_identificacion_var.get()
        numero_identificacion = self.numero_identificacion_entry.get().strip()
        nombre = self.nombre_entry.get().strip()
        apellido = self.apellido_entry.get().strip()
        fecha_nacimiento_str = self.fecha_nacimiento_entry.get_date().strftime('%Y-%m-%d')
        correo = self.correo_entry.get().strip()
        password = self.password_entry.get()
        telefono = self.telefono_entry.get().strip()

        if (
            not validar_obligatorio(numero_identificacion, 'número de identificación') or
            not validar_obligatorio(nombre, 'nombre') or
            not validar_obligatorio(apellido, 'apellido') or
            not validar_obligatorio(correo, 'correo') or
            not validar_obligatorio(password, 'password')
        ): return

        if insert_user(
                    tipo_identificacion,
                    numero_identificacion, 
                    nombre,
                    apellido,
                    correo,
                    password,
                    fecha_nacimiento_str,
                    telefono
                ):
            self.load_users()
            self.clear_fields()

    def update_selected_user(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Selección Requerida", "Por favor, seleccione un usuario de la tabla para actualizar.")
            return

        user_id = self.tree.item(selected_item)['values'][0]
        tipo_identificacion = self.tipo_identificacion_entry.get().strip()
        numero_identificacion = self.tipo_identificacion_var.get().strip()
        nombre = self.nombre_entry.get().strip()
        fecha_nacimiento_str = self.fecha_nacimiento_entry.get_date().strftime('%Y-%m-%d')
        apellido = self.apellido_entry.get().strip()
        correo = self.correo_entry.get().strip()
        telefono = self.telefono_entry.get().strip()
        password = self.password_entry.get() # Obtener la nueva contraseña (si se ingresó)

        if (
            not validar_obligatorio(numero_identificacion, 'número de identificación') or
            not validar_obligatorio(nombre, 'nombre') or
            not validar_obligatorio(apellido, 'apellido') or
            not validar_obligatorio(correo, 'correo')
        ): return

        if password:
            if update_user(user_id, tipo_identificacion, numero_identificacion, nombre, apellido, password):
                self.load_users()
                self.clear_fields()
        
        if fecha_nacimiento_str:
            if update_user(user_id, tipo_identificacion, numero_identificacion, nombre, apellido):
                self.load_users()
                self.clear_fields()

        if telefono:
            if update_user(user_id, tipo_identificacion, numero_identificacion, nombre, apellido, correo, telefono):
                self.load_users()
                self.clear_fields()
        
        else:
            if update_user(user_id, tipo_identificacion, numero_identificacion, nombre, apellido, correo):
                self.load_users()
                self.clear_fields()

    def delete_selected_user(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Selección Requerida", "Por favor, seleccione un usuario de la tabla para eliminar.")
            return

        user_id = self.tree.item(selected_item)['values'][0]
        if messagebox.askyesno("Confirmar Eliminación", f"¿Está seguro de que desea eliminar al usuario con ID {user_id}?"):
            if delete_user(user_id):
                self.load_users()
                self.clear_fields()

    def on_tree_select(self, event):
        selected_item = self.tree.focus()
        if selected_item:
            values = self.tree.item(selected_item)['values']
            self.id_entry.delete(0, tk.END)
            self.id_entry.insert(0, values[0])
            self.nombre_entry.delete(0, tk.END)
            self.nombre_entry.insert(0, values[1])
            
            date_obj = datetime.strptime(str(values[2]), '%Y-%m-%d').date()
            self.fecha_nacimiento_entry.set_date(date_obj)
            self.password_entry.delete(0, tk.END)
            
            self.id_entry.config(state='disabled')
        else:
            self.clear_fields()
            self.id_entry.config(state='normal')

    def clear_fields(self):
        self.id_entry.config(state='normal')
        self.id_entry.delete(0, tk.END)
        self.nombre_entry.delete(0, tk.END)
        self.fecha_nacimiento_entry.set_date(datetime.now().date())
        self.password_entry.delete(0, tk.END)

# --- Ejecutar la Aplicación ---
if __name__ == "__main__":
    create_table()

    root = tk.Tk()
    app = UserApp(root)
    root.mainloop()