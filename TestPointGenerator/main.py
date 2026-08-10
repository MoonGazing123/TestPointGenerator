import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import random
import os
import subprocess
import zipfile
import shutil
import time
from threading import Thread

# ========== 默认生成器 ==========
def generate_input(template, idx):
    """根据模板生成一组输入数据"""
    # 这里是一个示例模板解析器
    # 支持格式: "n 10 100" 表示生成一个在 [10, 100] 之间的 n
    #            "a 5 20" 表示生成一个在 [5, 20] 之间的 a
    #            固定值直接写数字
    parts = template.strip().split()
    output = []
    for part in parts:
        if part.isdigit():
            output.append(part)
        else:
            # 格式: 变量名 最小值 最大值
            # 简化处理：如果 part 是变量名，后面跟着范围
            # 这里我们只处理 "a b c" 这种格式
            pass
    # 如果模板为空，返回默认
    if not template.strip():
        return f"{random.randint(1, 100)} {random.randint(1, 100)}"
    # 尝试解析：假设格式为 "变量1 范围1 范围2 变量2 范围3 范围4 ..."
    tokens = template.split()
    result = []
    i = 0
    while i < len(tokens):
        if i + 2 < len(tokens) and tokens[i+1].isdigit() and tokens[i+2].isdigit():
            # 变量 最小值 最大值
            low = int(tokens[i+1])
            high = int(tokens[i+2])
            result.append(str(random.randint(low, high)))
            i += 3
        elif tokens[i].isdigit():
            result.append(tokens[i])
            i += 1
        else:
            # 单个值，直接输出
            result.append(tokens[i])
            i += 1
    return " ".join(result)

# ========== GUI 主程序 ==========
class TestPointGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("测试点生成器 v1.0")
        self.root.geometry("680x520")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f2f5")
        
        # 状态变量
        self.std_path = tk.StringVar(value="")
        self.template = tk.StringVar(value="n 1 100 a 1 100")
        self.count = tk.StringVar(value="10")
        self.zip_name = tk.StringVar(value="test_data")
        
        self.build_ui()
    
    def build_ui(self):
        # 主容器
        main = tk.Frame(self.root, bg="#f0f2f5")
        main.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 标题
        title = tk.Label(main, text="⚙️ 测试点生成器", font=("Inter", 20, "bold"), bg="#f0f2f5")
        title.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 16))
        
        # ===== 第1行：选择 std.exe =====
        tk.Label(main, text="📁 选择标准程序 (std.exe):", font=("Inter", 13), bg="#f0f2f5")\
            .grid(row=1, column=0, sticky="w", pady=4)
        
        frame_std = tk.Frame(main, bg="#f0f2f5")
        frame_std.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        entry_std = tk.Entry(frame_std, textvariable=self.std_path, font=("Inter", 12), width=60)
        entry_std.pack(side="left", padx=(0, 8))
        btn_std = tk.Button(frame_std, text="浏览", command=self.select_std, 
                            font=("Inter", 11), bg="#1890ff", fg="white", padx=12)
        btn_std.pack(side="left")
        
        # ===== 第2行：数据模板 =====
        tk.Label(main, text="📝 数据生成模板 (变量 最小值 最大值):", font=("Inter", 13), bg="#f0f2f5")\
            .grid(row=3, column=0, sticky="w", pady=(4, 0))
        tk.Label(main, text="示例: n 1 100 a 1 100  → 生成 n 和 a 各在 [1,100] 随机", 
                 font=("Inter", 11), bg="#f0f2f5", fg="#888")\
            .grid(row=4, column=0, sticky="w", pady=(0, 4))
        
        entry_template = tk.Entry(main, textvariable=self.template, font=("Inter", 12), width=60)
        entry_template.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        
        # ===== 第3行：生成数量 =====
        tk.Label(main, text="📊 生成数据组数:", font=("Inter", 13), bg="#f0f2f5")\
            .grid(row=6, column=0, sticky="w", pady=4)
        entry_count = tk.Entry(main, textvariable=self.count, font=("Inter", 12), width=10)
        entry_count.grid(row=7, column=0, sticky="w", pady=(0, 12))
        
        # ===== 第4行：Zip文件名 =====
        tk.Label(main, text="📦 输出 Zip 文件名 (不含后缀):", font=("Inter", 13), bg="#f0f2f5")\
            .grid(row=8, column=0, sticky="w", pady=4)
        entry_zip = tk.Entry(main, textvariable=self.zip_name, font=("Inter", 12), width=30)
        entry_zip.grid(row=9, column=0, sticky="w", pady=(0, 12))
        
        # ===== 生成按钮 =====
        btn_generate = tk.Button(main, text="🚀 生成测试点", command=self.start_generate,
                                 font=("Inter", 14, "bold"), bg="#52c41a", fg="white", padx=24, pady=8)
        btn_generate.grid(row=10, column=0, pady=8, sticky="w")
        
        # ===== 进度/日志区域 =====
        self.log_text = tk.Text(main, height=10, font=("Consolas", 11), bg="#1a1a2e", fg="#e0e0e0", state="disabled")
        self.log_text.grid(row=11, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        
        # 滚动条
        scrollbar = tk.Scrollbar(main, command=self.log_text.yview)
        scrollbar.grid(row=11, column=2, sticky="ns", padx=(0, 4))
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # 底部信息
        tk.Label(main, text="需要 std.exe 与当前程序在同一目录，或通过浏览指定", 
                 font=("Inter", 10), bg="#f0f2f5", fg="#aaa")\
            .grid(row=12, column=0, columnspan=2, sticky="w", pady=(8, 0))
    
    def log(self, msg):
        self.log_text.config(state="normal")
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")
        self.root.update()
    
    def select_std(self):
        path = filedialog.askopenfilename(title="选择 std.exe", filetypes=[("可执行文件", "*.exe")])
        if path:
            self.std_path.set(path)
    
    def start_generate(self):
        # 检查 std.exe
        std = self.std_path.get().strip()
        if not std:
            messagebox.showerror("错误", "请先选择 std.exe 文件")
            return
        if not os.path.exists(std):
            messagebox.showerror("错误", "std.exe 文件不存在")
            return
        
        try:
            count = int(self.count.get())
            if count <= 0:
                raise ValueError
        except:
            messagebox.showerror("错误", "请输入有效的正整数作为数据组数")
            return
        
        # 在新线程中执行，避免界面卡死
        Thread(target=self.run_generate, args=(std, count), daemon=True).start()
    
    def run_generate(self, std_path, count):
        self.log("=" * 50)
        self.log("🚀 开始生成测试点...")
        
        # 创建临时目录
        temp_dir = "temp_gen"
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)
        
        template = self.template.get().strip()
        zip_name = self.zip_name.get().strip() or "test_data"
        
        try:
            for i in range(1, count + 1):
                # 生成 .in 文件
                in_path = os.path.join(temp_dir, f"{i}.in")
                input_data = generate_input(template, i)
                with open(in_path, "w", encoding="utf-8") as f:
                    f.write(input_data + "\n")
                
                # 调用 std.exe 生成 .out
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
                        self.log(f"⚠️ 第 {i} 组数据执行出错: {result.stderr.decode().strip()}")
                except subprocess.TimeoutExpired:
                    self.log(f"❌ 第 {i} 组数据执行超时 (5秒)")
                except Exception as e:
                    self.log(f"❌ 第 {i} 组数据执行失败: {e}")
                
                self.log(f"✅ 已生成第 {i}/{count} 组测试点")
            
            # 打包成 zip
            zip_path = f"{zip_name}.zip"
            with zipfile.ZipFile(zip_path, "w") as zf:
                for fname in os.listdir(temp_dir):
                    zf.write(os.path.join(temp_dir, fname), fname)
            
            # 清理临时目录
            shutil.rmtree(temp_dir)
            
            self.log(f"\n🎉 所有测试点已生成！")
            self.log(f"📦 压缩包: {os.path.abspath(zip_path)}")
            self.log(f"📊 共 {count} 组数据")
            self.log("=" * 50)
            
            messagebox.showinfo("完成", f"✅ 测试点生成完成！\n共 {count} 组数据\n压缩包: {zip_path}")
            
        except Exception as e:
            self.log(f"❌ 生成失败: {e}")
            messagebox.showerror("错误", f"生成失败: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TestPointGenerator(root)
    root.mainloop()