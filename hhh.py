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
        self.root.geometry("550x420")  # Немного уменьшил высоту
        
        # Переменные для хранения путей к файлам
        self.document_path = None
        self.stamp_path = None
        self.output_path = None
        self.document_type = None  # 'pdf' или 'image'
        
        # Фиксированное качество 600 DPI
        self.quality_dpi = 600
        
        # Цвет текста (темно-синий #000080)
        self.text_color = (0, 0, 128, 255)  # RGBA: (R, G, B, Alpha)
        
        # === ФИКСИРОВАННЫЕ ПАРАМЕТРЫ ===
        self.text_zone_padding_mm = 3  # 5 мм отступ со всех сторон текста
        self.text_margin_mm = 0        # 2 мм отступ текста от печати (ФИКСИРОВАННЫЙ)
        
        # Определяем путь к шрифту
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        elif '__file__' in globals():
            application_path = os.path.dirname(os.path.abspath(__file__))
        else:
            application_path = os.path.dirname(os.path.abspath(sys.argv[0])) if sys.argv[0] else os.getcwd()
        
        self.font_path = os.path.join(application_path, "Kalissa.otf")
        print(f"🔤 Папка программы: {application_path}")
        print(f"🔤 Путь к шрифту: {self.font_path}")
        print(f"🔤 Шрифт существует: {os.path.exists(self.font_path)}")
        print(f"🎨 Цвет текста: #000080 (темно-синий)")
        print(f"📏 Зона текста: +{self.text_zone_padding_mm} мм со всех сторон")
        print(f"📏 Отступ текста от печати: {self.text_margin_mm} мм (фиксированный)")
        print(f"🎯 Текст центрирован относительно печати")
        
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
        
        # Текст для печати
        text_frame = tk.LabelFrame(self.root, text="3. Текст над печатью", padx=10, pady=10)
        text_frame.pack(pady=10, fill='x', padx=20)
        
        # Первая строка
        line1_frame = tk.Frame(text_frame)
        line1_frame.pack(fill='x', pady=2)
        
        tk.Label(line1_frame, text="Строка 1:", width=10, anchor='w').pack(side='left')
        self.text_line1 = tk.Entry(line1_frame, width=40)
        self.text_line1.pack(side='left', fill='x', expand=True)
        
        # Вторая строка
        line2_frame = tk.Frame(text_frame)
        line2_frame.pack(fill='x', pady=2)
        
        tk.Label(line2_frame, text="Строка 2:", width=10, anchor='w').pack(side='left')
        self.text_line2 = tk.Entry(line2_frame, width=40)
        self.text_line2.pack(side='left', fill='x', expand=True)
        
        # Размер текста
        text_size_frame = tk.Frame(text_frame)
        text_size_frame.pack(fill='x', pady=2)
        
        tk.Label(text_size_frame, text="Размер шрифта:", width=12, anchor='w').pack(side='left')
        self.text_size_var = tk.StringVar(value="14")
        text_size_spinbox = tk.Spinbox(text_size_frame, from_=8, to=72, textvariable=self.text_size_var, width=8)
        text_size_spinbox.pack(side='left')
        tk.Label(text_size_frame, text="pt", font=("Arial", 8), fg="gray").pack(side='left', padx=(2, 0))
        
        # Информация о шрифте, цвете и параметрах
        font_status = "✅ Шрифт найден" if os.path.exists(self.font_path) else "❌ Шрифт не найден"
        font_color = "green" if os.path.exists(self.font_path) else "red"
        
        info_frame = tk.Frame(text_frame)
        info_frame.pack(fill='x', pady=(5, 0))
        
        font_info = tk.Label(
            info_frame,
            text=f"🔤 Шрифт: Kalissa.otf ({font_status})",
            font=("Arial", 8),
            fg=font_color
        )
        font_info.pack(side='left')
        
        # Индикатор цвета
        color_indicator = tk.Label(
            info_frame,
            text="🎨 Цвет: #000080",
            font=("Arial", 8),
            fg="#000080"
        )
        color_indicator.pack(side='right')
        
        # Информация о параметрах
        params_frame = tk.Frame(text_frame)
        params_frame.pack(fill='x', pady=(2, 0))
        
        params_info = tk.Label(
            params_frame,
            text=f"📏 Зона текста: +{self.text_zone_padding_mm} мм | 📏 Отступ от печати: {self.text_margin_mm} мм | 🎯 Центрировано",
            font=("Arial", 8, "italic"),
            fg="#4CAF50"
        )
        params_info.pack(anchor='w')
        
        # Параметры печати
        options_frame = tk.LabelFrame(self.root, text="4. Параметры печати", padx=10, pady=10)
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
        
        # Кнопка для постановки печати
        self.stamp_button = tk.Button(
            self.root,
            text="🖨️ ПОСТАВИТЬ ПЕЧАТЬ И ТЕКСТ",
            command=self.add_stamp,
            bg="#2196F3",
            fg="white",
            font=("Arial", 12, "bold"),
            height=2,
            width=25
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
    
    def get_font(self, font_size_pt):
        """Загружает шрифт Kalissa.otf из папки с программой"""
        font_size_px = int(font_size_pt * self.quality_dpi / 72)
        
        if os.path.exists(self.font_path):
            try:
                font = ImageFont.truetype(self.font_path, font_size_px)
                print(f"✅ Загружен шрифт: Kalissa.otf (размер {font_size_pt}pt)")
                return font
            except Exception as e:
                print(f"❌ Ошибка загрузки Kalissa.otf: {e}")
        
        print("⚠️ Kalissa.otf не загружен, используем Arial")
        try:
            font = ImageFont.truetype("arial.ttf", font_size_px)
            return font
        except:
            return ImageFont.load_default()
    
    def create_text_image(self, text_line1, text_line2, font_size_pt, stamp_width_mm, dpi):
        """Создает изображение с текстом используя Kalissa шрифт и цвет #000080"""
        
        pixels_per_mm = dpi / 25.4
        padding_px = int(self.text_zone_padding_mm * pixels_per_mm)  # 5 мм в пикселях
        stamp_width_px = int(stamp_width_mm * pixels_per_mm)  # ширина печати в пикселях
        
        font = self.get_font(font_size_pt)
        
        # Создаем временное изображение для расчета размеров
        temp_img = Image.new('RGBA', (1, 1), (255, 255, 255, 0))
        temp_draw = ImageDraw.Draw(temp_img)
        
        try:
            # Получаем полные размеры с учетом всех выступов
            bbox1 = temp_draw.textbbox((0, 0), text_line1, font=font)
            bbox2 = temp_draw.textbbox((0, 0), text_line2, font=font)
            
            text1_width = bbox1[2] - bbox1[0]
            text2_width = bbox2[2] - bbox2[0]
            
            # Используем полную высоту с учетом выступов
            text1_height = bbox1[3] - bbox1[1]
            text2_height = bbox2[3] - bbox2[1]
            
        except Exception as e:
            print(f"Ошибка расчета bbox: {e}")
            # Запасные значения
            text1_width = len(text_line1) * font_size_pt * dpi / 72 * 0.6
            text2_width = len(text_line2) * font_size_pt * dpi / 72 * 0.6
            text1_height = font_size_pt * dpi / 72
            text2_height = font_size_pt * dpi / 72
        
        # Ширина текстового блока с учетом отступа 5 мм слева и справа
        text_block_width = max(text1_width, text2_width) + (padding_px * 2)
        
        # Отступ между строками
        line_spacing = int(font_size_pt * dpi / 72 * 0.3)
        
        # Общая высота с учетом отступа 5 мм сверху и снизу
        total_height = text1_height + text2_height + line_spacing + (padding_px * 2)
        
        # Создаем изображение для текста
        text_img = Image.new('RGBA', (text_block_width, total_height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(text_img)
        
        # Вычисляем центр текстового блока (две строки как единое целое)
        text_block_height = text1_height + text2_height + line_spacing
        text_block_center_y = text_block_height // 2
        
        # Координаты для первой строки (центрированы по горизонтали и вертикали внутри блока)
        x1 = (text_block_width - text1_width) // 2
        y1 = (total_height - text_block_height) // 2
        
        # Координаты для второй строки
        x2 = (text_block_width - text2_width) // 2
        y2 = y1 + text1_height + line_spacing
        
        # Рисуем текст темно-синим цветом #000080
        draw.text((x1, y1), text_line1, fill=self.text_color, font=font)
        draw.text((x2, y2), text_line2, fill=self.text_color, font=font)
        
        print(f"📝 Текст создан: размер {text_block_width}x{total_height}px")
        
        return text_img
    
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
            
            ext = os.path.splitext(filename)[1].lower()
            if ext == '.pdf':
                self.document_type = 'pdf'
                self.doc_type_label.config(text="📄 PDF документ", fg="blue")
            elif ext in ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff']:
                self.document_type = 'image'
                self.doc_type_label.config(text="🖼️ Изображение", fg="green")
            else:
                self.document_type = None
                self.doc_type_label.config(text="❌ Неподдерживаемый формат", fg="red")
            
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
            self.status_label.config(text="Выберите документ", fg="gray")
        elif not self.stamp_path:
            self.status_label.config(text="Выберите изображение печати", fg="orange")
        elif not self.document_type:
            self.status_label.config(text="❌ Неподдерживаемый формат документа", fg="red")
        else:
            self.status_label.config(text="✅ Все файлы выбраны. Можно ставить печать!", fg="green")
    
    def add_stamp(self):
        if not self.document_path or not self.stamp_path:
            messagebox.showerror("Ошибка", "Сначала выберите документ и изображение печати!")
            return
        
        if not self.document_type:
            messagebox.showerror("Ошибка", "Неподдерживаемый формат документа!")
            return
        
        try:
            stamp_width_mm = float(self.size_var.get())
            margin_right_mm = float(self.margin_right_var.get())
            margin_bottom_mm = float(self.margin_bottom_var.get())
            font_size_pt = float(self.text_size_var.get())
            
            text_line1 = self.text_line1.get().strip()
            text_line2 = self.text_line2.get().strip()
            
            if not text_line1 and not text_line2:
                messagebox.showerror("Ошибка", "Введите хотя бы одну строку текста!")
                return
            
            self.output_path = filedialog.asksaveasfilename(
                title="Сохранить PDF как...",
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                initialfile="document_with_stamp.pdf"
            )
            
            if not self.output_path:
                return
            
            self.status_label.config(text="⏳ Ставим печать и текст (600 DPI)...", fg="blue")
            self.root.update()
            
            if self.document_type == 'pdf':
                self.add_stamp_and_text_to_pdf(
                    self.document_path, self.stamp_path, self.output_path,
                    stamp_width_mm, margin_right_mm, margin_bottom_mm,
                    text_line1, text_line2, font_size_pt
                )
            else:
                self.add_stamp_and_text_to_image(
                    self.document_path, self.stamp_path, self.output_path,
                    stamp_width_mm, margin_right_mm, margin_bottom_mm,
                    text_line1, text_line2, font_size_pt
                )
            
            self.status_label.config(
                text=f"✅ Готово! Файл сохранен: {os.path.basename(self.output_path)}",
                fg="green"
            )
            
            if messagebox.askyesno("Успех", f"Печать и текст успешно добавлены!\n\nФайл сохранен:\n{self.output_path}\n\nОткрыть папку с файлом?"):
                self.open_folder(os.path.dirname(self.output_path))
            
        except Exception as e:
            self.status_label.config(text="❌ Ошибка при постановке печати", fg="red")
            messagebox.showerror("Ошибка", f"Произошла ошибка:\n{str(e)}")
    
    def add_stamp_and_text_to_pdf(self, input_pdf, stamp_image, output_pdf, 
                                  stamp_width_mm, margin_right_mm, margin_bottom_mm,
                                  text_line1, text_line2, font_size_pt):
        doc = fitz.open(input_pdf)
        stamp_pil = Image.open(stamp_image)
        
        text_img = self.create_text_image(text_line1, text_line2, font_size_pt, stamp_width_mm, self.quality_dpi)
        
        stamp_width = stamp_width_mm * 2.83
        margin_right = margin_right_mm * 2.83
        margin_bottom = margin_bottom_mm * 2.83
        text_margin = self.text_margin_mm * 2.83  # Фиксированный отступ 2 мм
        
        text_width_pts = (text_img.width * 72) / self.quality_dpi
        text_height_pts = (text_img.height * 72) / self.quality_dpi
        scale_factor = self.quality_dpi / 72
        
        # Увеличенный минимальный отступ от верхнего края
        min_top_margin = 15 * 2.83  # 15 мм в points
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            rect = page.rect
            
            # Базовая позиция печати
            stamp_x = rect.width - stamp_width - margin_right
            stamp_y = rect.height - stamp_width - margin_bottom
            
            # Базовая позиция текста (над печатью)
            # Текст центрирован относительно печати по горизонтали
            text_x = stamp_x + (stamp_width - text_width_pts) / 2
            text_y = stamp_y - text_height_pts - text_margin
            
            # Проверяем верхнюю границу с запасом
            if text_y < min_top_margin:
                overlap = min_top_margin - text_y
                stamp_y -= overlap
                text_y = stamp_y - text_height_pts - text_margin
                print(f"⚠️ Текст поднят на {overlap:.1f} points для сохранения отступа")
            
            # Проверяем боковые границы
            if text_x < 5 * 2.83:
                text_x = 5 * 2.83
                print("⚠️ Текст сдвинут от левого края")
            
            if text_x + text_width_pts > rect.width - 5 * 2.83:
                text_x = rect.width - text_width_pts - 5 * 2.83
                print("⚠️ Текст сдвинут от правого края")
            
            # Масштабируем печать
            stamp_resized = stamp_pil.resize(
                (int(stamp_width * scale_factor), 
                 int(stamp_width * stamp_pil.height / stamp_pil.width * scale_factor)),
                Image.Resampling.LANCZOS
            )
            
            stamp_bytes = io.BytesIO()
            stamp_resized.save(stamp_bytes, format='PNG')
            stamp_bytes.seek(0)
            page.insert_image(
                fitz.Rect(stamp_x, stamp_y, stamp_x + stamp_width, stamp_y + stamp_width),
                pixmap=fitz.Pixmap(stamp_bytes.read())
            )
            
            text_bytes = io.BytesIO()
            text_img.save(text_bytes, format='PNG')
            text_bytes.seek(0)
            page.insert_image(
                fitz.Rect(text_x, text_y, text_x + text_width_pts, text_y + text_height_pts),
                pixmap=fitz.Pixmap(text_bytes.read())
            )
            
            print(f"📄 Страница {page_num + 1}: отступ текста от печати = {self.text_margin_mm} мм")
        
        doc.save(output_pdf, garbage=4, deflate=True)
        doc.close()
    
    def add_stamp_and_text_to_image(self, input_image, stamp_image, output_pdf,
                                    stamp_width_mm, margin_right_mm, margin_bottom_mm,
                                    text_line1, text_line2, font_size_pt):
        main_image = Image.open(input_image)
        stamp_pil = Image.open(stamp_image)
        
        text_img = self.create_text_image(text_line1, text_line2, font_size_pt, stamp_width_mm, self.quality_dpi)
        
        pixels_per_mm = self.quality_dpi / 25.4
        stamp_width_px = int(stamp_width_mm * pixels_per_mm)
        margin_right_px = int(margin_right_mm * pixels_per_mm)
        margin_bottom_px = int(margin_bottom_mm * pixels_per_mm)
        text_margin_px = int(self.text_margin_mm * pixels_per_mm)  # Фиксированный отступ 2 мм
        
        stamp_resized = stamp_pil.resize(
            (stamp_width_px, int(stamp_width_px * stamp_pil.height / stamp_pil.width)),
            Image.Resampling.LANCZOS
        )
        
        target_width = int(210 * pixels_per_mm)
        if main_image.width < target_width * 0.8:
            ratio = target_width / main_image.width
            main_image = main_image.resize((target_width, int(main_image.height * ratio)), Image.Resampling.LANCZOS)
        
        # Базовая позиция печати
        stamp_x = main_image.width - stamp_width_px - margin_right_px
        stamp_y = main_image.height - stamp_resized.height - margin_bottom_px
        
        # Базовая позиция текста (центрирован относительно печати)
        text_x = stamp_x + (stamp_width_px - text_img.width) / 2
        text_y = stamp_y - text_img.height - text_margin_px
        
        # Проверяем границы для изображения
        min_top_margin_px = int(15 * pixels_per_mm)
        
        if text_y < min_top_margin_px:
            overlap = min_top_margin_px - text_y
            stamp_y -= overlap
            text_y = stamp_y - text_img.height - text_margin_px
            print(f"⚠️ Текст поднят в изображении")
        
        if text_x < int(5 * pixels_per_mm):
            text_x = int(5 * pixels_per_mm)
            print("⚠️ Текст сдвинут от левого края изображения")
        
        if text_x + text_img.width > main_image.width - int(5 * pixels_per_mm):
            text_x = main_image.width - text_img.width - int(5 * pixels_per_mm)
            print("⚠️ Текст сдвинут от правого края изображения")
        
        result_image = main_image.copy()
        if result_image.mode != 'RGBA':
            result_image = result_image.convert('RGBA')
        
        result_image.paste(text_img, (int(text_x), int(text_y)), text_img)
        result_image.paste(stamp_resized, (int(stamp_x), int(stamp_y)), stamp_resized)
        
        if result_image.mode == 'RGBA':
            result_image = result_image.convert('RGB')
        
        result_image.save(output_pdf, "PDF", resolution=self.quality_dpi)
    
    def open_folder(self, path):
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            import subprocess
            subprocess.run(["open", path])
        else:
            import subprocess
            subprocess.run(["xdg-open", path])

if __name__ == "__main__":
    root = tk.Tk()
    app = StampApp(root)
    root.mainloop()