import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import random
import string
import os
import subprocess
import zipfile
import shutil
from threading import Thread

class Variable:
    def __init__(self, name="var", var_type="整数", min_val=0, max_val=100, **kwargs):
        self.name = name
        self.var_type = var_type
        self.min_val = min_val
        self.max_val = max_val
        self.kwargs = kwargs  # 用于字符串长度、小数位数等

    def generate(self):
        if self.var_type == "整数":
            return random.randint(self.min_val, self.max_val)
        elif self.var_type == "浮点数":
            decimal = self.kwargs.get("decimal", 2)
            val = random.uniform(self.min_val, self.max_val)
            return round(val, decimal)
        elif self.var_type == "字符串":
            min_len = self.min_val
            max_len = self.max_val
            length = random.randint(min_len, max_len)
            charset = self.kwargs.get("charset", "ascii")
            if charset == "ascii":
                chars = string.ascii_letters + string.digits
            elif charset == "数字":
                chars = string.digits
            elif charset == "字母":
                chars = string.ascii_letters
            elif charset == "可打印":
                chars = string.printable.strip()
            else:
                chars = string.ascii_letters
            return ''.join(random.choice(chars) for _ in range(length))
        elif self.var_type == "字符":
            charset = self.kwargs.get("charset", "字母数字")
            if charset == "字母数字":
                pool = string.ascii_letters + string.digits
            elif charset == "字母":
                pool = string.ascii_letters
            elif charset == "数字":
                pool = string.digits
            else:
                pool = string.ascii_letters
            return random.choice(pool)
        elif self.var_type == "布尔值":
            return str(random.choice([True, False]))
        return ""

class TestPointGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("测试点生成器 v2.0")
        self.root.geometry("820x650")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f2f5")

        self.std_path = tk.StringVar()
        self.count = tk.StringVar(value="10")
        self.variables = []  # 存放 Variable 对象
        self.selected_idx = None

        self.build_ui()

    def build_ui(self):
        main = tk.Frame(self.root, bg="#f0f2f5")
        main.pack(fill="both", expand=True, padx=16, pady=16)

        # ===== 顶部：std选择 + 组数 =====
        top_frame = tk.Frame(main, bg="#f0f2f5")
        top_frame.pack(fill="x", pady=(0, 12))

        tk.Label(top_frame, text="📁 选择 std.exe:", font=("Inter", 12), bg="#f0f2f5").pack(side="left", padx=(0, 8))
        entry_std = tk.Entry(top_frame, textvariable=self.std_path, width=50)
        entry_std.pack(side="left", padx=(0, 8))
        tk.Button(top_frame, text="浏览", command=self.select_std, bg="#1890ff", fg="white").pack(side="left", padx=(0, 16))

        tk.Label(top_frame, text="组数:", font=("Inter", 12), bg="#f0f2f5").pack(side="left", padx=(0, 4))
        entry_count = tk.Entry(top_frame, textvariable=self.count, width=6)
        entry_count.pack(side="left")

        # ===== 中间：变量列表 =====
        list_frame = tk.Frame(main, bg="#f0f2f5")
        list_frame.pack(fill="both", expand=True, pady=(0, 12))

        tk.Label(list_frame, text="📋 变量列表", font=("Inter", 14, "bold"), bg="#f0f2f5").pack(anchor="w")

        # 列表头
        header = tk.Frame(list_frame, bg="#e8ecf1", height=30)
        header.pack(fill="x", pady=(4, 0))
        tk.Label(header, text="#", width=4, bg="#e8ecf1", font=("Inter", 11)).pack(side="left", padx=4)
        tk.Label(header, text="变量名", width=12, bg="#e8ecf1", font=("Inter", 11)).pack(side="left", padx=4)
        tk.Label(header, text="类型", width=10, bg="#e8ecf1", font=("Inter", 11)).pack(side="left", padx=4)
        tk.Label(header, text="参数", width=30, bg="#e8ecf1", font=("Inter", 11)).pack(side="left", padx=4)
        tk.Label(header, text="操作", width=10, bg="#e8ecf1", font=("Inter", 11)).pack(side="right", padx=4)

        self.listbox_frame = tk.Frame(list_frame, bg="white", height=200)
        self.listbox_frame.pack(fill="both", expand=True, pady=(0, 4))
        self.listbox_frame.pack_propagate(False)
        self.listbox_canvas = tk.Canvas(self.listbox_frame, bg="white", highlightthickness=0)
        self.listbox_scrollbar = tk.Scrollbar(self.listbox_frame, orient="vertical", command=self.listbox_canvas.yview)
        self.listbox_inner = tk.Frame(self.listbox_canvas, bg="white")
        self.listbox_canvas.configure(yscrollcommand=self.listbox_scrollbar.set)
        self.listbox_scrollbar.pack(side="right", fill="y")
        self.listbox_canvas.pack(side="left", fill="both", expand=True)
        self.canvas_window = self.listbox_canvas.create_window((0, 0), window=self.listbox_inner, anchor="nw", width=680)

        self.listbox_inner.bind("<Configure>", self._on_inner_configure)

        # 添加变量按钮
        add_btn = tk.Button(list_frame, text="➕ 添加变量", command=self.add_variable, bg="#52c41a", fg="white", font=("Inter", 11))
        add_btn.pack(anchor="w", pady=(4, 0))

        # ===== 变量编辑区 =====
        edit_frame = tk.Frame(main, bg="#fafafa", relief="groove", bd=1)
        edit_frame.pack(fill="x", pady=(0, 12))

        tk.Label(edit_frame, text="✏️ 变量详情", font=("Inter", 12, "bold"), bg="#fafafa").pack(anchor="w", padx=8, pady=(8, 4))

        self.edit_vars = {}
        row1 = tk.Frame(edit_frame, bg="#fafafa")
        row1.pack(fill="x", padx=8, pady=2)
        tk.Label(row1, text="变量名:", bg="#fafafa", width=8).pack(side="left")
        self.edit_vars["name"] = tk.Entry(row1, width=12)
        self.edit_vars["name"].pack(side="left", padx=(0, 16))
        tk.Label(row1, text="类型:", bg="#fafafa", width=8).pack(side="left")
        self.edit_vars["type"] = ttk.Combobox(row1, values=["整数", "浮点数", "字符串", "字符", "布尔值"], width=10, state="readonly")
        self.edit_vars["type"].pack(side="left")
        self.edit_vars["type"].bind("<<ComboboxSelected>>", self.on_type_change)

        row2 = tk.Frame(edit_frame, bg="#fafafa")
        row2.pack(fill="x", padx=8, pady=2)
        tk.Label(row2, text="参数:", bg="#fafafa", width=8).pack(side="left")
        self.edit_vars["param_frame"] = tk.Frame(row2, bg="#fafafa")
        self.edit_vars["param_frame"].pack(side="left", fill="x", expand=True)
        self.create_param_widgets("整数")

        row3 = tk.Frame(edit_frame, bg="#fafafa")
        row3.pack(fill="x", padx=8, pady=(4, 8))
        tk.Button(row3, text="更新变量", command=self.update_variable, bg="#1890ff", fg="white").pack(side="left", padx=(0, 8))
        tk.Button(row3, text="删除选中", command=self.delete_selected, bg="#ff4d4f", fg="white").pack(side="left")

        # ===== 底部：生成按钮 + 日志 =====
        bottom = tk.Frame(main, bg="#f0f2f5")
        bottom.pack(fill="x")

        btn_generate = tk.Button(bottom, text="🚀 生成测试点", command=self.start_generate,
                                 font=("Inter", 14, "bold"), bg="#52c41a", fg="white", padx=24, pady=8)
        btn_generate.pack(anchor="w", pady=(0, 8))

        self.log_text = tk.Text(bottom, height=8, font=("Consolas", 11), bg="#1a1a2e", fg="#e0e0e0", state="disabled")
        self.log_text.pack(fill="x")
        self.log_text.pack_propagate(False)

        # 初始添加一个默认变量
        self.add_variable()

    def create_param_widgets(self, var_type):
        # 清空旧的参数控件
        for w in self.edit_vars["param_frame"].winfo_children():
            w.destroy()

        if var_type == "整数":
            tk.Label(self.edit_vars["param_frame"], text="最小值:", bg="#fafafa").pack(side="left", padx=(0, 4))
            self.edit_vars["min"] = tk.Entry(self.edit_vars["param_frame"], width=8)
            self.edit_vars["min"].pack(side="left", padx=(0, 8))
            tk.Label(self.edit_vars["param_frame"], text="最大值:", bg="#fafafa").pack(side="left", padx=(0, 4))
            self.edit_vars["max"] = tk.Entry(self.edit_vars["param_frame"], width=8)
            self.edit_vars["max"].pack(side="left")
        elif var_type == "浮点数":
            tk.Label(self.edit_vars["param_frame"], text="最小值:", bg="#fafafa").pack(side="left", padx=(0, 4))
            self.edit_vars["min"] = tk.Entry(self.edit_vars["param_frame"], width=8)
            self.edit_vars["min"].pack(side="left", padx=(0, 8))
            tk.Label(self.edit_vars["param_frame"], text="最大值:", bg="#fafafa").pack(side="left", padx=(0, 4))
            self.edit_vars["max"] = tk.Entry(self.edit_vars["param_frame"], width=8)
            self.edit_vars["max"].pack(side="left", padx=(0, 8))
            tk.Label(self.edit_vars["param_frame"], text="小数位:", bg="#fafafa").pack(side="left", padx=(0, 4))
            self.edit_vars["decimal"] = tk.Entry(self.edit_vars["param_frame"], width=4)
            self.edit_vars["decimal"].insert(0, "2")
            self.edit_vars["decimal"].pack(side="left")
        elif var_type == "字符串":
            tk.Label(self.edit_vars["param_frame"], text="最小长度:", bg="#fafafa").pack(side="left", padx=(0, 4))
            self.edit_vars["min"] = tk.Entry(self.edit_vars["param_frame"], width=6)
            self.edit_vars["min"].pack(side="left", padx=(0, 8))
            tk.Label(self.edit_vars["param_frame"], text="最大长度:", bg="#fafafa").pack(side="left", padx=(0, 4))
            self.edit_vars["max"] = tk.Entry(self.edit_vars["param_frame"], width=6)
            self.edit_vars["max"].pack(side="left", padx=(0, 8))
            tk.Label(self.edit_vars["param_frame"], text="字符集:", bg="#fafafa").pack(side="left", padx=(0, 4))
            self.edit_vars["charset"] = ttk.Combobox(self.edit_vars["param_frame"], values=["ascii", "数字", "字母", "可打印"], width=8, state="readonly")
            self.edit_vars["charset"].set("ascii")
            self.edit_vars["charset"].pack(side="left")
        elif var_type == "字符":
            tk.Label(self.edit_vars["param_frame"], text="字符集:", bg="#fafafa").pack(side="left", padx=(0, 4))
            self.edit_vars["charset"] = ttk.Combobox(self.edit_vars["param_frame"], values=["字母数字", "字母", "数字"], width=10, state="readonly")
            self.edit_vars["charset"].set("字母数字")
            self.edit_vars["charset"].pack(side="left")
        elif var_type == "布尔值":
            tk.Label(self.edit_vars["param_frame"], text="(随机 True/False)", bg="#fafafa").pack(side="left")

    def on_type_change(self, event=None):
        var_type = self.edit_vars["type"].get()
        self.create_param_widgets(var_type)

    def _on_inner_configure(self, event):
        self.listbox_canvas.configure(scrollregion=self.listbox_canvas.bbox("all"))

    def select_std(self):
        path = filedialog.askopenfilename(title="选择 std.exe", filetypes=[("可执行文件", "*.exe")])
        if path:
            self.std_path.set(path)

    def add_variable(self):
        # 默认参数
        var = Variable("var", "整数", 1, 100)
        self.variables.append(var)
        self.refresh_list()
        # 选中新添加的
        self.selected_idx = len(self.variables) - 1
        self.load_to_edit(self.selected_idx)

    def refresh_list(self):
        for w in self.listbox_inner.winfo_children():
            w.destroy()
        for idx, var in enumerate(self.variables):
            row = tk.Frame(self.listbox_inner, bg="white" if idx % 2 == 0 else "#f8f9fa")
            row.pack(fill="x", pady=1)

            # 序号
            tk.Label(row, text=str(idx+1), width=4, bg=row["bg"]).pack(side="left", padx=4)
            tk.Label(row, text=var.name, width=12, bg=row["bg"], anchor="w").pack(side="left", padx=4)
            tk.Label(row, text=var.var_type, width=10, bg=row["bg"]).pack(side="left", padx=4)

            # 参数显示
            param_str = self._format_param(var)
            tk.Label(row, text=param_str, width=30, bg=row["bg"], anchor="w").pack(side="left", padx=4)

            # 删除按钮
            btn = tk.Button(row, text="×", command=lambda i=idx: self.delete_var(i), bg="#ff4d4f", fg="white", font=("Inter", 10), width=2)
            btn.pack(side="right", padx=4)

            # 点击行选择
            row.bind("<Button-1>", lambda e, i=idx: self.select_var(i))
            for child in row.winfo_children():
                child.bind("<Button-1>", lambda e, i=idx: self.select_var(i))

    def _format_param(self, var):
        if var.var_type == "整数":
            return f"{var.min_val} ~ {var.max_val}"
        elif var.var_type == "浮点数":
            dec = var.kwargs.get("decimal", 2)
            return f"{var.min_val} ~ {var.max_val} ({dec}位)"
        elif var.var_type == "字符串":
            return f"长度 {var.min_val} ~ {var.max_val}"
        elif var.var_type == "字符":
            charset = var.kwargs.get("charset", "字母数字")
            return f"字符集: {charset}"
        elif var.var_type == "布尔值":
            return "True/False"
        return ""

    def select_var(self, idx):
        self.selected_idx = idx
        self.load_to_edit(idx)
        self.refresh_list()

    def load_to_edit(self, idx):
        if idx is None or idx >= len(self.variables):
            return
        var = self.variables[idx]
        self.edit_vars["name"].delete(0, tk.END)
        self.edit_vars["name"].insert(0, var.name)
        self.edit_vars["type"].set(var.var_type)
        self.create_param_widgets(var.var_type)

        if var.var_type in ["整数", "浮点数", "字符串"]:
            if hasattr(var, "min_val"):
                self.edit_vars["min"].delete(0, tk.END)
                self.edit_vars["min"].insert(0, str(var.min_val))
            if hasattr(var, "max_val"):
                self.edit_vars["max"].delete(0, tk.END)
                self.edit_vars["max"].insert(0, str(var.max_val))
        if var.var_type == "浮点数":
            self.edit_vars["decimal"].delete(0, tk.END)
            self.edit_vars["decimal"].insert(0, str(var.kwargs.get("decimal", 2)))
        if var.var_type == "字符串":
            if "charset" in var.kwargs:
                self.edit_vars["charset"].set(var.kwargs["charset"])
        if var.var_type == "字符":
            if "charset" in var.kwargs:
                self.edit_vars["charset"].set(var.kwargs["charset"])

    def delete_var(self, idx):
        if 0 <= idx < len(self.variables):
            del self.variables[idx]
            if self.selected_idx == idx:
                self.selected_idx = None
            elif self.selected_idx is not None and self.selected_idx > idx:
                self.selected_idx -= 1
            self.refresh_list()
            if self.variables:
                self.load_to_edit(0)
            else:
                self.clear_edit()

    def delete_selected(self):
        if self.selected_idx is not None:
            self.delete_var(self.selected_idx)

    def clear_edit(self):
        for entry in self.edit_vars.values():
            if isinstance(entry, tk.Entry):
                entry.delete(0, tk.END)
        self.edit_vars["type"].set("")

    def update_variable(self):
        if self.selected_idx is None:
            messagebox.showwarning("提示", "请先选择要编辑的变量")
            return
        name = self.edit_vars["name"].get().strip()
        if not name:
            messagebox.showwarning("提示", "请输入变量名")
            return
        var_type = self.edit_vars["type"].get()
        if not var_type:
            messagebox.showwarning("提示", "请选择类型")
            return

        var = self.variables[self.selected_idx]
        var.name = name
        var.var_type = var_type

        # 读取参数
        if var_type == "整数":
            try:
                var.min_val = int(self.edit_vars["min"].get())
                var.max_val = int(self.edit_vars["max"].get())
                if var.min_val > var.max_val:
                    raise ValueError
            except:
                messagebox.showwarning("提示", "请输入有效的整数范围")
                return
            var.kwargs = {}
        elif var_type == "浮点数":
            try:
                var.min_val = float(self.edit_vars["min"].get())
                var.max_val = float(self.edit_vars["max"].get())
                if var.min_val > var.max_val:
                    raise ValueError
                var.kwargs["decimal"] = int(self.edit_vars["decimal"].get())
            except:
                messagebox.showwarning("提示", "请输入有效的浮点数范围")
                return
        elif var_type == "字符串":
            try:
                var.min_val = int(self.edit_vars["min"].get())
                var.max_val = int(self.edit_vars["max"].get())
                if var.min_val > var.max_val or var.min_val < 0:
                    raise ValueError
                var.kwargs["charset"] = self.edit_vars["charset"].get()
            except:
                messagebox.showwarning("提示", "请输入有效的长度范围")
                return
        elif var_type == "字符":
            var.kwargs["charset"] = self.edit_vars["charset"].get()
            var.min_val = var.max_val = 0
        elif var_type == "布尔值":
            var.min_val = var.max_val = 0
            var.kwargs = {}

        self.refresh_list()
        self.load_to_edit(self.selected_idx)

    def log(self, msg):
        self.log_text.config(state="normal")
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")
        self.root.update()

    def start_generate(self):
        std = self.std_path.get().strip()
        if not std or not os.path.exists(std):
            messagebox.showerror("错误", "请先选择有效的 std.exe")
            return
        try:
            count = int(self.count.get())
            if count <= 0:
                raise ValueError
        except:
            messagebox.showerror("错误", "请输入有效的正整数")
            return
        if not self.variables:
            messagebox.showerror("错误", "请至少添加一个变量")
            return

        Thread(target=self.run_generate, args=(std, count), daemon=True).start()

    def run_generate(self, std_path, count):
        self.log("=" * 50)
        self.log("🚀 开始生成测试点...")

        temp_dir = "temp_gen"
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)

        zip_name = "test_data"

        try:
            for i in range(1, count + 1):
                # 生成一行数据
                data_line = " ".join(str(var.generate()) for var in self.variables)
                in_path = os.path.join(temp_dir, f"{i}.in")
                with open(in_path, "w", encoding="utf-8") as f:
                    f.write(data_line + "\n")

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
                    self.log(f"❌ 第 {i} 组数据超时")
                except Exception as e:
                    self.log(f"❌ 第 {i} 组数据执行失败: {e}")

                self.log(f"✅ 已生成第 {i}/{count} 组测试点")

            zip_path = f"{zip_name}.zip"
            with zipfile.ZipFile(zip_path, "w") as zf:
                for fname in os.listdir(temp_dir):
                    zf.write(os.path.join(temp_dir, fname), fname)

            shutil.rmtree(temp_dir)

            self.log(f"\n🎉 所有测试点已生成！")
            self.log(f"📦 压缩包: {os.path.abspath(zip_path)}")
            self.log(f"📊 共 {count} 组数据，{len(self.variables)} 个变量")
            self.log("=" * 50)
            messagebox.showinfo("完成", f"✅ 测试点生成完成！\n共 {count} 组数据\n压缩包: {zip_path}")

        except Exception as e:
            self.log(f"❌ 生成失败: {e}")
            messagebox.showerror("错误", f"生成失败: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TestPointGenerator(root)
    root.mainloop()
