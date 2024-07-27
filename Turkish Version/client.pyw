import os, socket, time, threading, tkinter as tk
from tkinter import messagebox, scrolledtext

host = "localhost"
port = 2000

clock = time.strftime("%H:%M")

def closing():
    os._exit(0)

def username():
    global username
    username = ""

    def submit(event):
        global username
        name = entry.get().strip()
        if not name.isalpha(): messagebox.showerror("Uyarı", "Sadece alfabetik karakterler geçerli.")
        elif len(name) < 3: messagebox.showerror("Uyarı", "İsim minumum 3 harf olmalı.")
        elif len(name) > 10: messagebox.showerror("Uyarı", "İsim maksimum 10 harf olmalı.")
        else: username = name; root.destroy()

    root = tk.Tk()
    root.geometry("400x140")
    root.resizable(False, False)
    root.title("Join")
    root.configure(bg='#212121')
    root.iconbitmap("icon.ico")

    root.update_idletasks()

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - root.winfo_width()) // 2
    y = int((screen_height - root.winfo_height() * 2.4) // 2)
    root.geometry(f"{root.winfo_width()}x{root.winfo_height()}+{x}+{y}")

    frame = tk.Frame(root, bg='#212121')
    frame.pack(expand=True, fill='both', pady=11)

    label = tk.Label(frame, text="Name?", font=("Arial", 13), bg="#212121", fg="#fff")
    label.pack(pady=20)

    entry = tk.Entry(frame, font=("Arial", 11), width=30, relief="sunken")
    entry.pack()
    entry.focus()

    root.protocol("WM_DELETE_WINDOW", closing)
    root.bind('<Return>', submit)
    root.mainloop()

    return username
username = username()

try:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((host, port))
    server.send(username.encode('utf-8'))
except Exception: messagebox.showerror("Hata", "Sunucu kapalı!"); closing()

root = tk.Tk()
root.geometry("400x500")
root.resizable(False, False)
root.title("Sohbet")
root.configure(bg='#212121')
root.iconbitmap("icon.ico")

topFrame = tk.Frame(root, bg="#212121")
topFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

bottomFrame = tk.Frame(root, bg='#212121')
bottomFrame.pack(side=tk.BOTTOM, fill=tk.X)

messages = scrolledtext.ScrolledText(topFrame, bg="#212121", fg="#fff", state=tk.DISABLED)
messages.config(spacing3=4, padx=7)
messages.pack(fill=tk.BOTH, expand=True)

entry = tk.Entry(bottomFrame)
entry.pack(fill=tk.X)
entry.focus()

def addmsg(message):
    messages.configure(state=tk.NORMAL)
    messages.insert(tk.END, message + "\n")
    messages.configure(state=tk.DISABLED)
    messages.see(tk.END)

def take():
    while True:
        try:
            data = server.recv(1024).decode()
            addmsg(data)
            if(not data):
                closing()
        except Exception: break
    closing()

def send(event):
    message = entry.get().strip()
    if(message == "exit"): closing()
    elif message:
        addmsg(f"[{clock}] {username}: {message}")
        server.send(f"[{clock}] {username}: {message}".encode('utf-8'))
        entry.delete(0, tk.END)

threading.Thread(target=take).start()
addmsg(f"[{clock}] {username} sohbete katıldı.")
root.bind('<Return>', send)
root.protocol("WM_DELETE_WINDOW", closing)

root.mainloop()
