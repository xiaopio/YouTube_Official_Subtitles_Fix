import re
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime


class SRTFixerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SRT字幕修复工具")
        self.root.geometry("600x400")
        self.root.resizable(True, True)

        # 设置样式
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("微软雅黑", 10))
        self.style.configure("TButton", font=("微软雅黑", 10))
        self.style.configure("Accent.TButton", font=("微软雅黑", 10, "bold"))

        # 输入文件路径
        self.input_path = tk.StringVar()

        # 输出文件路径
        self.output_path = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 标题
        title_label = ttk.Label(main_frame, text="SRT字幕修复工具", font=("微软雅黑", 16, "bold"))
        title_label.pack(pady=(0, 20))

        # 文件选择区域（替代拖放区域，避免兼容性问题）
        self.select_frame = ttk.Frame(main_frame, relief=tk.RAISED, padding="30", borderwidth=2)
        self.select_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        # 点击区域添加事件
        self.select_frame.bind("<Button-1>", lambda e: self.browse_input())
        self.select_frame.configure(cursor="hand2")  # 鼠标悬停显示手型

        select_label = ttk.Label(
            self.select_frame,
            text="点击此处选择SRT文件",
            font=("微软雅黑", 12)
        )
        select_label.pack(expand=True)
        select_label.bind("<Button-1>", lambda e: self.browse_input())
        select_label.configure(cursor="hand2")

        # 文件路径显示
        path_frame = ttk.Frame(main_frame)
        path_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(path_frame, text="输入文件:").pack(side=tk.LEFT, padx=(0, 10))

        input_entry = ttk.Entry(path_frame, textvariable=self.input_path, state="readonly", width=50)
        input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        browse_btn = ttk.Button(path_frame, text="浏览", command=self.browse_input)
        browse_btn.pack(side=tk.RIGHT)

        # 输出路径
        output_frame = ttk.Frame(main_frame)
        output_frame.pack(fill=tk.X, pady=(0, 20))

        ttk.Label(output_frame, text="输出位置:").pack(side=tk.LEFT, padx=(0, 10))

        output_entry = ttk.Entry(output_frame, textvariable=self.output_path, state="readonly", width=50)
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        output_btn = ttk.Button(output_frame, text="选择", command=self.browse_output)
        output_btn.pack(side=tk.RIGHT)

        # 处理按钮
        process_frame = ttk.Frame(main_frame)
        process_frame.pack(fill=tk.X, pady=(20, 0))

        process_btn = ttk.Button(process_frame, text="处理字幕文件", command=self.process_file, style="Accent.TButton")
        process_btn.pack(side=tk.RIGHT)

        # 状态标签
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, foreground="green")
        status_label.pack(anchor=tk.W, pady=(10, 0))

    def browse_input(self):
        # 浏览选择输入文件
        file_path = filedialog.askopenfilename(
            title="选择SRT文件",
            filetypes=[("SRT文件", "*.srt"), ("所有文件", "*.*")]
        )

        if file_path:
            self.input_path.set(file_path)

            # 自动生成输出路径
            dir_name, file_name = os.path.split(file_path)
            name, ext = os.path.splitext(file_name)
            self.output_path.set(os.path.join(dir_name, f"{name}_fixed{ext}"))

    def browse_output(self):
        # 浏览选择输出位置
        if not self.input_path.get():
            messagebox.showwarning("警告", "请先选择输入文件")
            return

        default_dir, default_file = os.path.split(self.output_path.get() or self.input_path.get())
        file_path = filedialog.asksaveasfilename(
            title="保存修复后的文件",
            defaultextension=".srt",
            filetypes=[("SRT文件", "*.srt"), ("所有文件", "*.*")],
            initialdir=default_dir,
            initialfile=default_file
        )

        if file_path:
            self.output_path.set(file_path)

    def process_file(self):
        # 处理SRT文件
        input_path = self.input_path.get()
        output_path = self.output_path.get()

        if not input_path:
            messagebox.showwarning("警告", "请选择输入文件")
            return

        if not output_path:
            messagebox.showwarning("警告", "请选择输出位置")
            return

        try:
            self.status_var.set("正在处理...")
            self.root.update()

            # 读取SRT内容
            with open(input_path, 'r', encoding='utf-8') as f:
                srt_content = f.read()

            # 解析SRT
            entries = self.parse_srt(srt_content)

            # 修复重叠
            entries = self.fix_overlapping(entries)

            # 生成新的SRT
            new_srt = self.generate_srt(entries)

            # 写入输出文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(new_srt)

            self.status_var.set("处理完成!")
            messagebox.showinfo("成功", f"文件已保存至:\n{output_path}")

        except Exception as e:
            self.status_var.set("处理失败")
            messagebox.showerror("错误", f"处理过程中发生错误:\n{str(e)}")

    def time_to_ms(self, time_str):
        """将SRT时间格式转换为毫秒数"""
        time_str = time_str.replace(',', '.')
        try:
            dt = datetime.strptime(time_str, "%H:%M:%S.%f")
            return int((dt.hour * 3600 + dt.minute * 60 + dt.second) * 1000 + dt.microsecond / 1000)
        except ValueError:
            # 处理可能的格式错误
            return 0

    def ms_to_time(self, ms):
        """将毫秒数转换为SRT时间格式"""
        hours = ms // 3600000
        ms %= 3600000
        minutes = ms // 60000
        ms %= 60000
        seconds = ms // 1000
        ms %= 1000
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{ms:03d}"

    def parse_srt(self, srt_content):
        """解析SRT内容为条目列表"""
        blocks = re.split(r'\n\s*\n', srt_content.strip())
        entries = []

        for block in blocks:
            lines = [line.strip() for line in block.split('\n') if line.strip()]
            if len(lines) < 2:
                continue

            index = lines[0]
            time_line = lines[1]
            start_str, end_str = re.split(r'\s*-->\s*', time_line)

            start_ms = self.time_to_ms(start_str)
            end_ms = self.time_to_ms(end_str)

            text = ' '.join(lines[2:]) if len(lines) > 2 else ''

            entries.append({
                'index': index,
                'start_ms': start_ms,
                'end_ms': end_ms,
                'text': text
            })

        return sorted(entries, key=lambda x: x['start_ms'])

    def fix_overlapping(self, entries):
        """修复时间轴重叠"""
        for i in range(len(entries) - 1):
            current = entries[i]
            next_entry = entries[i + 1]

            if current['end_ms'] > next_entry['start_ms']:
                current['end_ms'] = next_entry['start_ms']

        return entries

    def process_punctuation(self, text):
        """处理标点符号"""
        if not text:
            return text

        punctuation = ',.!?;:"\'()[]{}<>、，。！？；：“”‘’（）【】《》'

        # 去除开头的标点
        start_idx = 0
        while start_idx < len(text) and text[start_idx] in punctuation:
            start_idx += 1

        # 去除结尾的标点
        end_idx = len(text) - 1
        while end_idx >= 0 and text[end_idx] in punctuation:
            end_idx -= 1

        if start_idx > end_idx:
            return ''

        trimmed = text[start_idx:end_idx + 1]

        # 句中的标点替换为两个空格
        processed = []
        for char in trimmed:
            if char in punctuation:
                processed.append('  ')
            else:
                processed.append(char)

        return ''.join(processed)

    def generate_srt(self, entries):
        """生成SRT格式字符串"""
        srt_lines = []

        for i, entry in enumerate(entries, 1):
            srt_lines.append(str(i))
            start_time = self.ms_to_time(entry['start_ms'])
            end_time = self.ms_to_time(entry['end_ms'])
            srt_lines.append(f"{start_time} --> {end_time}")
            srt_lines.append(self.process_punctuation(entry['text']))
            srt_lines.append('')

        return '\n'.join(srt_lines).rstrip()


if __name__ == "__main__":
    root = tk.Tk()
    app = SRTFixerApp(root)
    root.mainloop()
