
import tkinter as tk
import time

def test_gui():
    print("Testing Tkinter... Window should appear shortly.")
    root = tk.Tk()
    root.title("Diagnostic Window")
    root.geometry("300x300")
    root.configure(bg="blue")

    label = tk.Label(root, text="IF YOU SEE THIS,\nTKINTER IS WORKING!",
                     fg="white", bg="blue", font=("Arial", 16, "bold"))
    label.pack(expand=True)

    print("Mainloop starting. Window should be blue with white text.")
    print("Close the window or press Ctrl+C to finish.")

    root.mainloop()
    print("Mainloop finished.")

if __name__ == "__main__":
    try:
        test_gui()
    except Exception as e:
        print(f"ERROR: {e}")
