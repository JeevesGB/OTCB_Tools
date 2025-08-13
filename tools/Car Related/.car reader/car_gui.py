import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os

class CarToolGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(".CAR File String Extractor/Rebuilder")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        self.file_path = ''
        self.csv_path = ''
        self.original_size = 0

        self.create_widgets()

    def create_widgets(self):
        tk.Button(self.root, text="Select .CAR File", command=self.load_car_file).pack(pady=5)
        tk.Button(self.root, text="Extract Strings to CSV", command=self.extract_strings).pack(pady=5)
        tk.Button(self.root, text="Select CSV to Rebuild", command=self.load_csv_file).pack(pady=5)

        self.size_entry = tk.Entry(self.root)
        self.size_entry.pack(pady=5, fill="x", padx=10, expand=True)
        self.size_entry.insert(0, "0")  # default value, will be updated when file is loaded


        tk.Button(self.root, text="Rebuild .CAR File", command=self.rebuild_car_file).pack(pady=10)

    def load_car_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("CAR files", "*.CAR")])
        if self.file_path:
            self.original_size = os.path.getsize(self.file_path)
            messagebox.showinfo("File Loaded", f"Loaded {self.file_path}\nSize: {self.original_size} bytes")

    def extract_strings(self):
        if not self.file_path:
            messagebox.showwarning("No File", "Please select a .CAR file first.")
            return
        output_csv = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if output_csv:
            subprocess.run(["python", "extract_strings_to_csv_v2.py", self.file_path, output_csv])
            messagebox.showinfo("Extraction Complete", f"Strings saved to {output_csv}")

    def load_csv_file(self):
        self.csv_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if self.csv_path:
            messagebox.showinfo("CSV Loaded", f"Loaded {self.csv_path}")

    def rebuild_car_file(self):
        if not self.csv_path:
            messagebox.showwarning("No CSV", "Please select a CSV file first.")
            return
        try:
            size = int(self.size_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Size", "Enter a valid number for the original file size.")
            return
        output_file = filedialog.asksaveasfilename(defaultextension=".CAR", filetypes=[("CAR files", "*.CAR")])
        if output_file:
            subprocess.run(["python", "convert_csv_to_binary_v2.py", self.csv_path, str(size), output_file])
            messagebox.showinfo("Rebuild Complete", f"Rebuilt CAR file saved to {output_file}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CarToolGUI(root)
    root.mainloop()
