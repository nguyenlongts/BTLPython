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

import pandas as pd
import json



SAVE_FILE = "currencies.json"

def load_currencies():
    if not os.path.exists(SAVE_FILE):
        return []
    with open(SAVE_FILE, "r", encoding="utf-8") as f:
        content = f.read().strip()
        if not content:
            return []
        return json.loads(content)

def save_currencies(data):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def download_csv(currency_code, currencies, render_table, driver):
   
    try:
        for i, c in enumerate(currencies):
            if c["code"].lower() == currency_code.lower():
                currencies[i]["status"] = "Đang tải..."
                save_currencies(currencies)
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
                    save_currencies(currencies)
                    break
        else:
            raise Exception("Không tìm thấy file tải về.")
    except Exception as e:
        messagebox.showerror("❌ Lỗi", f"Không tải được dữ liệu cho {currency_code}: {e}")
        for i, c in enumerate(currencies):
            if c["code"].lower() == currency_code.lower():
                currencies[i]["status"] = "Lỗi tải"
                save_currencies(currencies)
                break
    finally:
        render_table()


def create_currency_downloader_gui(parent):
    currencies = load_currencies()
    
    # Main container frame
    main_frame = tk.Frame(parent)
    main_frame.pack(pady=10, padx=10)
    entry_frame = tk.Frame(main_frame)
    entry_frame.pack(pady=10)
    
    tk.Label(entry_frame, text="Nhập mã tiền tệ:").pack(side=tk.LEFT, padx=5)
    code_entry = tk.Entry(entry_frame)
    code_entry.pack(side=tk.LEFT, padx=5)
    # Table Frame with border
    table_frame = tk.Frame(main_frame, borderwidth=2, relief="solid", bg="white")
    table_frame.pack(pady=10, padx=10)
    
    # Define columns
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
        
        # Fill table with data
        for row_idx, currency in enumerate(currencies, start=1):
            row_cells = []
            
            # Code column
            code_cell = tk.Label(table_frame, text=currency["code"], 
                               font=('Arial', 12), borderwidth=1, relief="solid",
                               fg="blue", cursor="hand2", bg="white")
            code_cell.grid(row=row_idx, column=0, sticky="nsew")
            row_cells.append(code_cell)
            
            # Status column
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
            
            # Checkbox column
            check_var = tk.BooleanVar(value=currency.get("checked", False))
            check_vars.append(check_var)
            
            def toggle_check(idx=row_idx-1):
                currencies[idx]["checked"] = not currencies[idx].get("checked", False)
                check_vars[idx].set(currencies[idx]["checked"])
                save_currencies(currencies)
            
            check_cell = tk.Checkbutton(table_frame, variable=check_var, 
                                      command=lambda idx=row_idx-1: toggle_check(idx),
                                      borderwidth=1, relief="solid", bg="white")
            check_cell.grid(row=row_idx, column=2, sticky="nsew")
            row_cells.append(check_cell)
            
            table_cells.append(row_cells)
    
    # Configure grid to expand
    for i in range(len(columns)):
        table_frame.grid_columnconfigure(i, weight=1)
    
    
    

    def add_currency():
        code = code_entry.get().strip().upper()
        if not code:
            messagebox.showwarning("⚠️ Cảnh báo", "Vui lòng nhập mã tiền tệ!")
            return
        
        # Check if currency already exists
        for c in currencies:
            if c["code"] == code:
                messagebox.showinfo("Thông báo", f"Mã tiền tệ {code} đã tồn tại!")
                return 
        
        currencies.append({"code": code, "status": "Chưa tải", "checked": True})
        save_currencies(currencies)
        render_table()
        code_entry.delete(0, tk.END)  
    
    add_button = tk.Button(entry_frame, text="Thêm", command=add_currency)
    add_button.pack(side=tk.LEFT, padx=5)
    
    def download_selected():
        selected = [c for c in currencies if c.get("checked", False) and (c["status"] == "Chưa tải" or c["status"] == "Lỗi tải")]
        
        if not selected:
            messagebox.showwarning("⚠️ Cảnh báo", "Vui lòng chọn ít nhất một loại tiền tệ chưa tải để tải xuống!")
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
            messagebox.showerror("❌ Lỗi", f"Không thể khởi tạo trình duyệt: {e}")
        finally:
            if driver is not None:
                driver.quit()
    
    button_frame = tk.Frame(main_frame)
    button_frame.pack(pady=10)
    download_button = tk.Button(button_frame, text="Tải xuống", bg="green", fg="white", 
                              command=download_selected, padx=10, pady=5)
    download_button.grid(row=0,column=0,pady=10)
    def reset_status():
        for currency in currencies:
            currency["status"] = "Chưa tải"
            currency["checked"] = False
        save_currencies(currencies)
        render_table()
        messagebox.showinfo("✅ Thành công", "Đã đặt lại trạng thái và bỏ chọn tất cả tiền tệ.")
    reset_button = tk.Button(button_frame, text="Đặt lại", bg="orange", fg="white", 
                            command=reset_status, padx=10, pady=5)
    reset_button.grid(row=0,column=1, padx=5)
    render_table()