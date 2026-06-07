import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
from PIL import Image, ImageTk
import sqlite3
import hashlib
import uuid

# Database initialization
def init_db():
    conn = sqlite3.connect('insurance.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS Users (
        user_id TEXT PRIMARY KEY,
        username TEXT UNIQUE,
        password_hash TEXT,
        full_name TEXT,
        email TEXT
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS Vehicles (
        vehicle_id TEXT PRIMARY KEY,
        user_id TEXT,
        vehicle_number TEXT,
        manufacturer TEXT,
        model TEXT,
        year TEXT,
        chassis_number TEXT,
        is_taxi BOOLEAN,
        FOREIGN KEY (user_id) REFERENCES Users(user_id)
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS Policies (
        policy_id TEXT PRIMARY KEY,
        user_id TEXT,
        vehicle_id TEXT,
        birthdate TEXT,
        registration_place TEXT,
        ipn TEXT,
        email TEXT,
        phone_number TEXT,
        city TEXT,
        street TEXT,
        house TEXT,
        apartment TEXT,
        engine_volume TEXT,
        is_individual BOOLEAN,
        has_franchise BOOLEAN,
        contract_period TEXT,
        privileges TEXT,
        contract_duration TEXT,
        policy_cost REAL,
        creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES Users(user_id),
        FOREIGN KEY (vehicle_id) REFERENCES Vehicles(vehicle_id)
    )''')
    
    conn.commit()
    conn.close()

init_db()

# Password hashing
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Birthdate validation
def validate_birthdate(birthdate_str):
    try:
        birth_date = datetime.strptime(birthdate_str, "%d.%m.%Y")
        age = (datetime.now() - birth_date).days // 365
        if age < 18:
            messagebox.showerror("Помилка", "Користувач має бути старше 18 років.")
            return False
    except ValueError:
        messagebox.showerror("Помилка", "Невірний формат дати. Використовуйте ДД.ММ.РРРР.")
        return False
    return True

# Coefficient functions
def get_engine_coefficient():
    engine_type = engine_volume.get()
    coefficients = {
        "B1": 1.00, "B2": 1.14, "B3": 1.18, "B4": 1.82, "B5": 0.90,
        "F": 0.34, "D1": 2.55, "D2": 3.00, "C1": 2.00, "C2": 2.18,
        "E": 0.50, "A1": 0.34, "A2": 0.68
    }
    return coefficients.get(engine_type, 1.00)

def get_registration_coefficient():
    place = registration_place.get().lower()
    coefficients = {
        "Київ": 4.80,
        "Дніпро": 3.50, "Львів": 3.50, "Одеса": 3.50, "Харків": 3.50, "Бориспіль": 3.50, "Боярка": 3.50,
        "Бровари": 3.50, "Буча": 3.50, "Васильків": 3.50, "Вишгород": 3.50, "Вишневе": 3.50, "Ірпінь": 3.50,
        "Обухів": 3.50, "Донецьк": 2.80, "Запоріжжя": 2.80, "Кривий Ріг": 2.80,
        "Алчевськ": 2.50, "Бердянськ": 2.50, "Біла Церква": 2.50, "Вінниця": 2.50, "Горлівка": 2.50,
        "Євпаторія": 2.50, "Житомир": 2.50, "Івано-Франківськ": 2.50, "Кам’янець-Подільський": 2.50,
        "Кам’янськ": 2.50, "Керч": 2.50, "Кропивницький": 2.50, "Краматорськ": 2.50, "Кременчук": 2.50,
        "Лисичанськ": 2.50, "Луганськ": 2.50, "Луцьк": 2.50, "Макіївка": 2.50, "Маріуполь": 2.50,
        "Мелітополь": 2.50, "Миколаїв": 2.50, "Нікополь": 2.50, "Павлоград": 2.50, "Полтава": 2.50,
        "Рівне": 2.50, "Севастополь": 2.50, "Сєверодонецьк": 2.50, "Сімферопол": 2.50, "Слов’янськ": 2.50,
        "Суми": 2.50, "Тернопіль": 2.50, "Ужгород": 2.50, "Херсон": 2.50, "Хмельницький": 2.50,
        "Черкаси": 2.50, "Чернівці": 2.50, "Чернігів": 2.50, "Інші населені пункти України": 1.60,
        "Для транспортних засобів, які зареєстровані в інших країнах": 5.60
    }
    return coefficients.get(place, 1.0)

def get_franchise_coefficient():
    engine_type = engine_volume.get()
    if has_franchise.get():
        if is_individual.get():
            coefficients = {
                "B1": 1.42, "B2": 1.42, "B3": 1.41, "B4": 1.40, "B5": 1.65,
                "F": 1.40, "D1": 1.42, "D2": 1.42, "C1": 1.40, "C2": 1.40,
                "E": 1.40, "A1": 1.42, "A2": 1.40
            }
        else:
            coefficients = {
                "B1": 1.60, "B2": 1.60, "B3": 1.60, "B4": 1.55, "B5": 1.89,
                "F": 1.55, "D1": 1.70, "D2": 1.70, "C1": 1.42, "C2": 1.56,
                "E": 1.55, "A1": 2.25, "A2": 2.20
            }
    else:
        if is_individual.get():
            coefficients = {
                "B1": 2.08, "B2": 2.06, "B3": 2.06, "B4": 1.90, "B5": 2.44,
                "F": 2.08, "D1": 1.92, "D2": 1.94, "C1": 1.92, "C2": 2.07,
                "E": 2.07, "A1": 2.12, "A2": 2.04
            }
        else:
            coefficients = {
                "B1": 2.20, "B2": 2.18, "B3": 2.18, "B4": 1.97, "B5": 2.56,
                "F": 2.46, "D1": 2.20, "D2": 2.31, "C1": 2.04, "C2": 2.27,
                "E": 2.45, "A1": 3.09, "A2": 2.98
            }
    return coefficients.get(engine_type, 1.00)

def get_contract_period_coefficient():
    try:
        # Зчитуємо період і строк з полів
        period = int(contract_period.get())  # Наприклад, 12 місяців
        duration = int(contract_duration.get())  # Наприклад, 2 місяці
        # Розрахунок різниці між періодом та строком
        difference = period - duration
        # Визначення коефіцієнта k6 в залежності від різниці
        if difference <= 0:
            return 1.0  # Якщо різниця <= 0, коефіцієнт дорівнює 1.0
        elif difference == 1:
            return 1.0
        elif difference == 2:
            return 1.0
        elif difference == 3:
            return 1.0
        elif difference == 4:
            return 1.0
        elif difference == 5:
            return 1.0
        elif difference == 6:
            return 0.7
        elif difference == 7:
            return 0.75
        elif difference == 8:
            return 0.8
        elif difference == 9:
            return 0.85
        elif difference == 10:
            return 0.9
        elif difference == 11:
            return 0.95
        else:
            return 1.0  # Якщо різниця більша за 11, коефіцієнт залишається 1.0
    except ValueError:
        messagebox.showerror("Помилка введення", "Перевірте правильність введення періоду та строку договору.")
        return 1.0

# Policy cost calculation
def calculate_policy_cost():
    try:
        base_rate = 180
        k1 = get_engine_coefficient()
        k2 = get_registration_coefficient()
        k3 = 1.4 if is_taxi.get() else 1.0
        k4 = 1.76 if is_individual.get() else 1.2
        k5 = 1
        k6 = get_franchise_coefficient()
        k7 = get_contract_period_coefficient()
        
        total_cost = base_rate * k1 * k2 * k3 * k4 * k5 * k6 * k7
        return round(total_cost, 2)
    except Exception as e:
        messagebox.showerror("Помилка розрахунку", f"Помилка: {e}")
        return 0

# Save data to database
def save_data():
    if not validate_birthdate(birthdate.get()):
        return
    
    policy_cost = calculate_policy_cost()
    
    conn = sqlite3.connect('insurance.db')
    c = conn.cursor()
    
    vehicle_id = str(uuid.uuid4())
    c.execute('''INSERT INTO Vehicles (vehicle_id, user_id, vehicle_number, manufacturer, model, year, chassis_number, is_taxi)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                (vehicle_id, current_user_id, vehicle_number.get(), manufacturer.get(), model.get(),
                 year.get(), chassis_number.get(), is_taxi.get()))
    
    policy_id = str(uuid.uuid4())
    c.execute('''INSERT INTO Policies (policy_id, user_id, vehicle_id, birthdate, registration_place, ipn,
                email, phone_number, city, street, house, apartment, engine_volume, is_individual,
                has_franchise, contract_period, privileges, contract_duration, policy_cost)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (policy_id, current_user_id, vehicle_id, birthdate.get(), registration_place.get(),
                 ipn.get(), email.get(), phone_number.get(), city.get(), street.get(), house.get(),
                 apartment.get(), engine_volume.get(), is_individual.get(), has_franchise.get(),
                 contract_period.get(), privileges.get(), contract_duration.get(), policy_cost))
    
    conn.commit()
    conn.close()
    
    data = (
        f"Номер транспорту: {vehicle_number.get()}\n"
        f"Виробник: {manufacturer.get()}\n"
        f"Модель: {model.get()}\n"
        f"Рік випуску: {year.get()}\n"
        f"Номер кузова: {chassis_number.get()}\n"
        f"Таксі: {'Так' if is_taxi.get() else 'Ні'}\n"
        f"ПІБ: {full_name.get()}\n"
        f"Дата народження: {birthdate.get()}\n"
        f"Місце реєстрації: {registration_place.get()}\n"
        f"ІПН: {ipn.get()}\n"
        f"Email: {email.get()}\n"
        f"Телефон: {phone_number.get()}\n"
        f"Місто: {city.get()}\n"
        f"Вулиця: {street.get()}\n"
        f"Будинок: {house.get()}\n"
        f"Квартира: {apartment.get()}\n"
        f"Об'єм двигуна: {engine_volume.get()}\n"
        f"Фіз/Юр особа: {'Фізична' if is_individual.get() else 'Юридична'}\n"
        f"Франшиза: {'Так' if has_franchise.get() else 'Ні'}\n"
        f"Період дії договору: {contract_period.get()}\n"
        f"Пільги: {privileges.get()}\n"
        f"Строк дії договору: {contract_duration.get()}\n"
        f"Вартість полісу: {policy_cost} грн\n"
    )
    
    messagebox.showinfo("Поліс збережений", data)
    show_policy(data)

# Show policy
def show_policy(policy_data):
    policy_window = tk.Toplevel(root)
    policy_window.title("Ваш страховий поліс")
    policy_window.geometry("600x600")
    policy_window.configure(bg='#f0f0f0')
    
    container = ttk.Frame(policy_window)
    container.pack(expand=True, fill='both', padx=20, pady=20)
    
    ttk.Label(container, text="Ваш страховий поліс", font=('Arial', 16, 'bold')).pack(pady=10)
    text_widget = tk.Text(container, height=20, width=60, wrap='word', font=('Arial', 12))
    text_widget.pack(pady=10, fill='both', expand=True)
    text_widget.insert('1.0', policy_data)
    text_widget.config(state='disabled')
    
    ttk.Button(container, text="Закрити", command=policy_window.destroy).pack(pady=10)

# Login function
def login():
    username = username_var.get()
    password = password_var.get()
    
    conn = sqlite3.connect('insurance.db')
    c = conn.cursor()
    c.execute("SELECT user_id, password_hash FROM Users WHERE username=?", (username,))
    result = c.fetchone()
    conn.close()
    
    if result and result[1] == hash_password(password):
        global current_user_id
        current_user_id = result[0]
        login_frame.pack_forget()
        main_frame.pack(expand=True, fill='both')
        root.geometry("800x600")  # Reset to a consistent size
        show_frame(0)
    else:
        messagebox.showerror("Помилка", "Невірне ім'я користувача або пароль")

# Register function
def register():
    username = username_var.get()
    password = password_var.get()
    full_name = register_full_name_var.get()
    email = register_email_var.get()
    
    conn = sqlite3.connect('insurance.db')
    c = conn.cursor()
    
    try:
        user_id = str(uuid.uuid4())
        c.execute('''INSERT INTO Users (user_id, username, password_hash, full_name, email)
                    VALUES (?, ?, ?, ?, ?)''',
                    (user_id, username, hash_password(password), full_name, email))
        conn.commit()
        messagebox.showinfo("Успіх", "Реєстрація пройшла успішно. Будь ласка, увійдіть.")
        show_login_frame()
    except sqlite3.IntegrityError:
        messagebox.showerror("Помилка", "Ім'я користувача вже існує")
    finally:
        conn.close()

# Progress bar
def update_progress(step):
    canvas.delete("all")
    letters = ["Держ. номер", "Дані авто", "Дані страхувальника", "Дані договору", "Підтвердження", "Готовий поліс"]
    canvas_width = canvas.winfo_width()
    arrow_width = max(100, canvas_width // len(letters))  # Minimum width to prevent collapse
    
    for i, label in enumerate(letters):
        color = "#0055a5" if i <= step else "lightgray"
        x1 = i * arrow_width
        x2 = x1 + arrow_width
        points = [x1, 10, x2 - 10, 10, x2, 30, x2 - 10, 50, x1, 50]
        canvas.create_polygon(points, fill=color, outline=color)
        canvas.create_text((x1 + x2 - 10) / 2, 30, text=label, fill="white" if i <= step else "black", font=('Arial', 9, 'bold'))

# Main window setup
root = tk.Tk()
root.title("Страховий поліс")
root.geometry("800x600")
root.minsize(800, 600)  # Prevent excessive shrinking
root.configure(bg='#f0f0f0')

# Variables
current_user_id = None
username_var = tk.StringVar()
password_var = tk.StringVar()
register_full_name_var = tk.StringVar()
register_email_var = tk.StringVar()
vehicle_number = tk.StringVar()
manufacturer = tk.StringVar()
model = tk.StringVar()
year = tk.StringVar()
chassis_number = tk.StringVar()
is_taxi = tk.BooleanVar()
full_name = tk.StringVar()
birthdate = tk.StringVar()
registration_place = tk.StringVar()
ipn = tk.StringVar()
email = tk.StringVar()
phone_number = tk.StringVar()
city = tk.StringVar()
street = tk.StringVar()
house = tk.StringVar()
apartment = tk.StringVar()
engine_volume = tk.StringVar()
is_individual = tk.BooleanVar()
has_franchise = tk.BooleanVar()
contract_period = tk.StringVar()
privileges = tk.StringVar()
contract_duration = tk.StringVar()

# Styles
style = ttk.Style()
style.theme_use('clam')
style.configure('TFrame', background='#f0f0f0')
style.configure('TLabel', background='#f0f0f0', font=('Helvetica', 12))
style.configure('TEntry', font=('Helvetica', 12), padding=5)
style.configure('TButton', font=('Helvetica', 10, 'bold'), foreground='#ffffff', background='#0055a5')
style.map('TButton', background=[('active', '#003087')])
style.configure('TCheckbutton', background='#f0f0f0', font=('Helvetica', 12))

# Login frame
login_frame = ttk.Frame(root, style='TFrame')
login_container = ttk.Frame(login_frame, style='TFrame')
login_container.pack(pady=20)
ttk.Label(login_container, text="Вхід у систему", font=('Arial', 16, 'bold')).grid(row=0, column=0, columnspan=2, pady=20)
ttk.Label(login_container, text="Ім'я користувача:").grid(row=1, column=0, sticky='e', pady=5)
ttk.Entry(login_container, textvariable=username_var, width=30).grid(row=1, column=1, pady=5)
ttk.Label(login_container, text="Пароль:").grid(row=2, column=0, sticky='e', pady=5)
ttk.Entry(login_container, textvariable=password_var, show="*", width=30).grid(row=2, column=1, pady=5)
ttk.Button(login_container, text="Увійти", command=login).grid(row=3, column=0, columnspan=2, pady=10)
ttk.Button(login_container, text="Зареєструватися", command=lambda: show_register_frame()).grid(row=4, column=0, columnspan=2, pady=5)

# Register frame
register_frame = ttk.Frame(root, style='TFrame')
register_container = ttk.Frame(register_frame, style='TFrame')
register_container.pack(pady=20)
ttk.Label(register_container, text="Реєстрація", font=('Arial', 16, 'bold')).grid(row=0, column=0, columnspan=2, pady=20)
ttk.Label(register_container, text="Ім'я користувача:").grid(row=1, column=0, sticky='e', pady=5)
ttk.Entry(register_container, textvariable=username_var, width=30).grid(row=1, column=1, pady=5)
ttk.Label(register_container, text="Пароль:").grid(row=2, column=0, sticky='e', pady=5)
ttk.Entry(register_container, textvariable=password_var, show="*", width=30).grid(row=2, column=1, pady=5)
ttk.Label(register_container, text="ПІБ:").grid(row=3, column=0, sticky='e', pady=5)
ttk.Entry(register_container, textvariable=register_full_name_var, width=30).grid(row=3, column=1, pady=5)
ttk.Label(register_container, text="Email:").grid(row=4, column=0, sticky='e', pady=5)
ttk.Entry(register_container, textvariable=register_email_var, width=30).grid(row=4, column=1, pady=5)
ttk.Button(register_container, text="Зареєструватися", command=register).grid(row=5, column=0, columnspan=2, pady=10)
ttk.Button(register_container, text="Назад", command=lambda: show_login_frame()).grid(row=6, column=0, columnspan=2, pady=5)

# Main frame
main_frame = ttk.Frame(root, style='TFrame')
canvas = tk.Canvas(main_frame, height=60, bg='#e1e1e1')
canvas.pack(fill='x')
root.update_idletasks()
update_progress(0)

# Step frames
frames = [ttk.Frame(main_frame, style='TFrame') for _ in range(6)]
for frame in frames:
    frame.pack(expand=True, fill='both', padx=20, pady=20)

def show_frame(index):
    for i, frame in enumerate(frames):
        frame.pack_forget() if i != index else frame.pack(expand=True, fill='both', padx=20, pady=20)
    update_progress(index)

def show_login_frame():
    login_frame.pack(expand=True, fill='both')
    register_frame.pack_forget()
    main_frame.pack_forget()
    root.geometry("800x600")  # Reset size for login

def show_register_frame():
    register_frame.pack(expand=True, fill='both')
    login_frame.pack_forget()
    main_frame.pack_forget()
    root.geometry("800x600")  # Reset size for register

# Step 1: Vehicle number
frame1_container = ttk.Frame(frames[0], style='TFrame')
frame1_container.pack(expand=True)
ttk.Label(frame1_container, text="Введіть держ. номер транспортного засобу:", font=('Arial', 14)).grid(row=0, column=0, columnspan=2, pady=20)
try:
    flag_image = Image.open("1.png")
    flag_image = flag_image.resize((15, 20), Image.LANCZOS)
    flag_photo = ImageTk.PhotoImage(flag_image)
    flag_label = tk.Label(frame1_container, image=flag_photo)
    flag_label.image = flag_photo
    flag_label.grid(row=1, column=0, sticky='e', padx=5)
except:
    pass
ttk.Entry(frame1_container, textvariable=vehicle_number, width=30).grid(row=1, column=1, pady=10)
ttk.Button(frame1_container, text="Продовжити", command=lambda: show_frame(1)).grid(row=2, column=0, columnspan=2, pady=20)

# Step 2: Vehicle details
frame2_container = ttk.Frame(frames[1], style='TFrame')
frame2_container.pack(expand=True)
ttk.Label(frame2_container, text="Введіть дані автомобіля", font=('Arial', 14)).grid(row=0, column=0, columnspan=2, pady=20)
ttk.Label(frame2_container, text="Виробник:").grid(row=1, column=0, sticky='e', pady=5)
ttk.Entry(frame2_container, textvariable=manufacturer, width=30).grid(row=1, column=1, pady=5)
ttk.Label(frame2_container, text="Модель:").grid(row=2, column=0, sticky='e', pady=5)
ttk.Entry(frame2_container, textvariable=model, width=30).grid(row=2, column=1, pady=5)
ttk.Label(frame2_container, text="Рік випуску:").grid(row=3, column=0, sticky='e', pady=5)
ttk.Entry(frame2_container, textvariable=year, width=30).grid(row=3, column=1, pady=5)
ttk.Label(frame2_container, text="Номер кузова:").grid(row=4, column=0, sticky='e', pady=5)
ttk.Entry(frame2_container, textvariable=chassis_number, width=30).grid(row=4, column=1, pady=5)
ttk.Checkbutton(frame2_container, text="Використовується в таксі", variable=is_taxi).grid(row=5, column=0, columnspan=2, pady=5)
frame_buttons_1 = ttk.Frame(frame2_container, style='TFrame')
frame_buttons_1.grid(row=6, column=0, columnspan=2, pady=20)
ttk.Button(frame_buttons_1, text="Назад", command=lambda: show_frame(0)).pack(side='left', padx=10)
ttk.Button(frame_buttons_1, text="Продовжити", command=lambda: show_frame(2)).pack(side='right', padx=10)

# Step 3: Policyholder details
frame3_container = ttk.Frame(frames[2], style='TFrame')
frame3_container.pack(expand=True)
ttk.Label(frame3_container, text="Введіть дані страхувальника", font=('Arial', 14)).grid(row=0, column=0, columnspan=2, pady=20)
ttk.Label(frame3_container, text="ПІБ:").grid(row=1, column=0, sticky='e', pady=5)
ttk.Entry(frame3_container, textvariable=full_name, width=30).grid(row=1, column=1, pady=5)
ttk.Label(frame3_container, text="Дата народження:").grid(row=2, column=0, sticky='e', pady=5)
ttk.Entry(frame3_container, textvariable=birthdate, width=30).grid(row=2, column=1, pady=5)
ttk.Label(frame3_container, text="Місце реєстрації:").grid(row=3, column=0, sticky='e', pady=5)
ttk.Entry(frame3_container, textvariable=registration_place, width=30).grid(row=3, column=1, pady=5)
ttk.Label(frame3_container, text="ІПН:").grid(row=4, column=0, sticky='e', pady=5)
ttk.Entry(frame3_container, textvariable=ipn, width=30).grid(row=4, column=1, pady=5)
ttk.Label(frame3_container, text="Email:").grid(row=5, column=0, sticky='e', pady=5)
ttk.Entry(frame3_container, textvariable=email, width=30).grid(row=5, column=1, pady=5)
ttk.Label(frame3_container, text="Телефон:").grid(row=6, column=0, sticky='e', pady=5)
ttk.Entry(frame3_container, textvariable=phone_number, width=30).grid(row=6, column=1, pady=5)
frame_buttons_2 = ttk.Frame(frame3_container, style='TFrame')
frame_buttons_2.grid(row=7, column=0, columnspan=2, pady=20)
ttk.Button(frame_buttons_2, text="Назад", command=lambda: show_frame(1)).pack(side='left', padx=10)
ttk.Button(frame_buttons_2, text="Продовжити", command=lambda: show_frame(3)).pack(side='right', padx=10)

# Step 4: Contract details
frame4_container = ttk.Frame(frames[3], style='TFrame')
frame4_container.pack(expand=True)
ttk.Label(frame4_container, text="Введіть дані договору", font=('Arial', 14)).grid(row=0, column=0, columnspan=2, pady=20)
ttk.Label(frame4_container, text="Об'єм двигуна:").grid(row=1, column=0, sticky='e', pady=5)
ttk.Entry(frame4_container, textvariable=engine_volume, width=30).grid(row=1, column=1, pady=5)
ttk.Checkbutton(frame4_container, text="Фізична особа", variable=is_individual).grid(row=2, column=0, columnspan=2, pady=5)
ttk.Checkbutton(frame4_container, text="Франшиза", variable=has_franchise).grid(row=3, column=0, columnspan=2, pady=5)
ttk.Label(frame4_container, text="Період дії договору:").grid(row=4, column=0, sticky='e', pady=5)
ttk.Entry(frame4_container, textvariable=contract_period, width=30).grid(row=4, column=1, pady=5)
ttk.Label(frame4_container, text="Пільги:").grid(row=5, column=0, sticky='e', pady=5)
ttk.Entry(frame4_container, textvariable=privileges, width=30).grid(row=5, column=1, pady=5)
ttk.Label(frame4_container, text="Строк дії договору (скільки в простої):").grid(row=6, column=0, sticky='e', pady=5)
ttk.Entry(frame4_container, textvariable=contract_duration, width=30).grid(row=6, column=1, pady=5)
frame_buttons_3 = ttk.Frame(frame4_container, style='TFrame')
frame_buttons_3.grid(row=7, column=0, columnspan=2, pady=20)
ttk.Button(frame_buttons_3, text="Назад", command=lambda: show_frame(2)).pack(side='left', padx=10)
ttk.Button(frame_buttons_3, text="Продовжити", command=lambda: show_frame(4)).pack(side='right', padx=10)

# Step 5: Confirm data
frame5_container = ttk.Frame(frames[4], style='TFrame')
frame5_container.pack(expand=True)
ttk.Label(frame5_container, text="Перевірте всі дані перед збереженням", font=('Arial', 14)).grid(row=0, column=0, columnspan=2, pady=20)
frame_buttons_4 = ttk.Frame(frame5_container, style='TFrame')
frame_buttons_4.grid(row=1, column=0, columnspan=2, pady=20)
ttk.Button(frame_buttons_4, text="Назад", command=lambda: show_frame(3)).pack(side='left', padx=10)
ttk.Button(frame_buttons_4, text="Зберегти та показати поліс", command=save_data).pack(side='right', padx=10)

# Step 6: Policy ready
frame6_container = ttk.Frame(frames[5], style='TFrame')
frame6_container.pack(expand=True)
ttk.Label(frame6_container, text="Ваш поліс готовий!", font=('Arial', 14)).grid(row=0, column=0, columnspan=2, pady=20)
ttk.Label(frame6_container, text="Вартість полісу:").grid(row=1, column=0, sticky='e', pady=5)
policy_cost_label = ttk.Label(frame6_container, text="")
policy_cost_label.grid(row=1, column=1, pady=5)

def show_policy_cost():
    if validate_birthdate(birthdate.get()):
        cost = calculate_policy_cost()
        policy_cost_label.config(text=f"{cost} грн")

frame_buttons_5 = ttk.Frame(frame6_container, style='TFrame')
frame_buttons_5.grid(row=2, column=0, columnspan=2, pady=20)
ttk.Button(frame_buttons_5, text="Назад", command=lambda: show_frame(4)).pack(side='left', padx=10)
ttk.Button(frame_buttons_5, text="Завершити", command=show_policy_cost).pack(side='right', padx=10)

# Start application
show_login_frame()
root.mainloop()