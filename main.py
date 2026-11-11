import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from plyer import notification

# ---------------- DATABASE ----------------
conn = sqlite3.connect("medicine.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS medicines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    time TEXT NOT NULL,
    instructions TEXT
)
""")
conn.commit()

# ---------------- COLORS ----------------
BG = "#F3F6FC"
WHITE = "#FFFFFF"
BLUE = "#2563EB"
DARK = "#172B4D"
MUTED = "#64748B"
GREEN = "#16A085"
RED = "#DC3545"

# ---------------- WINDOW ----------------
root = tk.Tk()
root.title("MediCare | Medicine Reminder")
root.geometry("1000x650")
root.minsize(800, 550)
root.resizable(True, True)
root.configure(bg=BG)

style = ttk.Style()
style.theme_use("clam")

style.configure(
    "Treeview",
    background=WHITE,
    foreground=DARK,
    rowheight=35,
    fieldbackground=WHITE,
    font=("Segoe UI", 10)
)

style.configure(
    "Treeview.Heading",
    background="#E8EFFB",
    foreground=DARK,
    font=("Segoe UI", 10, "bold"),
    padding=9
)

style.map(
    "Treeview",
    background=[("selected", "#D7E7FF")],
    foreground=[("selected", DARK)]
)

# ---------------- HEADER ----------------
header = tk.Frame(root, bg=BLUE, height=110)
header.pack(fill="x")
header.pack_propagate(False)

tk.Label(
    header,
    text="MediCare",
    font=("Segoe UI", 27, "bold"),
    bg=BLUE,
    fg=WHITE
).pack(anchor="w", padx=28, pady=(15, 0))

tk.Label(
    header,
    text="Your personal medicine reminder dashboard",
    font=("Segoe UI", 11),
    bg=BLUE,
    fg="#E0ECFF"
).pack(anchor="w", padx=30, pady=4)

# ---------------- MAIN CONTENT ----------------
main = tk.Frame(root, bg=BG)
main.pack(fill="both", expand=True, padx=22, pady=15)

# ---------------- SUMMARY CARDS ----------------
summary = tk.Frame(main, bg=BG)
summary.pack(fill="x", pady=(0, 15))


def make_card(parent, title, color):
    card = tk.Frame(parent, bg=WHITE, padx=18, pady=12)
    card.pack(side="left", fill="x", expand=True, padx=5)

    tk.Label(
        card,
        text=title,
        font=("Segoe UI", 10),
        bg=WHITE,
        fg=MUTED
    ).pack(anchor="w")

    value = tk.Label(
        card,
        text="0",
        font=("Segoe UI", 22, "bold"),
        bg=WHITE,
        fg=color
    )
    value.pack(anchor="w", pady=(4, 0))
    return value


total_label = make_card(summary, "Total Medicines", BLUE)
reminder_label = make_card(summary, "Daily Reminders", GREEN)

# ---------------- MEDICINE FORM ----------------
form_card = tk.Frame(main, bg=WHITE, padx=20, pady=15)
form_card.pack(fill="x", pady=(0, 15))

tk.Label(
    form_card,
    text="Medicine Management",
    font=("Segoe UI", 16, "bold"),
    bg=WHITE,
    fg=DARK
).grid(row=0, column=0, columnspan=3,
       sticky="w", pady=(0, 12))


def make_label(text, row, column):
    tk.Label(
        form_card,
        text=text,
        font=("Segoe UI", 10, "bold"),
        bg=WHITE,
        fg=DARK
    ).grid(row=row, column=column,
           sticky="w", padx=7, pady=5)


def make_entry(row, column):
    entry = tk.Entry(
        form_card,
        font=("Segoe UI", 11),
        bg="#F8FAFC",
        fg=DARK,
        relief="flat",
        highlightthickness=1,
        highlightbackground="#D9E2F0",
        highlightcolor=BLUE
    )
    entry.grid(
        row=row,
        column=column,
        sticky="ew",
        padx=7,
        pady=5,
        ipady=7
    )
    return entry


make_label("Medicine Name", 1, 0)
name_entry = make_entry(2, 0)

make_label("Time (HH:MM)", 1, 1)
time_entry = make_entry(2, 1)

make_label("Instructions", 1, 2)
instruction_entry = make_entry(2, 2)

for column in range(3):
    form_card.grid_columnconfigure(column, weight=1)

# ---------------- MEDICINE TABLE ----------------
table_card = tk.Frame(main, bg=WHITE, padx=15, pady=12)
table_card.pack(fill="both", expand=True)

tk.Label(
    table_card,
    text="Your Medicine Schedule",
    font=("Segoe UI", 16, "bold"),
    bg=WHITE,
    fg=DARK
).pack(anchor="w", pady=(0, 10))

table_frame = tk.Frame(table_card, bg=WHITE)
table_frame.pack(fill="both", expand=True)

table = ttk.Treeview(
    table_frame,
    columns=("Name", "Time", "Instructions"),
    show="headings",
    selectmode="browse"
)

table.heading("Name", text="MEDICINE")
table.heading("Time", text="REMINDER TIME")
table.heading("Instructions", text="INSTRUCTIONS")

table.column("Name", width=220)
table.column("Time", width=160, anchor="center")
table.column("Instructions", width=350)

scrollbar = ttk.Scrollbar(
    table_frame,
    orient="vertical",
    command=table.yview
)
table.configure(yscrollcommand=scrollbar.set)

table.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# ---------------- FUNCTIONS ----------------
def clear_fields():
    name_entry.delete(0, tk.END)
    time_entry.delete(0, tk.END)
    instruction_entry.delete(0, tk.END)


def clear_form():
    clear_fields()
    selected = table.selection()
    if selected:
        table.selection_remove(*selected)


def valid_time(value):
    try:
        datetime.strptime(value, "%H:%M")
        return True
    except ValueError:
        return False


def load_medicines():
    table.delete(*table.get_children())

    cursor.execute("SELECT * FROM medicines ORDER BY time")
    rows = cursor.fetchall()

    for row in rows:
        table.insert(
            "",
            tk.END,
            iid=str(row[0]),
            values=row[1:]
        )

    total_label.config(text=str(len(rows)))
    reminder_label.config(text=str(len(rows)))


def select_medicine(event=None):
    selected = table.selection()
    if not selected:
        return

    values = table.item(selected[0], "values")
    clear_fields()

    name_entry.insert(0, values[0])
    time_entry.insert(0, values[1])
    instruction_entry.insert(0, values[2])


def add_medicine():
    name = name_entry.get().strip()
    time = time_entry.get().strip()
    instructions = instruction_entry.get().strip()

    if not name or not time:
        messagebox.showerror(
            "Missing Details",
            "Enter medicine name and time."
        )
        return

    if not valid_time(time):
        messagebox.showerror(
            "Invalid Time",
            "Use 24-hour HH:MM format, e.g. 08:30."
        )
        return

    cursor.execute(
        "INSERT INTO medicines (name, time, instructions) VALUES (?, ?, ?)",
        (name, time, instructions)
    )
    conn.commit()

    load_medicines()
    clear_form()
    messagebox.showinfo("Success", "Medicine added successfully!")


def update_medicine():
    selected = table.selection()

    if not selected:
        messagebox.showwarning(
            "Select Medicine",
            "Select a medicine to update."
        )
        return

    name = name_entry.get().strip()
    time = time_entry.get().strip()
    instructions = instruction_entry.get().strip()

    if not name or not time:
        messagebox.showerror(
            "Missing Details",
            "Enter medicine name and time."
        )
        return

    if not valid_time(time):
        messagebox.showerror(
            "Invalid Time",
            "Use 24-hour HH:MM format, e.g. 08:30."
        )
        return

    cursor.execute(
        "UPDATE medicines SET name=?, time=?, instructions=? WHERE id=?",
        (name, time, instructions, selected[0])
    )
    conn.commit()

    load_medicines()
    clear_form()
    messagebox.showinfo("Updated", "Medicine updated successfully!")


def delete_medicine():
    selected = table.selection()

    if not selected:
        messagebox.showwarning(
            "Select Medicine",
            "Select a medicine to delete."
        )
        return

    if not messagebox.askyesno(
        "Confirm Delete",
        "Delete the selected medicine?"
    ):
        return

    cursor.execute(
        "DELETE FROM medicines WHERE id=?",
        (selected[0],)
    )
    conn.commit()

    load_medicines()
    clear_form()
    messagebox.showinfo("Deleted", "Medicine deleted successfully!")


def make_button(parent, text, color, command):
    return tk.Button(
        parent,
        text=text,
        command=command,
        bg=color,
        fg=WHITE,
        activebackground=color,
        activeforeground=WHITE,
        font=("Segoe UI", 10, "bold"),
        relief="flat",
        cursor="hand2",
        padx=15,
        pady=9
    )


# ---------------- BUTTONS ----------------
buttons = tk.Frame(main, bg=BG)
buttons.pack(fill="x", pady=(8, 8), before=table_card)

make_button(
    buttons, "+ Add Medicine", BLUE, add_medicine
).pack(side="left", padx=(0, 8))

make_button(
    buttons, "Update", GREEN, update_medicine
).pack(side="left", padx=8)

make_button(
    buttons, "Delete", RED, delete_medicine
).pack(side="left", padx=8)

make_button(
    buttons, "Clear", MUTED, clear_form
).pack(side="left", padx=8)

table.bind("<<TreeviewSelect>>", select_medicine)

# ---------------- DESKTOP REMINDERS ----------------

notified_medicines = set()


def check_reminders():
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    current_minute = now.strftime("%H:%M")

    cursor.execute(
        "SELECT id, name, time, instructions FROM medicines"
    )
    medicines = cursor.fetchall()

    for medicine_id, name, med_time, instructions in medicines:
        reminder_key = (medicine_id, today, med_time)

        if (
            med_time == current_minute
            and reminder_key not in notified_medicines
        ):
            message = f"It's time to take: {name}"

            if instructions:
                message += f"\nInstructions: {instructions}"

            try:
                notification.notify(
                    title="MediCare Reminder",
                    message=message,
                    app_name="MediCare",
                    timeout=10
                )

                notified_medicines.add(reminder_key)

            except Exception as error:
                print("Notification error:", error)

    root.after(5000, check_reminders)
# ---------------- START APP ----------------
load_medicines()
root.after(1000, check_reminders)


def close_app():
    conn.close()
    root.destroy()


root.protocol("WM_DELETE_WINDOW", close_app)
root.mainloop()