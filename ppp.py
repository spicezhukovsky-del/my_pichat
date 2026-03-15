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
        self.root.geometry("600x800")
        
        # Переменные для хранения путей к файлам
        self.document_path = None
        self.stamp_path = None
        self.signature_path = None
        self.output_path = None
        self.document_type = None
        
        # Фиксированное качество 600 DPI
        self.quality_dpi = 600
        
        # Цвет текста (темно-синий #000080)
        self.text_color = (0, 0, 128, 255)
        
        # === НАСТРОЙКИ С МИНИМАЛЬНЫМИ ОТСТУПАМИ ===
        self.text_zone_padding_mm = 0.5        # 0.5 мм отступ со всех сторон текста
        self.text_margin_mm = 0                 # 0 мм отступ текста от печати
        self.stamp_opacity = 0.6                # 60% прозрачность печати
        self.signature_height_mm = 8            # Высота изображения подписи в мм
        self.signature_text_spacing_mm = 1      # 1 мм между подписью и текстом
        
        # Определяем путь к шрифту
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        elif '__file__' in globals():
            application_path = os.path.dirname(os.path.abspath(__file__))
        else:
            application_path = os.path.dirname(os.path.abspath(sys.argv[0])) if sys.argv[0] else os.getcwd()
        
        self.font_path = os.path.join(application_path, "Gogol.ttf")
        print(f"🔤 Папка программы: {application_path}")
        print(f"🔤 Путь к шрифту: {self.font_path}")
        print(f"🔤 Шрифт существует: {os.path.exists(self.font_path)}")
        
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
        text_frame = tk.LabelFrame(self.root, text="3. Текст и подпись над печатью", padx=10, pady=10)
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
        
        # Третья строка (подпись + текст)
        line3_frame = tk.LabelFrame(text_frame, text="Строка 3: Подпись + текст", padx=5, pady=5)
        line3_frame.pack(fill='x', pady=5)
        
        sig_select_frame = tk.Frame(line3_frame)
        sig_select_frame.pack(fill='x', pady=2)
        
        tk.Label(sig_select_frame, text="Подпись:", width=10, anchor='w').pack(side='left')
        self.signature_entry = tk.Entry(sig_select_frame, width=30)
        self.signature_entry.pack(side='left', padx=(0, 5), fill='x', expand=True)
        
        tk.Button(
            sig_select_frame, 
            text="Обзор...", 
            command=self.select_signature,
            bg="#FF9800",
            fg="white",
            font=("Arial", 8)
        ).pack(side='left')
        
        sig_text_frame = tk.Frame(line3_frame)
        sig_text_frame.pack(fill='x', pady=2)
        
        tk.Label(sig_text_frame, text="Текст:", width=10, anchor='w').pack(side='left')
        self.signature_text = tk.Entry(sig_text_frame, width=40)
        self.signature_text.pack(side='left', fill='x', expand=True)
        
        # Размер текста
        text_size_frame = tk.Frame(text_frame)
        text_size_frame.pack(fill='x', pady=2)
        
        tk.Label(text_size_frame, text="Размер шрифта:", width=12, anchor='w').pack(side='left')
        self.text_size_var = tk.StringVar(value="14")
        text_size_spinbox = tk.Spinbox(text_size_frame, from_=8, to=72, textvariable=self.text_size_var, width=8)
        text_size_spinbox.pack(side='left')
        tk.Label(text_size_frame, text="pt", font=("Arial", 8), fg="gray").pack(side='left', padx=(2, 0))
        
        # Параметры печати
        options_frame = tk.LabelFrame(self.root, text="4. Параметры печати", padx=10, pady=10)
        options_frame.pack(pady=10, fill='x', padx=20)
        
        size_frame = tk.Frame(options_frame)
        size_frame.pack(fill='x', pady=2)
        
        tk.Label(size_frame, text="Размер печати (мм):", width=15, anchor='w').pack(side='left')
        self.size_var = tk.StringVar(value="40")
        tk.Entry(size_frame, textvariable=self.size_var, width=10).pack(side='left')
        
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
            filetypes=[("Изображения", "*.png *.jpg *.jpeg *.gif *.bmp"), ("PNG", "*.png")]
        )
        if filename:
            self.stamp_path = filename
            self.stamp_entry.delete(0, tk.END)
            self.stamp_entry.insert(0, filename)
            self.update_status()
    
    def select_signature(self):
        filename = filedialog.askopenfilename(
            title="Выберите изображение подписи",
            filetypes=[("Изображения", "*.png *.jpg *.jpeg *.gif *.bmp"), ("PNG", "*.png")]
        )
        if filename:
            self.signature_path = filename
            self.signature_entry.delete(0, tk.END)
            self.signature_entry.insert(0, filename)
            self.update_status()
    
    def update_status(self):
        if not self.document_path:
            self.status_label.config(text="Выберите документ", fg="gray")
        elif not self.stamp_path:
            self.status_label.config(text="Выберите изображение печати", fg="orange")
        elif not self.document_type:
            self.status_label.config(text="❌ Неподдерживаемый формат документа", fg="red")
        else:
            self.status_label.config(text="✅ Все файлы выбраны", fg="green")
    
    def get_font(self, font_size_pt):
        font_size_px = int(font_size_pt * self.quality_dpi / 72)
        if os.path.exists(self.font_path):
            try:
                return ImageFont.truetype(self.font_path, font_size_px)
            except:
                pass
        try:
            return ImageFont.truetype("arial.ttf", font_size_px)
        except:
            return ImageFont.load_default()
    
    def apply_opacity(self, image, opacity):
        if image.mode == 'RGBA':
            r, g, b, a = image.split()
            a = a.point(lambda p: p * opacity)
            return Image.merge('RGBA', (r, g, b, a))
        else:
            image = image.convert('RGBA')
            r, g, b, a = image.split()
            a = a.point(lambda p: p * opacity)
            return Image.merge('RGBA', (r, g, b, a))
    
    def create_signature_line(self, signature_image_path, signature_text, font_size_pt, dpi):
        pixels_per_mm = dpi / 25.4
        spacing_px = int(self.signature_text_spacing_mm * pixels_per_mm)
        font = self.get_font(font_size_pt)
        
        if signature_image_path and os.path.exists(signature_image_path):
            signature_img = Image.open(signature_image_path)
            target_height_px = int(self.signature_height_mm * pixels_per_mm)
            ratio = target_height_px / signature_img.height
            target_width_px = int(signature_img.width * ratio)
            signature_img = signature_img.resize((target_width_px, target_height_px), Image.Resampling.LANCZOS)
        else:
            signature_img = Image.new('RGBA', (1, 1), (255, 255, 255, 0))
        
        temp_img = Image.new('RGBA', (1, 1), (255, 255, 255, 0))
        temp_draw = ImageDraw.Draw(temp_img)
        
        try:
            bbox = temp_draw.textbbox((0, 0), signature_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            text_y_offset = bbox[1]
        except:
            text_width = len(signature_text) * font_size_pt * dpi / 72 * 0.6
            text_height = font_size_pt * dpi / 72
            text_y_offset = 0
        
        line_height = max(signature_img.height, text_height)
        line_width = signature_img.width + spacing_px + text_width
        
        line_img = Image.new('RGBA', (line_width, line_height), (255, 255, 255, 0))
        
        sig_y = (line_height - signature_img.height) // 2
        line_img.paste(signature_img, (0, sig_y), signature_img if signature_img.mode == 'RGBA' else None)
        
        draw = ImageDraw.Draw(line_img)
        text_x = signature_img.width + spacing_px
        text_y = (line_height - text_height) // 2 - text_y_offset
        draw.text((text_x, text_y), signature_text, fill=self.text_color, font=font)
        
        return line_img
    
    def create_text_image(self, text_line1, text_line2, signature_path, signature_text, font_size_pt, stamp_width_mm, dpi):
        pixels_per_mm = dpi / 25.4
        padding_px = int(self.text_zone_padding_mm * pixels_per_mm)
        font = self.get_font(font_size_pt)
        
        signature_line = self.create_signature_line(signature_path, signature_text, font_size_pt, dpi)
        
        temp_img = Image.new('RGBA', (1, 1), (255, 255, 255, 0))
        temp_draw = ImageDraw.Draw(temp_img)
        
        text_lines = []
        text_widths = []
        text_heights = []
        text_bboxes = []
        
        if text_line1.strip():
            text_lines.append(text_line1)
            try:
                bbox = temp_draw.textbbox((0, 0), text_line1, font=font)
                text_widths.append(bbox[2] - bbox[0])
                text_heights.append(bbox[3] - bbox[1])
                text_bboxes.append(bbox)
            except:
                text_widths.append(len(text_line1) * font_size_pt * dpi / 72 * 0.6)
                text_heights.append(font_size_pt * dpi / 72)
                text_bboxes.append(None)
        
        if text_line2.strip():
            text_lines.append(text_line2)
            try:
                bbox = temp_draw.textbbox((0, 0), text_line2, font=font)
                text_widths.append(bbox[2] - bbox[0])
                text_heights.append(bbox[3] - bbox[1])
                text_bboxes.append(bbox)
            except:
                text_widths.append(len(text_line2) * font_size_pt * dpi / 72 * 0.6)
                text_heights.append(font_size_pt * dpi / 72)
                text_bboxes.append(None)
        
        max_width = max(max(text_widths) if text_widths else 0, signature_line.width)
        block_width = max_width + (padding_px * 2)
        
        line_spacing = int(font_size_pt * dpi / 72 * 0.1)  # 10% отступ между строками
        
        # Убираем extra_bottom_padding
        total_height = padding_px  # только отступ сверху
        
        for i, height in enumerate(text_heights):
            total_height += height
            if i < len(text_heights) - 1:
                total_height += line_spacing
        
        if text_lines:
            total_height += line_spacing
        
        total_height += signature_line.height
        total_height += padding_px  # отступ снизу
        
        result_img = Image.new('RGBA', (block_width, total_height), (255, 255, 255, 0))
        
        y = padding_px
        draw = ImageDraw.Draw(result_img)
        
        for i, line in enumerate(text_lines):
            x = (block_width - text_widths[i]) // 2
            if text_bboxes[i] is not None:
                bbox = text_bboxes[i]
                draw.text((x, y - bbox[1]), line, fill=self.text_color, font=font)
            else:
                draw.text((x, y), line, fill=self.text_color, font=font)
            y += text_heights[i] + line_spacing
        
        if text_lines:
            y += line_spacing
        
        sig_x = (block_width - signature_line.width) // 2
        result_img.paste(signature_line, (sig_x, y), signature_line)
        
        return result_img
    
    def add_stamp(self):
        if not self.document_path or not self.stamp_path:
            messagebox.showerror("Ошибка", "Выберите файлы!")
            return
        
        try:
            stamp_width_mm = float(self.size_var.get())
            margin_right_mm = float(self.margin_right_var.get())
            margin_bottom_mm = float(self.margin_bottom_var.get())
            font_size_pt = float(self.text_size_var.get())
            
            text_line1 = self.text_line1.get().strip()
            text_line2 = self.text_line2.get().strip()
            signature_text = self.signature_text.get().strip()
            signature_path = self.signature_entry.get().strip()
            
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
            
            text_img = self.create_text_image(
                text_line1, text_line2, signature_path, signature_text, 
                font_size_pt, stamp_width_mm, self.quality_dpi
            )
            
            if self.document_type == 'pdf':
                self.add_stamp_and_text_to_pdf(
                    self.document_path, self.stamp_path, self.output_path,
                    stamp_width_mm, margin_right_mm, margin_bottom_mm,
                    text_img
                )
            else:
                self.add_stamp_and_text_to_image(
                    self.document_path, self.stamp_path, self.output_path,
                    stamp_width_mm, margin_right_mm, margin_bottom_mm,
                    text_img
                )
            
            self.status_label.config(text="✅ Готово!", fg="green")
            
        except Exception as e:
            self.status_label.config(text="❌ Ошибка", fg="red")
            messagebox.showerror("Ошибка", str(e))
    
    def add_stamp_and_text_to_pdf(self, input_pdf, stamp_image, output_pdf, 
                                  stamp_width_mm, margin_right_mm, margin_bottom_mm,
                                  text_img):
        doc = fitz.open(input_pdf)
        stamp_pil = Image.open(stamp_image)
        stamp_pil = self.apply_opacity(stamp_pil, self.stamp_opacity)
        
        stamp_width = stamp_width_mm * 2.83
        margin_right = margin_right_mm * 2.83
        margin_bottom = margin_bottom_mm * 2.83
        text_margin = self.text_margin_mm * 2.83
        
        text_width_pts = (text_img.width * 72) / self.quality_dpi
        text_height_pts = (text_img.height * 72) / self.quality_dpi
        scale_factor = self.quality_dpi / 72
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            rect = page.rect
            
            stamp_x = rect.width - stamp_width - margin_right
            stamp_y = rect.height - stamp_width - margin_bottom
            
            # Текст прямо над печатью (вплотную)
            text_x = stamp_x + (stamp_width - text_width_pts) / 2
            text_y = stamp_y - text_height_pts - text_margin - 1  # -1 для надежности
            
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
        
        doc.save(output_pdf, garbage=4, deflate=True)
        doc.close()
    
    def add_stamp_and_text_to_image(self, input_image, stamp_image, output_pdf,
                                    stamp_width_mm, margin_right_mm, margin_bottom_mm,
                                    text_img):
        main_image = Image.open(input_image)
        stamp_pil = Image.open(stamp_image)
        stamp_pil = self.apply_opacity(stamp_pil, self.stamp_opacity)
        
        pixels_per_mm = self.quality_dpi / 25.4
        stamp_width_px = int(stamp_width_mm * pixels_per_mm)
        margin_right_px = int(margin_right_mm * pixels_per_mm)
        margin_bottom_px = int(margin_bottom_mm * pixels_per_mm)
        text_margin_px = int(self.text_margin_mm * pixels_per_mm)
        
        stamp_resized = stamp_pil.resize(
            (stamp_width_px, int(stamp_width_px * stamp_pil.height / stamp_pil.width)),
            Image.Resampling.LANCZOS
        )
        
        stamp_x = main_image.width - stamp_width_px - margin_right_px
        stamp_y = main_image.height - stamp_resized.height - margin_bottom_px
        
        text_x = stamp_x + (stamp_width_px - text_img.width) / 2
        text_y = stamp_y - text_img.height - text_margin_px - 1  # -1 для надежности
        
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