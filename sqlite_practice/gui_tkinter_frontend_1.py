import tkinter as tk

#Function for converting F to C
def convert_temp(fahr_value):
    return 5.0 * (fahr_value - 32) / 9

cels_value = 0
#Function run by button
def convert():
    fahr_value = float(entry_fahr.get())
    cels_value = convert_temp(fahr_value)
    lbl_cels["text"] = str(round(cels_value, 2)) + "\N{DEGREE CELSIUS}"

#Set up window
window = tk.Tk()
window.title("Temperature Converter")
window.resizable(0, 0)

frame = tk.Frame(window)
frame.grid(row=0, column=0, padx=10)

#Label for entry box
lbl_fahr = tk.Label(frame, text="\N{DEGREE FAHRENHEIT}")
lbl_fahr.grid(row=0, column=2, sticky="w")

#Entry box
entry_fahr = tk.Entry(frame, width=10)
entry_fahr.grid(row=0, column=1, sticky="e")

#Convert button
btn_convert = tk.Button(frame, text="\N{RIGHTWARDS BLACK ARROW}", command=convert)
btn_convert.grid(row=0, column=3, pady=10)

#Display Celsius value
lbl_cels = tk.Label(frame, text=str(cels_value) + "\N{DEGREE CELSIUS}")
lbl_cels.grid(row=0, column=4, padx=10)


window.mainloop()