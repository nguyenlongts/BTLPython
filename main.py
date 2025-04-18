import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import autoMail
import crawlData
import compare
def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if file_path:
        with open(file_path, "r", encoding="utf-8") as f:
            emails = f.read().strip().split("\n") 
        entry_recipient.delete(0, tk.END)
        entry_recipient.insert(0, ", ".join(emails)) 

def open_currency_downloader():
    crawlData.gui_craw()    

def send_email():
    recipient = entry_recipient.get()
    subject = entry_subject.get()
    content = text_content.get("1.0", tk.END)
    if not recipient or not subject or not content.strip():
        messagebox.showwarning("Warning", "Vui lòng nhập đầy đủ thông tin.")
        return
    
    success = autoMail.send_email(recipient, subject, content)
    if success:
        messagebox.showinfo("Success", "Email đã được gửi thành công!")
    else:
        messagebox.showerror("Error", "Gửi email thất bại!")

def open_file_comparator():
    file_paths = filedialog.askopenfilenames(filetypes=[("CSV & Excel Files", "*.csv;*.xlsx;*.xls")])
    if len(file_paths) < 2:
        messagebox.showwarning("Warning", "Chọn ít nhất 2 file.")
        return
    differences = compare.compare_reports(file_paths)
    result_text.delete(1.0, tk.END)  
    if differences:
        diff_result = "\n".join(differences)
        result_text.insert(tk.END, diff_result)
        set_emailContent(diff_result)  
    else:
        result_text.insert(tk.END, "Không tìm thấy điểm khác biệt.")
        set_emailContent("Không tìm thấy điểm khác biệt") 
        
root = tk.Tk()
root.title("Ứng dụng Python tự động với Selenium")

notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both")

email_tab = ttk.Frame(notebook)
notebook.add(email_tab, text="Gửi Email")
tk.Label(email_tab, text="Người nhận:").pack()

entry_recipient = tk.Entry(email_tab, width=50)
entry_recipient.pack(pady=5)
btn_select_file = tk.Button(email_tab, text="Chọn File", command=select_file)
btn_select_file.pack(pady=5)
tk.Label(email_tab, text="Tiêu đề:").pack()
entry_subject = tk.Entry(email_tab, width=50)
entry_subject.pack(pady=5)

tk.Label(email_tab, text="Nội dung:").pack()
text_content = tk.Text(email_tab, width=100, height=10)
text_content.pack(pady=5)

btn_send_email = tk.Button(email_tab, text="Gửi Email", command=send_email)
btn_send_email.pack(pady=10)


file_compare_tab = ttk.Frame(notebook)
notebook.add(file_compare_tab, text="So Sánh File")

btn_compare = tk.Button(file_compare_tab, text="Chọn File để so sánh", command=open_file_comparator)
btn_compare.pack(pady=10)

result_text = tk.Text(file_compare_tab, width=100, height=20)
result_text.pack(padx=10, pady=10)
def set_emailContent():
    content = result_text.get("1.0", tk.END).strip()
    text_content.delete("1.0", tk.END)
    text_content.insert(tk.END, content)

btn_setContent = tk.Button(file_compare_tab,text="Đặt làm nội dung email",command=set_emailContent)
btn_setContent.pack(padx=10,pady=10)


currency_tab = ttk.Frame(notebook)
notebook.add(currency_tab, text="Tải Dữ Liệu Tiền Tệ")


crawlData.gui_craw(currency_tab)
root.mainloop()
