import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import random
import os
import subprocess
import zipfile
import shutil
import time
from threading import Thread

def generate_input(template, idx):
    parts = template.strip().split()
    output = []
    i = 0
    while i < len(parts):
        if i + 2 < len(parts) and parts[i+1].isdigit() and parts[i+2].isdigit():
            low = int(parts[i+1])
            high = int(parts[i+2])
            output.append(str(random.randint(low, high)))
            i += 3
        elif parts[i].isdigit():
            output.append(parts[i])
            i += 1
        else:
            output.append(parts[i])
            i += 1
    return " ".join(output)

class TestPointGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Test Point Generator v1.0")
        self.root.geometry("680x520")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f2f5")
        
        self.std_path = tk.StringVar(value="")
        self.template = tk.StringVar(value="n 1 100 a 1 100")
        self.count = tk.StringVar(value="10")
        self.zip_name = tk.StringVar(value="test_data")
        
        self.build_ui()
    
    def build_ui(self):
        main = tk.Frame(self.root, bg="#f0f2f5")
        main.pack(fill="both", expand=True, padx=20, pady=20)
        
        title = tk.Label(main, text="Test Point Generator", font=("Inter", 20, "bold"), bg="#f0f2f5")
        title.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 16))
        
        tk.Label(main, text="Select std.exe:", font=("Inter", 13), bg="#f0f2f5")\
            .grid(row=1, column=0, sticky="w", pady=4)
        
        frame_std = tk.Frame(main, bg="#f0f2f5")
        frame_std.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        entry_std = tk.Entry(frame_std, textvariable=self.std_path, font=("Inter", 12), width=60)
        entry_std.pack(side="left", padx=(0, 8))
        btn_std = tk.Button(frame_std, text="Browse", command=self.select_std, 
                            font=("Inter", 11), bg="#1890ff", fg="white", padx=12)
        btn_std.pack(side="left")
        
        tk.Label(main, text="Template (var min max):", font=("Inter", 13), bg="#f0f2f5")\
            .grid(row=3, column=0, sticky="w", pady=(4, 0))
        tk.Label(main, text="Example: n 1 100 a 1 100", 
                 font=("Inter", 11), bg="#f0f2f5", fg="#888")\
            .grid(row=4, column=0, sticky="w", pady=(0, 4))
        
        entry_template = tk.Entry(main, textvariable=self.template, font=("Inter", 12), width=60)
        entry_template.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        
        tk.Label(main, text="Number of test cases:", font=("Inter", 13), bg="#f0f2f5")\
            .grid(row=6, column=0, sticky="w", pady=4)
        entry_count = tk.Entry(main, textvariable=self.count, font=("Inter", 12), width=10)
        entry_count.grid(row=7, column=0, sticky="w", pady=(0, 12))
        
        tk.Label(main, text="Zip file name (without extension):", font=("Inter", 13), bg="#f0f2f5")\
            .grid(row=8, column=0, sticky="w", pady=4)
        entry_zip = tk.Entry(main, textvariable=self.zip_name, font=("Inter", 12), width=30)
        entry_zip.grid(row=9, column=0, sticky="w", pady=(0, 12))
        
        btn_generate = tk.Button(main, text="Generate Test Points", command=self.start_generate,
                                 font=("Inter", 14, "bold"), bg="#52c41a", fg="white", padx=24, pady=8)
        btn_generate.grid(row=10, column=0, pady=8, sticky="w")
        
        self.log_text = tk.Text(main, height=10, font=("Consolas", 11), bg="#1a1a2e", fg="#e0e0e0", state="disabled")
        self.log_text.grid(row=11, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        
        scrollbar = tk.Scrollbar(main, command=self.log_text.yview)
        scrollbar.grid(row=11, column=2, sticky="ns", padx=(0, 4))
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        tk.Label(main, text="std.exe must be in the same directory or specified via Browse", 
                 font=("Inter", 10), bg="#f0f2f5", fg="#aaa")\
            .grid(row=12, column=0, columnspan=2, sticky="w", pady=(8, 0))
    
    def log(self, msg):
        self.log_text.config(state="normal")
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")
        self.root.update()
    
    def select_std(self):
        path = filedialog.askopenfilename(title="Select std.exe", filetypes=[("Executable", "*.exe")])
        if path:
            self.std_path.set(path)
    
    def start_generate(self):
        std = self.std_path.get().strip()
        if not std:
            messagebox.showerror("Error", "Please select std.exe first")
            return
        if not os.path.exists(std):
            messagebox.showerror("Error", "std.exe not found")
            return
        
        try:
            count = int(self.count.get())
            if count <= 0:
                raise ValueError
        except:
            messagebox.showerror("Error", "Please enter a positive integer")
            return
        
        Thread(target=self.run_generate, args=(std, count), daemon=True).start()
    
    def run_generate(self, std_path, count):
        self.log("=" * 50)
        self.log("Start generating test points...")
        
        temp_dir = "temp_gen"
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)
        
        template = self.template.get().strip()
        zip_name = self.zip_name.get().strip() or "test_data"
        
        try:
            for i in range(1, count + 1):
                in_path = os.path.join(temp_dir, f"{i}.in")
                input_data = generate_input(template, i)
                with open(in_path, "w", encoding="utf-8") as f:
                    f.write(input_data + "\n")
                
                out_path = os.path.join(temp_dir, f"{i}.out")
                try:
                    with open(in_path, "r", encoding="utf-8") as f_in:
                        with open(out_path, "w", encoding="utf-8") as f_out:
                            result = subprocess.run(
                                [std_path],
                                stdin=f_in,
                                stdout=f_out,
                                stderr=subprocess.PIPE,
                                timeout=5
                            )
                    if result.returncode != 0:
                        self.log(f"Error at case {i}: {result.stderr.decode().strip()}")
                except subprocess.TimeoutExpired:
                    self.log(f"Timeout at case {i}")
                except Exception as e:
                    self.log(f"Failed at case {i}: {e}")
                
                self.log(f"Generated case {i}/{count}")
            
            zip_path = f"{zip_name}.zip"
            with zipfile.ZipFile(zip_path, "w") as zf:
                for fname in os.listdir(temp_dir):
                    zf.write(os.path.join(temp_dir, fname), fname)
            
            shutil.rmtree(temp_dir)
            
            self.log(f"\nAll test points generated!")
            self.log(f"Zip file: {os.path.abspath(zip_path)}")
            self.log(f"Total: {count} cases")
            self.log("=" * 50)
            
            messagebox.showinfo("Done", f"Generation complete!\n{count} cases\nZip: {zip_path}")
            
        except Exception as e:
            self.log(f"Generation failed: {e}")
            messagebox.showerror("Error", f"Generation failed: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TestPointGenerator(root)
    root.mainloop()
