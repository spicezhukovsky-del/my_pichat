import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import fitz  # PyMuPDF
from PIL import Image, ImageTk
import io
import os
import tempfile

class StampApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Постановка печати на документ")
        self.root.geometry("600x500")
        
        # Переменные для хранения путей к файлам
        self.document_path = None
        self.stamp_path = None
        self.output_path = None
        self.document_type = None  # 'pdf' или 'image'
        
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
        
        tk.Label(doc_frame, text="1. Выберите документ (PDF или изображение):", font=("Arial", 10)).pack(anchor='w')
        
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
        
        # Метка для отображения типа документа
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
        
        # Отступы
        margin_frame = tk.Frame(options_frame)
        margin_frame.pack(fill='x', pady=2)
        
        tk.Label(margin_frame, text="Отступ справа (мм):", width=15, anchor='w').pack(side='left')
        self.margin_right_var = tk.StringVar(value="50")
        tk.Entry(margin_frame, textvariable=self.margin_right_var, width=10).pack(side='left')
        
        margin_frame2 = tk.Frame(options_frame)
        margin_frame2.pack(fill='x', pady=2)
        
        tk.Label(margin_frame2, text="Отступ снизу (мм):", width=15, anchor='w').pack(side='left')
        self.margin_bottom_var = tk.StringVar(value="50")
        tk.Entry(margin_frame2, textvariable=self.margin_bottom_var, width=10).pack(side='left')
        
        # Информация о положении
        info_label = tk.Label(
            options_frame,
            text="📌 Печать ставится в правый нижний угол",
            font=("Arial", 9),
            fg="#666"
        )
        info_label.pack(pady=(5, 0))
        
        # Кнопка для постановки печати
        self.stamp_button = tk.Button(
            self.root,
            text="🖨️ ПОСТАВИТЬ ПЕЧАТЬ",
            command=self.add_stamp,
            bg="#2196F3",
            fg="white",
            font=("Arial", 12, "bold"),
            height=2,
            width=20
        )
        self.stamp_button.pack(pady=10)
        
        # Статус
        self.status_label = tk.Label(
            self.root,
            text="Выберите файлы для начала работы",
            font=("Arial", 9),
            fg="gray"
        )
        self.status_label.pack(pady=5)
    
    def select_document(self):
        filename = filedialog.askopenfilename(
            title="Выберите документ",
            filetypes=[
                ("Все поддерживаемые", "*.pdf *.png *.jpg *.jpeg *.bmp *.gif *.tiff"),
                ("PDF файлы", "*.pdf"),
                ("Изображения", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff"),
                ("Все файлы", "*.*")
            ]
        )
        if filename:
            self.document_path = filename
            
            # Определяем тип документа
            ext = os.path.splitext(filename)[1].lower()
            if ext == '.pdf':
                self.document_type = 'pdf'
                self.doc_type_label.config(
                    text="📄 PDF документ",
                    fg="blue"
                )
            elif ext in ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff']:
                self.document_type = 'image'
                self.doc_type_label.config(
                    text="🖼️ Изображение",
                    fg="green"
                )
            else:
                self.document_type = None
                self.doc_type_label.config(
                    text="❌ Неподдерживаемый формат",
                    fg="red"
                )
            
            self.doc_entry.delete(0, tk.END)
            self.doc_entry.insert(0, filename)
            self.update_status()
    
    def select_stamp(self):
        filename = filedialog.askopenfilename(
            title="Выберите изображение печати",
            filetypes=[
                ("Изображения", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("PNG с прозрачностью", "*.png"),
                ("Все файлы", "*.*")
            ]
        )
        if filename:
            self.stamp_path = filename
            self.stamp_entry.delete(0, tk.END)
            self.stamp_entry.insert(0, filename)
            self.update_status()
    
    def update_status(self):
        if not self.document_path:
            self.status_label.config(
                text="Выберите документ",
                fg="gray"
            )
        elif not self.stamp_path:
            self.status_label.config(
                text="Выберите изображение печати",
                fg="orange"
            )
        elif not self.document_type:
            self.status_label.config(
                text="❌ Неподдерживаемый формат документа",
                fg="red"
            )
        else:
            self.status_label.config(
                text="✅ Все файлы выбраны. Можно ставить печать!",
                fg="green"
            )
    
    def add_stamp(self):
        # Проверяем, что файлы выбраны
        if not self.document_path or not self.stamp_path:
            messagebox.showerror("Ошибка", "Сначала выберите документ и изображение печати!")
            return
        
        if not self.document_type:
            messagebox.showerror("Ошибка", "Неподдерживаемый формат документа!")
            return
        
        try:
            # Получаем параметры
            stamp_width_mm = float(self.size_var.get())
            margin_right_mm = float(self.margin_right_var.get())
            margin_bottom_mm = float(self.margin_bottom_var.get())
            
            # Запрашиваем имя для выходного файла
            self.output_path = filedialog.asksaveasfilename(
                title="Сохранить PDF как...",
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                initialfile="document_with_stamp.pdf"
            )
            
            if not self.output_path:
                return  # пользователь отменил сохранение
            
            # Обновляем статус
            self.status_label.config(text="⏳ Ставим печать...", fg="blue")
            self.root.update()
            
            # Обрабатываем в зависимости от типа документа
            if self.document_type == 'pdf':
                self.add_stamp_to_pdf(
                    self.document_path,
                    self.stamp_path,
                    self.output_path,
                    stamp_width_mm,
                    margin_right_mm,
                    margin_bottom_mm
                )
            else:  # image
                self.add_stamp_to_image(
                    self.document_path,
                    self.stamp_path,
                    self.output_path,
                    stamp_width_mm,
                    margin_right_mm,
                    margin_bottom_mm
                )
            
            self.status_label.config(
                text=f"✅ Готово! Файл сохранен: {os.path.basename(self.output_path)}",
                fg="green"
            )
            
            # Спрашиваем, открыть ли папку с файлом
            if messagebox.askyesno("Успех", f"Печать успешно поставлена!\n\nФайл сохранен:\n{self.output_path}\n\nОткрыть папку с файлом?"):
                self.open_folder(os.path.dirname(self.output_path))
            
        except Exception as e:
            self.status_label.config(text="❌ Ошибка при постановке печати", fg="red")
            messagebox.showerror("Ошибка", f"Произошла ошибка:\n{str(e)}")
    
    def add_stamp_to_pdf(self, input_pdf, stamp_image, output_pdf, stamp_width_mm, margin_right_mm, margin_bottom_mm):
        """Добавляет печать на PDF"""
        
        # Открываем PDF
        doc = fitz.open(input_pdf)
        
        # Открываем изображение печати
        stamp_pil = Image.open(stamp_image)
        
        # Конвертируем мм в points (1 мм = 2.83 points)
        stamp_width = stamp_width_mm * 2.83
        margin_right = margin_right_mm * 2.83
        margin_bottom = margin_bottom_mm * 2.83
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Получаем размер страницы в points
            rect = page.rect
            
            # Рассчитываем позицию (правый нижний угол с отступами)
            x = rect.width - stamp_width - margin_right
            y = rect.height - stamp_width - margin_bottom
            
            # Масштабируем печать
            stamp_resized = stamp_pil.resize(
                (int(stamp_width), int(stamp_width * stamp_pil.height / stamp_pil.width)),
                Image.Resampling.LANCZOS
            )
            
            # Конвертируем PIL в формат для fitz
            stamp_bytes = io.BytesIO()
            stamp_resized.save(stamp_bytes, format='PNG')
            stamp_bytes.seek(0)
            
            # Создаем pixmap из байтов
            stamp_pixmap = fitz.Pixmap(stamp_bytes.read())
            
            # Вставляем изображение
            page.insert_image(
                fitz.Rect(x, y, x + stamp_width, y + stamp_width),
                pixmap=stamp_pixmap
            )
        
        # Сохраняем результат
        doc.save(output_pdf)
        doc.close()
    
    def add_stamp_to_image(self, input_image, stamp_image, output_pdf, stamp_width_mm, margin_right_mm, margin_bottom_mm):
        """Добавляет печать на изображение и сохраняет как PDF"""
        
        # Открываем основное изображение
        main_image = Image.open(input_image)
        
        # Открываем печать
        stamp_pil = Image.open(stamp_image)
        
        # Конвертируем мм в пиксели (приблизительно, исходя из 300 DPI для печати)
        # Для A4: 300 DPI = 11.8 пикселей на мм
        pixels_per_mm = 11.8
        
        stamp_width_px = int(stamp_width_mm * pixels_per_mm)
        margin_right_px = int(margin_right_mm * pixels_per_mm)
        margin_bottom_px = int(margin_bottom_mm * pixels_per_mm)
        
        # Масштабируем печать
        stamp_resized = stamp_pil.resize(
            (stamp_width_px, int(stamp_width_px * stamp_pil.height / stamp_pil.width)),
            Image.Resampling.LANCZOS
        )
        
        # Рассчитываем позицию
        x = main_image.width - stamp_width_px - margin_right_px
        y = main_image.height - stamp_resized.height - margin_bottom_px
        
        # Создаем копию изображения
        result_image = main_image.copy()
        
        # Вставляем печать
        if stamp_resized.mode == 'RGBA':
            # Если печать с прозрачностью
            # Создаем белый фон, если основное изображение не имеет альфа-канала
            if result_image.mode != 'RGBA':
                result_image = result_image.convert('RGBA')
            result_image.paste(stamp_resized, (int(x), int(y)), stamp_resized)
        else:
            # Без прозрачности
            result_image.paste(stamp_resized, (int(x), int(y)))
        
        # Конвертируем в RGB для сохранения в PDF
        if result_image.mode == 'RGBA':
            result_image = result_image.convert('RGB')
        
        # Сохраняем как PDF
        result_image.save(output_pdf, "PDF", resolution=300.0)
    
    def open_folder(self, path):
        """Открывает папку в проводнике"""
        import subprocess
        import platform
        
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", path])
        else:  # Linux
            subprocess.run(["xdg-open", path])

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = StampApp(root)
    root.mainloop()