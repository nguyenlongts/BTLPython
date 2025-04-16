import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time
from datetime import datetime
import os
import sqlite3
import pandas as pd

DB_FILE  = "currencies.db"
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS currencies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE,
            status TEXT
        )
    """)
    conn.commit()
    conn.close()

def load_currencies():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT code, status FROM currencies")
        rows = cursor.fetchall()
        return [{"code": row[0], "status": row[1]} for row in rows]

def save_currency(code, status="Chưa tải"):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO currencies (code, status)
            VALUES (?, ?)
        """, (code, status))
        cursor.execute("""
            UPDATE currencies SET status = ? WHERE code = ?
        """, (status, code))
        conn.commit()

def delete_currency(code):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM currencies WHERE code = ?", (code,))
        conn.commit()


def download_csv(currency_code, currencies, render_table, driver):
    try:
        for i, c in enumerate(currencies):
            if c["code"].lower() == currency_code.lower():
                currencies[i]["status"] = "Đang tải..."
                save_currency(c["code"], "Đang tải...")
                render_table()
                break
        driver.get(f"https://vn.investing.com/currencies/single-currency-crosses?currency={currency_code}")

        download_icon = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'cursor-pointer')]/span"))
        )
        download_icon.click()

        today = datetime.today().strftime('%Y-%m-%d')
        download_dir = "C:\\Users\\Long\\Downloads"
        downloaded_file = os.path.join(download_dir, "Cặp tiền tệ Chéo đơn.csv")
        
        max_wait = 30
        start_time = time.time()
        while not os.path.exists(downloaded_file) and time.time() - start_time < max_wait:
            time.sleep(0.5)
        
        if os.path.exists(downloaded_file):
            new_file_name = f"{currency_code}-{today}.csv"
            new_file_path = os.path.join(download_dir, new_file_name)
            os.rename(downloaded_file, new_file_path)
            
            for i, c in enumerate(currencies):
                if c["code"].lower() == currency_code.lower():
                    currencies[i]["status"] = f"Đã tải ({today})"
                    save_currency(c["code"], f"Đã tải ({today})")
                    break
        else:
            raise Exception("Không tìm thấy file tải về.")
    except Exception as e:
        messagebox.showerror("❌ Lỗi", f"Không tải được dữ liệu cho {currency_code}: {e}")
        for i, c in enumerate(currencies):
            if c["code"].lower() == currency_code.lower():
                currencies[i]["status"] = "Lỗi tải"
                save_currency(c["code"], "Lỗi tải")
                break
    finally:
        render_table()


def gui_craw(parent):
    init_db()
    currencies = load_currencies()

    main_frame = tk.Frame(parent)
    main_frame.pack(pady=10, padx=10)
    entry_frame = tk.Frame(main_frame)
    entry_frame.pack(pady=10)

    tk.Label(entry_frame, text="Nhập mã tiền tệ:").pack(side=tk.LEFT, padx=5)
    code_entry = tk.Entry(entry_frame)
    code_entry.pack(side=tk.LEFT, padx=5)
    
    table_frame = tk.Frame(main_frame, borderwidth=2, relief="solid", bg="white")
    table_frame.pack(pady=10, padx=10)
    
    
    columns = ["Mã tiền tệ", "Trạng thái", "✔"]
    column_widths = [100, 200, 50]
    

    for col_idx, col_name in enumerate(columns):
        header_cell = tk.Label(table_frame, text=col_name, width=column_widths[col_idx]//10,
                              font=('Arial', 12, 'bold'), borderwidth=1, relief="solid", bg="white")
        header_cell.grid(row=0, column=col_idx, sticky="nsew")
    

    table_cells = []
    check_vars = []
    def render_table():
        for widget in table_frame.grid_slaves():
            if int(widget.grid_info()["row"]) > 0:
                widget.destroy()
        table_cells.clear()
        check_vars.clear()
        for row_idx, currency in enumerate(currencies, start=1):
            row_cells = []
            code_cell = tk.Label(table_frame, text=currency["code"], 
                               font=('Arial', 12), borderwidth=1, relief="solid",
                               fg="blue", cursor="hand2", bg="white")
            code_cell.grid(row=row_idx, column=0, sticky="nsew")
            row_cells.append(code_cell)
            status_text = currency["status"]
            status_color = "black"
            if status_text == "Đang tải...":
                status_color = "orange"
            elif status_text.startswith("Đã tải"):
                status_color = "green"
            elif status_text == "Lỗi tải":
                status_color = "red"
                
            status_cell = tk.Label(table_frame, text=status_text, 
                                 font=('Arial', 12), borderwidth=1, relief="solid", 
                                 bg="white", fg=status_color)
            status_cell.grid(row=row_idx, column=1, sticky="nsew")
            row_cells.append(status_cell)
            check_var = tk.BooleanVar(value=False)
            check_vars.append(check_var)
            def toggle_check(idx=row_idx-1):
                currencies[idx]["checked"] = not currencies[idx].get("checked", False)
                check_vars[idx].set(currencies[idx].get("checked", False))
            check_cell = tk.Checkbutton(table_frame, variable=check_var, 
                                      command=lambda idx=row_idx-1: toggle_check(idx),
                                      borderwidth=1, relief="solid", bg="white")
            check_cell.grid(row=row_idx, column=2, sticky="nsew")
            row_cells.append(check_cell)
            
            table_cells.append(row_cells)
    def reset_all():
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE currencies SET status = 'Chưa tải'")
            conn.commit()
        for currency in currencies:
            currency["status"] = "Chưa tải" 
        render_table()
    for i in range(len(columns)):
        table_frame.grid_columnconfigure(i, weight=1)
    
    def add_currency():
        code = code_entry.get().strip().upper()
        if not code:
            messagebox.showwarning("⚠️ Cảnh báo", "Vui lòng nhập mã tiền tệ!")
            return
    
        for c in currencies:
            if c["code"] == code:
                messagebox.showinfo("Thông báo", f"Mã tiền tệ {code} đã tồn tại!")
                return 
        
        save_currency(code)
        code_entry.delete(0, tk.END)  
        currencies.append({"code": code, "status": "Chưa tải"}) 
        render_table()   
    
    add_button = tk.Button(entry_frame, text="Thêm", command=add_currency,padx=10, pady=5)
    add_button.pack(side=tk.LEFT, padx=5)
    
    def download_selected():
        selected = [c for c in currencies if c.get("checked", False) and (c["status"] == "Chưa tải" or c["status"] == "Lỗi tải")]
        
        if not selected:
            messagebox.showwarning("Cảnh báo", "Chọn ít nhất một loại tiền tệ chưa tải để tải xuống!")
            return
        service = Service("C:/Users/Long/Desktop/BTL/chromedriver.exe")
        options = webdriver.ChromeOptions()
        options.add_argument("user-data-dir=C:\\Users\\Long\\AppData\\Local\\Google\\Chrome\\User Data")
        options.add_argument("profile-directory=Default")
        options.add_argument("--disable-sync")
        # options.add_argument("--headless")
        driver = None
        try:
            driver = webdriver.Chrome(service=service, options=options)

            for currency in selected:
                download_csv(currency["code"].lower(), currencies, render_table, driver)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể khởi tạo trình duyệt: {e}")
        finally:
            if driver is not None:
                driver.quit()
    def delete_selected():
        selected = [c for c in currencies if c.get("checked", False)]
        if not selected:
            messagebox.showwarning(" Cảnh báo", "Vui lòng chọn ít nhất một loại tiền tệ để xóa!")
            return
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            for currency in selected:
                cursor.execute("DELETE FROM currencies WHERE code = ?", (currency["code"],))
            conn.commit()
        
        currencies[:] = [currency for currency in currencies if not currency.get("checked", False)]
        
        render_table()
    button_frame = tk.Frame(main_frame)
    button_frame.pack(pady=10)
    download_button = tk.Button(button_frame, text="Tải xuống",
                              command=download_selected, padx=10, pady=5)
    download_button.grid(row=0, column=0, padx=5)
    delete_button = tk.Button(entry_frame, text="Xoá", command=delete_selected, padx=10, pady=5)
    delete_button.pack(side=tk.LEFT, padx=5)
    reset_button = tk.Button(button_frame, text="Reset tất cả",
                             command=reset_all, padx=10, pady=5)
    reset_button.grid(row=0, column=1, padx=5)
    render_table()