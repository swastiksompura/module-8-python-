#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MediTrack - Minimal but complete desktop app for the assessment
---------------------------------------------------------------
• Tkinter GUI with tabs
• OOP with inheritance (User -> Admin/Doctor/Receptionist), overloading via default args,
  overriding via role permissions.
• SQLite3 persistence (patients, appointments, invoices)
• File I/O (CSV invoice export, simple text log)
• Exception handling (custom exceptions + try/except/finally)
• Regex search for reports
Author: ChatGPT (for Jay Sompura)
"""

import os
import re
import csv
import sqlite3
from datetime import datetime
from dataclasses import dataclass, asdict, field
from typing import List, Optional, Tuple

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

DB_PATH = os.path.join(os.path.dirname(__file__), "meditrack.db")
LOG_PATH = os.path.join(os.path.dirname(__file__), "meditrack.log")

# ----------------------------- Utilities & Exceptions -----------------------------

class AccessDenied(Exception):
    pass

class ValidationError(Exception):
    pass

def log(msg: str) -> None:
    """Append a timestamped line to a log file (File I/O)."""
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat(timespec='seconds')}] {msg}\n")

def require_role(*allowed_roles):
    """Decorator to enforce role-based access with helpful message."""
    def decorator(fn):
        def wrapper(self, *args, **kwargs):
            if self.current_role not in allowed_roles:
                messagebox.showwarning("Access denied",
                                       f"'{self.current_role}' cannot perform this action.")
                log(f"ACCESS DENIED for role={self.current_role} calling {fn.__name__}")
                raise AccessDenied(f"Role {self.current_role} not permitted")
            return fn(self, *args, **kwargs)
        return wrapper
    return decorator

# ----------------------------- Data Models (OOP) -----------------------------

@dataclass
class Patient:
    name: str
    age: int
    gender: str
    phone: str
    disease: str = ""
    status: str = "New"  # New / Follow-up / Critical
    id: Optional[int] = None

@dataclass
class Appointment:
    patient_id: int
    doctor: str
    date: str   # YYYY-MM-DD
    time: str   # HH:MM
    notes: str = ""
    id: Optional[int] = None

@dataclass
class Invoice:
    patient_id: int
    consultation_fee: float = 0.0
    medicines_total: float = 0.0
    tax_pct: float = 18.0
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    id: Optional[int] = None

    # Method overloading style via default args (single method supports multiple use cases)
    def total(self, include_tax: bool = True) -> float:
        subtotal = self.consultation_fee + self.medicines_total
        if include_tax:
            return round(subtotal * (1 + self.tax_pct / 100.0), 2)
        return round(subtotal, 2)

# ----------------------------- Repository (SQLite3) -----------------------------

class Repo:
    def __init__(self, db_path: str = DB_PATH):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA foreign_keys=ON;")
        self.init_db()

    def init_db(self):
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS patients(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                gender TEXT NOT NULL,
                phone TEXT NOT NULL,
                disease TEXT,
                status TEXT
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS appointments(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                doctor TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                notes TEXT,
                FOREIGN KEY(patient_id) REFERENCES patients(id) ON DELETE CASCADE
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS invoices(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                consultation_fee REAL NOT NULL,
                medicines_total REAL NOT NULL,
                tax_pct REAL NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(patient_id) REFERENCES patients(id) ON DELETE CASCADE
            );
        """)
        self.conn.commit()

    # -- Patient CRUD --
    def add_patient(self, p: Patient) -> int:
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO patients(name, age, gender, phone, disease, status)
            VALUES (?, ?, ?, ?, ?, ?);
        """, (p.name, p.age, p.gender, p.phone, p.disease, p.status))
        self.conn.commit()
        return cur.lastrowid

    def update_patient(self, p: Patient) -> None:
        if p.id is None:
            raise ValidationError("Patient ID required for update")
        self.conn.execute("""
            UPDATE patients SET name=?, age=?, gender=?, phone=?, disease=?, status=?
            WHERE id=?;
        """, (p.name, p.age, p.gender, p.phone, p.disease, p.status, p.id))
        self.conn.commit()

    def get_patient(self, pid: int) -> Optional[Patient]:
        cur = self.conn.cursor()
        cur.execute("SELECT id, name, age, gender, phone, disease, status FROM patients WHERE id=?", (pid,))
        row = cur.fetchone()
        if row:
            return Patient(id=row[0], name=row[1], age=row[2], gender=row[3], phone=row[4], disease=row[5], status=row[6])
        return None

    def all_patients(self) -> List[Patient]:
        cur = self.conn.cursor()
        cur.execute("SELECT id, name, age, gender, phone, disease, status FROM patients ORDER BY id DESC")
        rows = cur.fetchall()
        return [Patient(id=r[0], name=r[1], age=r[2], gender=r[3], phone=r[4], disease=r[5], status=r[6]) for r in rows]

    # -- Appointments --
    def add_appointment(self, a: Appointment) -> int:
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO appointments(patient_id, doctor, date, time, notes)
            VALUES (?, ?, ?, ?, ?);
        """, (a.patient_id, a.doctor, a.date, a.time, a.notes))
        self.conn.commit()
        return cur.lastrowid

    def appointments_for(self, patient_id: int) -> List[Appointment]:
        cur = self.conn.cursor()
        cur.execute("""
            SELECT id, patient_id, doctor, date, time, notes
            FROM appointments WHERE patient_id=? ORDER BY date DESC, time DESC
        """, (patient_id,))
        rows = cur.fetchall()
        return [Appointment(id=r[0], patient_id=r[1], doctor=r[2], date=r[3], time=r[4], notes=r[5]) for r in rows]

    # -- Invoices --
    def add_invoice(self, inv: Invoice) -> int:
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO invoices(patient_id, consultation_fee, medicines_total, tax_pct, created_at)
            VALUES (?, ?, ?, ?, ?);
        """, (inv.patient_id, inv.consultation_fee, inv.medicines_total, inv.tax_pct, inv.created_at))
        self.conn.commit()
        return cur.lastrowid

    def invoices_for(self, patient_id: int) -> List[Invoice]:
        cur = self.conn.cursor()
        cur.execute("""
            SELECT id, patient_id, consultation_fee, medicines_total, tax_pct, created_at
            FROM invoices WHERE patient_id=? ORDER BY id DESC
        """, (patient_id,))
        rows = cur.fetchall()
        return [Invoice(id=r[0], patient_id=r[1], consultation_fee=r[2], medicines_total=r[3],
                        tax_pct=r[4], created_at=r[5]) for r in rows]

    # -- Regex search across patients/appointments --
    def regex_query(self, pattern: str, field: str = "disease") -> List[Tuple[str, int]]:
        """
        Search patients by regex on a chosen field; returns list[(name, id)].
        field can be 'disease', 'status', or 'name'.
        """
        cur = self.conn.cursor()
        col = "disease" if field not in ("status", "name") else field
        cur.execute(f"SELECT id, name, {col} FROM patients")
        rows = cur.fetchall()
        rx = re.compile(pattern, flags=re.IGNORECASE)
        result = [(r[1], r[0]) for r in rows if rx.search(str(r[2] or ""))]
        return result

# ----------------------------- Users & Roles (OOP) -----------------------------

class User:
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role

    # Overridable permission check
    def can_edit_billing(self) -> bool:
        return False

class Admin(User):
    def can_edit_billing(self) -> bool:
        return True

class Doctor(User):
    def can_edit_billing(self) -> bool:
        return True

class Receptionist(User):
    def can_edit_billing(self) -> bool:
        return False

# ----------------------------- GUI -----------------------------

class MediTrackApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MediTrack - MediCare Hub")
        self.geometry("950x600")
        self.repo = Repo()
        self.current_user: Optional[User] = None
        self.current_role: str = "Guest"
        self.create_login_ui()

    # ---------- Login ----------
    def create_login_ui(self):
        self.login_frame = ttk.Frame(self, padding=20)
        self.login_frame.pack(expand=True)

        ttk.Label(self.login_frame, text="Welcome to MediTrack", font=("Segoe UI", 18, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        ttk.Label(self.login_frame, text="Username").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.ent_user = ttk.Entry(self.login_frame, width=30)
        self.ent_user.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(self.login_frame, text="Role").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.cmb_role = ttk.Combobox(self.login_frame, values=["Admin", "Receptionist", "Doctor"], state="readonly", width=27)
        self.cmb_role.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        self.cmb_role.current(0)

        ttk.Button(self.login_frame, text="Login", command=self.handle_login).grid(row=3, column=0, columnspan=2, pady=12)

    def handle_login(self):
        name = self.ent_user.get().strip() or "User"
        role = self.cmb_role.get()
        self.current_role = role
        # Build proper User subclass (polymorphism)
        if role == "Admin":
            self.current_user = Admin(name, role)
        elif role == "Doctor":
            self.current_user = Doctor(name, role)
        else:
            self.current_user = Receptionist(name, role)

        log(f"LOGIN name={name} role={role}")
        self.login_frame.destroy()
        self.build_main_ui()

    # ---------- Main UI (Tabs) ----------
    def build_main_ui(self):
        top = ttk.Frame(self)
        top.pack(fill="x")
        ttk.Label(top, text=f"Logged in as: {self.current_user.name} ({self.current_role})",
                  font=("Segoe UI", 11, "bold")).pack(side="left", padx=10, pady=6)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_patients = ttk.Frame(self.notebook)
        self.tab_appts = ttk.Frame(self.notebook)
        self.tab_billing = ttk.Frame(self.notebook)
        self.tab_reports = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_patients, text="Patients")
        self.notebook.add(self.tab_appts, text="Appointments")
        self.notebook.add(self.tab_billing, text="Billing / Invoices")
        self.notebook.add(self.tab_reports, text="Regex Reports")

        self.build_patients_tab()
        self.build_appts_tab()
        self.build_billing_tab()
        self.build_reports_tab()

    # ---------- Patients Tab ----------
    def build_patients_tab(self):
        frm = self.tab_patients
        left = ttk.LabelFrame(frm, text="Create / Update Patient", padding=10)
        left.pack(side="left", fill="y", padx=5, pady=5)
        right = ttk.Frame(frm)
        right.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # form fields
        self.p_id = tk.StringVar()
        self.p_name = tk.StringVar()
        self.p_age = tk.StringVar()
        self.p_gender = tk.StringVar(value="Male")
        self.p_phone = tk.StringVar()
        self.p_disease = tk.StringVar()
        self.p_status = tk.StringVar(value="New")

        row = 0
        ttk.Label(left, text="Patient ID (for update)").grid(row=row, column=0, sticky="e"); 
        ttk.Entry(left, textvariable=self.p_id, width=25).grid(row=row, column=1, pady=3); row+=1
        ttk.Label(left, text="Name").grid(row=row, column=0, sticky="e"); 
        ttk.Entry(left, textvariable=self.p_name, width=25).grid(row=row, column=1, pady=3); row+=1
        ttk.Label(left, text="Age").grid(row=row, column=0, sticky="e");
        ttk.Entry(left, textvariable=self.p_age, width=25).grid(row=row, column=1, pady=3); row+=1
        ttk.Label(left, text="Gender").grid(row=row, column=0, sticky="e");
        ttk.Combobox(left, textvariable=self.p_gender, values=["Male","Female","Other"], width=22, state="readonly").grid(row=row, column=1, pady=3); row+=1
        ttk.Label(left, text="Phone").grid(row=row, column=0, sticky="e"); 
        ttk.Entry(left, textvariable=self.p_phone, width=25).grid(row=row, column=1, pady=3); row+=1
        ttk.Label(left, text="Disease").grid(row=row, column=0, sticky="e"); 
        ttk.Entry(left, textvariable=self.p_disease, width=25).grid(row=row, column=1, pady=3); row+=1
        ttk.Label(left, text="Status").grid(row=row, column=0, sticky="e"); 
        ttk.Combobox(left, textvariable=self.p_status, values=["New","Follow-up","Critical"], width=22, state="readonly").grid(row=row, column=1, pady=3); row+=1

        ttk.Button(left, text="Save New Patient", command=self.on_save_patient).grid(row=row, column=0, columnspan=2, pady=8); row+=1
        ttk.Button(left, text="Update Existing", command=self.on_update_patient).grid(row=row, column=0, columnspan=2, pady=4)

        # table
        self.tree_pat = ttk.Treeview(right, columns=("id","name","age","gender","phone","disease","status"), show="headings", height=16)
        for c in ("id","name","age","gender","phone","disease","status"):
            self.tree_pat.heading(c, text=c.title())
            self.tree_pat.column(c, width=100 if c!="disease" else 160)
        self.tree_pat.pack(fill="both", expand=True)
        self.refresh_patients()

    def refresh_patients(self):
        for i in self.tree_pat.get_children():
            self.tree_pat.delete(i)
        for p in self.repo.all_patients():
            self.tree_pat.insert("", "end", values=(p.id,p.name,p.age,p.gender,p.phone,p.disease,p.status))

    def _validate_patient(self) -> Patient:
        try:
            age = int(self.p_age.get())
        except ValueError as e:
            raise ValidationError("Age must be a number") from e
        phone = self.p_phone.get().strip()
        if not re.fullmatch(r"[0-9]{10}", phone):
            raise ValidationError("Phone must be 10 digits")
        return Patient(
            name=self.p_name.get().strip(),
            age=age,
            gender=self.p_gender.get(),
            phone=phone,
            disease=self.p_disease.get().strip(),
            status=self.p_status.get()
        )

    @require_role("Admin", "Receptionist", "Doctor")
    def on_save_patient(self):
        try:
            patient = self._validate_patient()
            pid = self.repo.add_patient(patient)
            log(f"ADD PATIENT id={pid}")
            self.refresh_patients()
            messagebox.showinfo("Saved", f"Patient saved with ID {pid}")
        except (ValidationError, sqlite3.DatabaseError) as e:
            messagebox.showerror("Error", str(e))
            log(f"ERROR save patient: {e}")

    @require_role("Admin", "Receptionist", "Doctor")
    def on_update_patient(self):
        try:
            patient = self._validate_patient()
            if not self.p_id.get().strip():
                raise ValidationError("Provide Patient ID to update")
            patient.id = int(self.p_id.get().strip())
            self.repo.update_patient(patient)
            log(f"UPDATE PATIENT id={patient.id}")
            self.refresh_patients()
            messagebox.showinfo("Updated", "Patient updated")
        except (ValidationError, sqlite3.DatabaseError, ValueError) as e:
            messagebox.showerror("Error", str(e))
            log(f"ERROR update patient: {e}")

    # ---------- Appointments Tab ----------
    def build_appts_tab(self):
        frm = self.tab_appts
        top = ttk.Frame(frm); top.pack(fill="x", padx=5, pady=5)
        ttk.Label(top, text="Patient ID").pack(side="left")
        self.ap_ptid = tk.StringVar()
        ttk.Entry(top, textvariable=self.ap_ptid, width=10).pack(side="left", padx=4)
        ttk.Label(top, text="Doctor").pack(side="left")
        self.ap_doc = tk.StringVar(value="Dr. Smith")
        ttk.Entry(top, textvariable=self.ap_doc, width=16).pack(side="left", padx=4)
        ttk.Label(top, text="Date (YYYY-MM-DD)").pack(side="left")
        self.ap_date = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(top, textvariable=self.ap_date, width=14).pack(side="left", padx=4)
        ttk.Label(top, text="Time (HH:MM)").pack(side="left")
        self.ap_time = tk.StringVar(value=datetime.now().strftime("%H:%M"))
        ttk.Entry(top, textvariable=self.ap_time, width=8).pack(side="left", padx=4)
        ttk.Label(top, text="Notes").pack(side="left")
        self.ap_notes = tk.StringVar()
        ttk.Entry(top, textvariable=self.ap_notes, width=20).pack(side="left", padx=4)
        ttk.Button(top, text="Add Appointment", command=self.on_add_appt).pack(side="left", padx=6)

        self.tree_appts = ttk.Treeview(frm, columns=("id","patient_id","doctor","date","time","notes"),
                                       show="headings", height=16)
        for c in ("id","patient_id","doctor","date","time","notes"):
            self.tree_appts.heading(c, text=c.title())
            self.tree_appts.column(c, width=120 if c!="notes" else 260)
        self.tree_appts.pack(fill="both", expand=True, padx=5, pady=5)

        bottom = ttk.Frame(frm); bottom.pack(fill="x", padx=5, pady=5)
        ttk.Button(bottom, text="Load Patient Appointments", command=self.on_load_appts).pack(side="left")

    @require_role("Admin", "Receptionist", "Doctor")
    def on_add_appt(self):
        try:
            pid = int(self.ap_ptid.get())
            # quick existence check
            if not self.repo.get_patient(pid):
                raise ValidationError("Patient ID not found")
            ap = Appointment(patient_id=pid, doctor=self.ap_doc.get().strip(), date=self.ap_date.get().strip(),
                             time=self.ap_time.get().strip(), notes=self.ap_notes.get().strip())
            apid = self.repo.add_appointment(ap)
            log(f"ADD APPOINTMENT id={apid} for patient={pid}")
            self.on_load_appts()
            messagebox.showinfo("Saved", f"Appointment #{apid} saved")
        except (ValidationError, ValueError) as e:
            messagebox.showerror("Error", str(e))
            log(f"ERROR add appt: {e}")

    def on_load_appts(self):
        for i in self.tree_appts.get_children():
            self.tree_appts.delete(i)
        try:
            pid = int(self.ap_ptid.get())
            for ap in self.repo.appointments_for(pid):
                self.tree_appts.insert("", "end", values=(ap.id, ap.patient_id, ap.doctor, ap.date, ap.time, ap.notes))
        except ValueError:
            messagebox.showwarning("Notice", "Enter a valid Patient ID to load appointments.")

    # ---------- Billing Tab ----------
    def build_billing_tab(self):
        frm = self.tab_billing
        top = ttk.LabelFrame(frm, text="Create Invoice", padding=10)
        top.pack(fill="x", padx=5, pady=5)

        self.b_pid = tk.StringVar()
        self.b_fee = tk.StringVar(value="300")
        self.b_med = tk.StringVar(value="0")
        self.b_tax = tk.StringVar(value="18")

        ttk.Label(top, text="Patient ID").grid(row=0, column=0, sticky="e"); ttk.Entry(top, textvariable=self.b_pid, width=10).grid(row=0, column=1, padx=3, pady=3)
        ttk.Label(top, text="Consultation Fee").grid(row=1, column=0, sticky="e"); ttk.Entry(top, textvariable=self.b_fee, width=10).grid(row=1, column=1, padx=3, pady=3)
        ttk.Label(top, text="Medicines Total").grid(row=2, column=0, sticky="e"); ttk.Entry(top, textvariable=self.b_med, width=10).grid(row=2, column=1, padx=3, pady=3)
        ttk.Label(top, text="Tax %").grid(row=3, column=0, sticky="e"); ttk.Entry(top, textvariable=self.b_tax, width=10).grid(row=3, column=1, padx=3, pady=3)
        ttk.Button(top, text="Create Invoice", command=self.on_create_invoice).grid(row=4, column=0, columnspan=2, pady=6)

        self.tree_inv = ttk.Treeview(frm, columns=("id","patient_id","consultation_fee","medicines_total","tax_pct","created_at","total"),
                                     show="headings", height=16)
        for c in ("id","patient_id","consultation_fee","medicines_total","tax_pct","created_at","total"):
            self.tree_inv.heading(c, text=c.title())
            self.tree_inv.column(c, width=120 if c not in ("created_at","total") else 160)
        self.tree_inv.pack(fill="both", expand=True, padx=5, pady=5)

        bottom = ttk.Frame(frm); bottom.pack(fill="x", padx=5, pady=5)
        ttk.Button(bottom, text="Load Invoices (for Patient ID)", command=self.on_load_invoices).pack(side="left")
        ttk.Button(bottom, text="Export Selected to CSV", command=self.on_export_invoice).pack(side="left", padx=6)

    @require_role("Admin", "Doctor")  # Receptionist blocked to demo AccessDenied
    def on_create_invoice(self):
        try:
            pid = int(self.b_pid.get())
            if not self.repo.get_patient(pid):
                raise ValidationError("Patient ID not found")
            inv = Invoice(
                patient_id=pid,
                consultation_fee=float(self.b_fee.get() or 0),
                medicines_total=float(self.b_med.get() or 0),
                tax_pct=float(self.b_tax.get() or 0)
            )
            invid = self.repo.add_invoice(inv)
            log(f"ADD INVOICE id={invid} patient={pid}")
            self.on_load_invoices()
            messagebox.showinfo("Saved", f"Invoice #{invid} created. Total: ₹{inv.total()}")
        except (ValidationError, ValueError) as e:
            messagebox.showerror("Error", str(e))
            log(f"ERROR create invoice: {e}")

    def on_load_invoices(self):
        for i in self.tree_inv.get_children():
            self.tree_inv.delete(i)
        try:
            pid = int(self.b_pid.get())
            for inv in self.repo.invoices_for(pid):
                self.tree_inv.insert("", "end", values=(inv.id, inv.patient_id, inv.consultation_fee, inv.medicines_total,
                                                        inv.tax_pct, inv.created_at, inv.total()))
        except ValueError:
            messagebox.showwarning("Notice", "Enter a valid Patient ID to load invoices.")

    def on_export_invoice(self):
        sel = self.tree_inv.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a row to export.")
            return
        values = self.tree_inv.item(sel[0])["values"]
        # File I/O - save to CSV chosen by user
        default_name = f"invoice_{int(values[0])}.csv"
        path = filedialog.asksaveasfilename(title="Save Invoice CSV", defaultextension=".csv",
                                            initialfile=default_name, filetypes=[("CSV", "*.csv")])
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Field", "Value"])
                for col_name, val in zip(("id","patient_id","consultation_fee","medicines_total","tax_pct","created_at","total"), values):
                    writer.writerow([col_name, val])
            log(f"EXPORT INVOICE file={path}")
            messagebox.showinfo("Exported", f"Saved: {path}")
        finally:
            pass  # demonstrates try/finally even when no exception

    # ---------- Reports (Regex) ----------
    def build_reports_tab(self):
        frm = self.tab_reports
        top = ttk.Frame(frm); top.pack(fill="x", padx=5, pady=8)
        ttk.Label(top, text="Regex Pattern").pack(side="left")
        self.rx_pattern = tk.StringVar(value="follow|flu|covid")
        ttk.Entry(top, textvariable=self.rx_pattern, width=30).pack(side="left", padx=6)
        ttk.Label(top, text="Field").pack(side="left")
        self.rx_field = tk.StringVar(value="disease")
        ttk.Combobox(top, textvariable=self.rx_field, values=["disease","status","name"], state="readonly", width=12).pack(side="left", padx=6)
        ttk.Button(top, text="Run Regex Search", command=self.on_regex_search).pack(side="left", padx=6)

        self.tree_rx = ttk.Treeview(frm, columns=("name","id"), show="headings", height=18)
        for c in ("name","id"):
            self.tree_rx.heading(c, text=c.title())
            self.tree_rx.column(c, width=200 if c=="name" else 80)
        self.tree_rx.pack(fill="both", expand=True, padx=5, pady=5)

        info = ttk.Label(frm, text="Examples: 'covid|typhoid', '^Crit' (status starts with 'Crit'), '.*Follow.*'",
                         foreground="gray")
        info.pack(side="bottom", pady=6)

    def on_regex_search(self):
        pattern = self.rx_pattern.get().strip()
        try:
            results = self.repo.regex_query(pattern, field=self.rx_field.get())
            for i in self.tree_rx.get_children():
                self.tree_rx.delete(i)
            for name, pid in results:
                self.tree_rx.insert("", "end", values=(name, pid))
        except re.error as e:
            messagebox.showerror("Invalid Regex", str(e))

# ----------------------------- Run -----------------------------

def main():
    try:
        app = MediTrackApp()
        app.mainloop()
    except Exception as e:
        # Last-resort error capture
        log(f"FATAL ERROR: {e}")
        raise

if __name__ == "__main__":
    main()
