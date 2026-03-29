import tkinter as tk
from tkinter import filedialog, messagebox
import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont
import io
import os
import platform
import sys

class StampApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Постановка печати на документ")
        self.root.geometry("500x450")
        
        # Переменные для хранения путей к файлам
        self.document_path = None
        self.stamp_path = None
        self.output_path = None
        self.document_type = None
        
        # Фиксированное качество 600 DPI
        self.quality_dpi = 600
        
        # Печать полностью непрозрачная
        self.stamp_opacity = 1.0  # 100% непрозрачность
        
        # Определяем путь к шрифту (для текста если понадобится)
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        elif '__file__' in globals():
            application_path = os.path.dirname(os.path.abspath(__file__))
        else:
            application_path = os.path.dirname(os.path.abspath(sys.argv[0])) if sys.argv[0] else os.getcwd()
        
        self.setup_ui()
    
    def setup_ui(self):
        # Заголовок
        title_label = tk.Label(
            self.root, 
            text="Постановка печати на документ", 
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=10)
        
        # Фрейм для выбора документа
        doc_frame = tk.Frame(self.root)
        doc_frame.pack(pady=5, fill='x', padx=20)
        
        tk.Label(doc_frame, text="1. Выберите PDF документ:", font=("Arial", 10)).pack(anchor='w')
        
        doc_select_frame = tk.Frame(doc_frame)
        doc_select_frame.pack(fill='x', pady=2)
        
        self.doc_entry = tk.Entry(doc_select_frame, width=50)
        self.doc_entry.pack(side='left', padx=(0, 5))
        
        tk.Button(
            doc_select_frame, 
            text="Обзор...", 
            command=self.select_document,
            bg="#4CAF50",
            fg="white"
        ).pack(side='left')
        
        self.doc_type_label = tk.Label(
            doc_frame,
            text="",
            font=("Arial", 8),
            fg="blue"
        )
        self.doc_type_label.pack(anchor='w', pady=(2, 0))
        
        # Фрейм для выбора печати
        stamp_frame = tk.Frame(self.root)
        stamp_frame.pack(pady=5, fill='x', padx=20)
        
        tk.Label(stamp_frame, text="2. Выберите изображение печати:", font=("Arial", 10)).pack(anchor='w')
        
        stamp_select_frame = tk.Frame(stamp_frame)
        stamp_select_frame.pack(fill='x', pady=2)
        
        self.stamp_entry = tk.Entry(stamp_select_frame, width=50)
        self.stamp_entry.pack(side='left', padx=(0, 5))
        
        tk.Button(
            stamp_select_frame, 
            text="Обзор...", 
            command=self.select_stamp,
            bg="#4CAF50",
            fg="white"
        ).pack(side='left')
        
        # Параметры печати
        options_frame = tk.LabelFrame(self.root, text="3. Параметры печати", padx=10, pady=10)
        options_frame.pack(pady=10, fill='x', padx=20)
        
        # Размер печати
        size_frame = tk.Frame(options_frame)
        size_frame.pack(fill='x', pady=2)
        
        tk.Label(size_frame, text="Размер печати (мм):", width=15, anchor='w').pack(side='left')
        self.size_var = tk.StringVar(value="40")
        tk.Entry(size_frame, textvariable=self.size_var, width=10).pack(side='left')
        
        # Отступ справа
        margin_right_frame = tk.Frame(options_frame)
        margin_right_frame.pack(fill='x', pady=2)
        
        tk.Label(margin_right_frame, text="Отступ справа (мм):", width=15, anchor='w').pack(side='left')
        self.margin_right_var = tk.StringVar(value="50")
        tk.Entry(margin_right_frame, textvariable=self.margin_right_var, width=10).pack(side='left')
        
        # Отступ снизу
        margin_bottom_frame = tk.Frame(options_frame)
        margin_bottom_frame.pack(fill='x', pady=2)
        
        tk.Label(margin_bottom_frame, text="Отступ снизу (мм):", width=15, anchor='w').pack(side='left')
        self.margin_bottom_var = tk.StringVar(value="50")
        tk.Entry(margin_bottom_frame, textvariable=self.margin_bottom_var, width=10).pack(side='left')
        
        # Кнопка
        self.stamp_button = tk.Button(
            self.root,
            text="ПОСТАВИТЬ ПЕЧАТЬ",
            command=self.add_stamp,
            bg="#2196F3",
            fg="white",
            font=("Arial", 12, "bold"),
            height=2,
            width=25
        )
        self.stamp_button.pack(pady=10)
        
        self.status_label = tk.Label(
            self.root,
            text="Выберите файлы для начала работы",
            font=("Arial", 9),
            fg="gray"
        )
        self.status_label.pack(pady=5)
    
    def select_document(self):
        filename = filedialog.askopenfilename(
            title="Выберите PDF документ",
            filetypes=[
                ("PDF файлы", "*.pdf"),
                ("Все файлы", "*.*")
            ]
        )
        if filename:
            self.document_path = filename
            self.document_type = 'pdf'
            self.doc_type_label.config(text="📄 PDF документ", fg="blue")
            self.doc_entry.delete(0, tk.END)
            self.doc_entry.insert(0, filename)
            self.update_status()
    
    def select_stamp(self):
        filename = filedialog.askopenfilename(
            title="Выберите изображение печати",
            filetypes=[("Изображения", "*.png *.jpg *.jpeg *.gif *.bmp"), ("PNG", "*.png")]
        )
        if filename:
            self.stamp_path = filename
            self.stamp_entry.delete(0, tk.END)
            self.stamp_entry.insert(0, filename)
            self.update_status()
    
    def update_status(self):
        if not self.document_path:
            self.status_label.config(text="Выберите PDF документ", fg="gray")
        elif not self.stamp_path:
            self.status_label.config(text="Выберите изображение печати", fg="orange")
        else:
            self.status_label.config(text="✅ Все файлы выбраны", fg="green")
    
    def apply_opacity(self, image, opacity):
        # При opacity = 1.0 изображение остается без изменений
        if opacity >= 1.0:
            return image
            
        if image.mode == 'RGBA':
            r, g, b, a = image.split()
            a = a.point(lambda p: p * opacity)
            return Image.merge('RGBA', (r, g, b, a))
        else:
            image = image.convert('RGBA')
            r, g, b, a = image.split()
            a = a.point(lambda p: p * opacity)
            return Image.merge('RGBA', (r, g, b, a))
    
    def add_stamp(self):
        if not self.document_path or not self.stamp_path:
            messagebox.showerror("Ошибка", "Выберите файлы!")
            return
        
        try:
            # Получаем настройки от пользователя
            stamp_width_mm = float(self.size_var.get())
            margin_right_mm = float(self.margin_right_var.get())
            margin_bottom_mm = float(self.margin_bottom_var.get())
            
            self.output_path = filedialog.asksaveasfilename(
                title="Сохранить PDF",
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                initialfile="document_with_stamp.pdf"
            )
            
            if not self.output_path:
                return
            
            self.status_label.config(text="⏳ Обработка...", fg="blue")
            self.root.update()
            
            # Открываем PDF
            doc = fitz.open(self.document_path)
            
            # Открываем изображение печати
            stamp_pil = Image.open(self.stamp_path)
            
            # Применяем прозрачность (1.0 - без изменений)
            if self.stamp_opacity < 1.0:
                stamp_pil = self.apply_opacity(stamp_pil, self.stamp_opacity)
            
            # Конвертируем мм в points (1 мм = 2.83 points)
            stamp_width = stamp_width_mm * 2.83
            margin_right = margin_right_mm * 2.83
            margin_bottom = margin_bottom_mm * 2.83
            
            scale_factor = self.quality_dpi / 72
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                rect = page.rect
                
                # Позиция печати (правый нижний угол)
                stamp_x = rect.width - stamp_width - margin_right
                stamp_y = rect.height - stamp_width - margin_bottom
                
                # Масштабируем печать
                stamp_resized = stamp_pil.resize(
                    (int(stamp_width * scale_factor), 
                     int(stamp_width * stamp_pil.height / stamp_pil.width * scale_factor)),
                    Image.Resampling.LANCZOS
                )
                
                stamp_bytes = io.BytesIO()
                stamp_resized.save(stamp_bytes, format='PNG')
                stamp_bytes.seek(0)
                
                # Вставляем печать
                page.insert_image(
                    fitz.Rect(stamp_x, stamp_y, stamp_x + stamp_width, stamp_y + stamp_width),
                    pixmap=fitz.Pixmap(stamp_bytes.read())
                )
            
            # Сохраняем результат
            doc.save(self.output_path, garbage=4, deflate=True)
            doc.close()
            
            self.status_label.config(text="✅ Готово!", fg="green")
            messagebox.showinfo("Успех", f"Печать успешно поставлена!\n\nФайл сохранен:\n{self.output_path}")
            
        except Exception as e:
            self.status_label.config(text="❌ Ошибка", fg="red")
            messagebox.showerror("Ошибка", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = StampApp(root)
    root.mainloop()