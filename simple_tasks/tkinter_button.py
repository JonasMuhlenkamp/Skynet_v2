import tkinter as tk
import webbrowser

def open_mail():
    chrome_path = "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s"
    webbrowser.get(chrome_path).open("mail.google.com")

root = tk.Tk()
frame = tk.Frame(root)
frame.pack()

button = tk.Button(frame, text="QUIT", fg="red", command=quit)
button.pack(side = tk.LEFT)

mail = tk.Button(frame, text="MAIL", bg="green", command=open_mail)
mail.pack(side = tk.LEFT)

root.mainloop()

