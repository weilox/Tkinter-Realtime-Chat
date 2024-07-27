from tkinter import scrolledtext, messagebox
import socket, os, threading, time, tkinter as tk

host = "localhost"
port = 2000

clock = time.strftime("%d-%m-%Y %H:%M")
def addmsg(message):
    messages.configure(state=tk.NORMAL)
    messages.insert(tk.END, message + "\n")
    messages.configure(state=tk.DISABLED)
    messages.see(tk.END)
def closing():
    addmsg(f"[{clock}] Server closed.")
    open("logs.txt", "a").write(f"[{clock}] Server closed.\n")
    os._exit(0)

if(not os.path.exists("logs.txt")): open("logs.txt","w")
if(not os.path.exists("banned.txt")): open("banned.txt","w")

connected_socket = []
connected_address = []

def isbanned(client_socket,client_address):
    while True:
        with open("banned.txt", "r") as file:
            for i in file:
                if(i.strip() == client_address[0]):
                    addmsg(f"[{clock}] {connected_address[0]} was banned.")
                    open("logs.txt", "a").write(f"[{clock}] {connected_address[0]} was banned.\n")
                    client_socket.close()
                    return

def broadcast(message, sender_socket=None, client_address=None):
    for client_socket in connected_socket:
        if client_socket != sender_socket:
            try:
                client_socket.send(message.encode('utf-8'))
            except Exception: remove(client_socket, client_address)

def remove(client_socket, client_address):
    if (client_socket in connected_socket): connected_socket.remove(client_socket)
    if (client_address[0] in connected_address): connected_address.remove(client_address[0])
    client_socket.close()

def listen(client_socket, client_address, username):
    try:
        threading.Thread(target=isbanned, args=(client_socket,client_address)).start()
        addmsg(f"[{clock}] [{client_address[0]}] {username} connected.")
        open("logs.txt", "a", encoding="utf-8").write(f"[{clock}] [{client_address[0]}] {username} connected.\n")
        broadcast(f"[{time.strftime("%H:%M")}] {username} joined to chat.", client_socket, client_address)
        connected_socket.append(client_socket);connected_address.append(client_address[0])
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                broadcast(message, client_socket, client_address)
            else:
                remove(client_socket, client_address)
                break
    except ConnectionResetError: 
        addmsg(f"[{clock}] [{client_address[0]}] {username} left the chat.")
        open("logs.txt", "a", encoding="utf-8").write(f"[{clock}] [{client_address[0]}] {username} left the chat.\n")
        remove(client_socket, client_address)
    except ConnectionAbortedError: remove(client_socket, client_address)

def control(client_socket, client_address, username):
    with open("banned.txt", "r") as file:
        for i in file:
            if(i.strip() == client_address[0]):
                addmsg(f"[{clock}] The banned user {username} tried to connect via {client_address[0]}.")
                open("logs.txt", "a").write(f"[{clock}] The banned user {username} tried to connect via {client_address[0]}.\n")
                client_socket.close()
                return False
    if(client_address[0] in connected_address):
        addmsg(f"[{clock}] {connected_address[0]} tried to connect twice.")
        open("logs.txt", "a").write(f"[{clock}] {connected_address[0]} tried to connect twice.\n")
        client_socket.close()
        return False
    return True

def command(event):
    cmd = entry.get().strip()
    if cmd == "exit": closing()
    elif entry.get().strip() == "logs": os.system(f'notepad logs.txt')
    elif cmd.startswith("ban "):
        ip = cmd[4:].strip()
        with open("banned.txt","a") as file:file.write(f"{ip}\n")
        addmsg(f"[{clock}] {ip} was added to banned list.")
        open("logs.txt", "a").write(f"[{clock}] {ip} was added to banned list.\n")
    elif cmd.startswith("unban "):
        ip = cmd[6:].strip()
        with open("banned.txt", "r") as file: lines = file.readlines()
        with open("banned.txt", "w") as file:
            for line in lines:
                if line.strip() != ip:
                    file.write(line)
        addmsg(f"[{clock}] {ip} unbanned.")
        open("logs.txt", "a").write(f"[{clock}] {ip} unbanned.\n")
    elif cmd.startswith("say "):
        message = cmd[4:].strip()
        broadcast(f"[{time.strftime('%H:%M')}] Server: {message}")
    entry.delete(0, tk.END)

def start():
    server.listen()
    addmsg(f"[{clock}] Server started.")
    open("logs.txt", "a").write(f"[{clock}] Server started.\n")
    while True:
        client_socket, client_address = server.accept()
        username = client_socket.recv(1024).decode()
        if(control(client_socket, client_address, username) != False):
            threading.Thread(target=listen, args=(client_socket, client_address, username)).start()

try:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
except OSError:messagebox.showerror("Error", "Server is already running!"); closing()

root = tk.Tk()
root.title("Server")
root.geometry("740x400")
root.iconbitmap("icon.ico")
root.configure(bg='#222')
root.resizable(False, False)
root.protocol("WM_DELETE_WINDOW", closing)

messages = scrolledtext.ScrolledText(root, height=19, padx=10, bg="#222", fg="#fff", spacing1=2, spacing3=2)
messages.pack(fill=tk.BOTH)

entry = tk.Entry(root, width=120)
entry.pack(fill=tk.X)
entry.focus_set()

threading.Thread(target=start).start()
root.bind('<Return>', command)

root.mainloop()
