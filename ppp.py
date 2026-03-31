import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont, ImageTk
import io
import os
import platform
import sys
import json

# Импорт для предпросмотра
try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False
    print("⚠️ pdf2image не установлен. Установите: pip install pdf2image")

class StampApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Постановка печати на документ")
        
        # Устанавливаем окно на весь экран
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}")
        
        try:
            self.root.state('zoomed')
        except:
            pass
        
        # Переменные для хранения путей к файлам
        self.document_path = None
        self.stamp_path = None
        self.output_path = None
        self.document_type = None
        
        # Фиксированные параметры
        self.quality_dpi = 600
        self.stamp_opacity = 1.0
        
        # Избранные файлы
        self.favorite_stamps = []
        self.favorites_file = "favorite_stamps.json"
        self.load_favorites()
        
        # Настройки стилей
        self.title_font = ("Arial", 20, "bold")
        self.label_font = ("Arial", 14)
        self.entry_font = ("Arial", 12)
        self.button_font = ("Arial", 14, "bold")
        self.small_font = ("Arial", 11)
        self.padding = 15
        self.button_height = 2
        
        # Создаем интерфейс
        self.setup_main_layout()
        self.setup_ui()
    
    def setup_main_layout(self):
        """Создает основной макет с двумя панелями"""
        screen_width = self.root.winfo_screenwidth()
        
        # Создаем PanedWindow с разделителем, но отключаем возможность перемещения
        self.main_paned = tk.PanedWindow(
            self.root, 
            orient=tk.HORIZONTAL, 
            sashrelief=tk.RAISED, 
            sashwidth=8,
            sashcursor="arrow"  # Можно убрать
        )
        self.main_paned.pack(fill=tk.BOTH, expand=True)
        
        # Левая панель (настройки)
        self.left_frame_container = tk.Frame(self.main_paned)
        self.main_paned.add(self.left_frame_container, width=int(screen_width * 0.65), minsize=400)
        
        # Правая панель (предпросмотр)
        self.right_frame = tk.Frame(self.main_paned, bg='white')
        self.main_paned.add(self.right_frame, width=int(screen_width * 0.35), minsize=350)
        
        # Отключаем возможность перемещения разделителя
        self.main_paned.paneconfig(self.left_frame_container, stretch='never')
        self.main_paned.paneconfig(self.right_frame, stretch='never')
        
        # Остальной код без изменений...
        
        # Настройка левой панели с прокруткой
        self.left_canvas = tk.Canvas(self.left_frame_container, highlightthickness=0)
        self.left_scrollbar = tk.Scrollbar(self.left_frame_container, orient="vertical", command=self.left_canvas.yview)
        self.left_frame = tk.Frame(self.left_canvas)
        
        self.left_frame.bind(
            "<Configure>",
            lambda e: self.left_canvas.configure(scrollregion=self.left_canvas.bbox("all"))
        )
        
        self.left_canvas.create_window((0, 0), window=self.left_frame, anchor="nw")
        self.left_canvas.configure(yscrollcommand=self.left_scrollbar.set)
        
        self.left_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.left_scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        
        # Прокрутка колесиком
        def _on_mousewheel(event):
            self.left_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.left_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _configure_canvas(event):
            self.left_canvas.itemconfig(1, width=event.width)
        self.left_canvas.bind("<Configure>", _configure_canvas)
        
        # Правая панель - предпросмотр
        self.preview_frame = tk.Frame(self.right_frame, bg='white')
        self.preview_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        preview_title = tk.Label(
            self.preview_frame,
            text="ПРЕДПРОСМОТР РЕЗУЛЬТАТА",
            font=("Arial", 16, "bold"),
            bg='white',
            fg="#2196F3"
        )
        preview_title.pack(pady=(0, 10))
        
        # Канвас для предпросмотра
        self.preview_canvas = tk.Canvas(self.preview_frame, bg='white', highlightthickness=1)
        self.preview_canvas.pack(fill='both', expand=True)
        
        # Начальное сообщение
        self.preview_canvas.create_text(
            200, 150,
            text="Выберите PDF документ",
            fill="gray",
            font=("Arial", 14),
            tags="placeholder"
        )
        
        # Кнопка обновления
        self.update_preview_btn = tk.Button(
            self.preview_frame,
            text="🔄 ОБНОВИТЬ ПРЕДПРОСМОТР",
            command=self.update_preview,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold"),
            height=1,
            pady=5
        )
        self.update_preview_btn.pack(pady=10, fill='x')
        
        self.preview_info = tk.Label(
            self.preview_frame,
            text="Выберите документ и печать для предпросмотра",
            font=("Arial", 10),
            bg='white',
            fg="gray"
        )
        self.preview_info.pack(pady=5)
    
    def load_favorites(self):
        """Загружает избранные файлы"""
        try:
            if os.path.exists(self.favorites_file):
                with open(self.favorites_file, 'r', encoding='utf-8') as f:
                    self.favorite_stamps = json.load(f)
        except Exception as e:
            print(f"Ошибка загрузки: {e}")
            self.favorite_stamps = []
    
    def save_favorites(self):
        """Сохраняет избранные файлы"""
        try:
            with open(self.favorites_file, 'w', encoding='utf-8') as f:
                json.dump(self.favorite_stamps, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
    
    def add_to_favorites(self, file_path):
        if not file_path:
            return False
        
        for fav in self.favorite_stamps:
            if fav['path'] == file_path:
                messagebox.showinfo("Информация", "Этот файл уже в избранном!")
                return False
        
        if len(self.favorite_stamps) >= 5:
            messagebox.showwarning("Предупреждение", "Нельзя добавить более 5 файлов!")
            return False
        
        try:
            stamp_width_mm = float(self.size_var.get())
            margin_right_mm = float(self.margin_right_var.get())
            margin_bottom_mm = float(self.margin_bottom_var.get())
        except:
            stamp_width_mm = 40
            margin_right_mm = 50
            margin_bottom_mm = 50
        
        self.favorite_stamps.append({
            'path': file_path,
            'name': os.path.basename(file_path),
            'size': stamp_width_mm,
            'margin_right': margin_right_mm,
            'margin_bottom': margin_bottom_mm
        })
        self.save_favorites()
        self.update_favorites_display()
        messagebox.showinfo("Успех", "Файл добавлен в избранное!")
        return True
    
    def remove_from_favorites(self, index):
        if 0 <= index < len(self.favorite_stamps):
            self.favorite_stamps.pop(index)
            self.save_favorites()
            self.update_favorites_display()
            return True
        return False
    
    def select_favorite_stamp(self, index):
        if 0 <= index < len(self.favorite_stamps):
            fav = self.favorite_stamps[index]
            if os.path.exists(fav['path']):
                self.stamp_path = fav['path']
                self.stamp_entry.delete(0, tk.END)
                self.stamp_entry.insert(0, fav['path'])
                self.size_var.set(str(fav['size']))
                self.margin_right_var.set(str(fav['margin_right']))
                self.margin_bottom_var.set(str(fav['margin_bottom']))
                self.update_status()
                self.update_preview()
                messagebox.showinfo("Выбрано", f"Выбрана печать:\n{os.path.basename(fav['path'])}")
            else:
                self.remove_from_favorites(index)
                messagebox.showerror("Ошибка", "Файл не найден!")
    
    def update_favorites_display(self):
        if not hasattr(self, 'favorites_frame'):
            return
        
        for widget in self.favorites_frame.winfo_children():
            widget.destroy()
        
        if not self.favorite_stamps:
            empty_label = tk.Label(
                self.favorites_frame,
                text="Нет избранных файлов. Нажмите ★ чтобы добавить",
                font=self.small_font,
                fg="gray"
            )
            empty_label.pack(pady=10)
        else:
            for i, fav in enumerate(self.favorite_stamps):
                fav_item_frame = tk.Frame(self.favorites_frame)
                fav_item_frame.pack(fill='x', pady=5)
                
                file_name = fav['name']
                if len(file_name) > 40:
                    file_name = file_name[:37] + "..."
                
                settings_text = f"📏 {fav['size']} мм | → {fav['margin_right']} мм | ↓ {fav['margin_bottom']} мм"
                
                select_btn = tk.Button(
                    fav_item_frame,
                    text=f"📁 {file_name}\n   {settings_text}",
                    command=lambda idx=i: self.select_favorite_stamp(idx),
                    bg="#E0E0E0",
                    font=self.small_font,
                    anchor='w',
                    justify='left',
                    height=2
                )
                select_btn.pack(side='left', padx=(0, 10), fill='x', expand=True)
                
                remove_btn = tk.Button(
                    fav_item_frame,
                    text="✖",
                    command=lambda idx=i: self.remove_from_favorites(idx),
                    bg="#FF5722",
                    fg="white",
                    width=3
                )
                remove_btn.pack(side='left')
    
    def update_current_settings_to_favorite(self):
        if not self.stamp_path:
            messagebox.showwarning("Предупреждение", "Сначала выберите файл печати!")
            return
        
        for fav in self.favorite_stamps:
            if fav['path'] == self.stamp_path:
                try:
                    fav['size'] = float(self.size_var.get())
                    fav['margin_right'] = float(self.margin_right_var.get())
                    fav['margin_bottom'] = float(self.margin_bottom_var.get())
                    self.save_favorites()
                    self.update_favorites_display()
                    messagebox.showinfo("Успех", "Настройки обновлены!")
                    self.update_preview()
                    return
                except:
                    messagebox.showerror("Ошибка", "Неверные значения!")
                    return
        
        messagebox.showinfo("Информация", "Файл не найден в избранном.")
    
    def update_preview(self):
        """Обновляет предпросмотр документа с печатью"""
        if not self.document_path:
            self.preview_canvas.delete("all")
            self.preview_canvas.create_text(
                200, 150,
                text="Выберите PDF документ",
                fill="gray",
                font=("Arial", 14),
                tags="placeholder"
            )
            self.preview_info.config(text="Выберите документ", fg="orange")
            return
        
        if not PDF2IMAGE_AVAILABLE:
            self.preview_info.config(text="❌ pdf2image не установлен", fg="red")
            return
        
        try:
            self.preview_info.config(text="⏳ Загрузка предпросмотра...", fg="blue")
            self.root.update()
            
            self.preview_canvas.delete("all")
            
            preview_dpi = 72
            max_preview_width = 500
            
            images = convert_from_path(self.document_path, dpi=preview_dpi, first_page=1, last_page=1)
            
            if not images:
                self.preview_info.config(text="❌ Не удалось загрузить страницу", fg="red")
                return
            
            doc_img = images[0]
            
            if doc_img.width > max_preview_width:
                ratio = max_preview_width / doc_img.width
                new_size = (max_preview_width, int(doc_img.height * ratio))
                doc_img = doc_img.resize(new_size, Image.Resampling.LANCZOS)
            
            scale = doc_img.width / 827
            
            if self.stamp_path and os.path.exists(self.stamp_path):
                try:
                    stamp_width_mm = float(self.size_var.get())
                    margin_right_mm = float(self.margin_right_var.get())
                    margin_bottom_mm = float(self.margin_bottom_var.get())
                    
                    stamp_img = Image.open(self.stamp_path).convert('RGBA')
                    
                    # Сохраняем пропорции для предпросмотра
                    orig_width, orig_height = stamp_img.size
                    aspect_ratio = orig_height / orig_width
                    
                    stamp_width_px = int(stamp_width_mm * scale * 3.78)
                    stamp_height_px = int(stamp_width_px * aspect_ratio)
                    
                    if stamp_width_px > 0 and stamp_width_px < doc_img.width:
                        stamp_img = stamp_img.resize((stamp_width_px, stamp_height_px), Image.Resampling.LANCZOS)
                    
                    # Вычисляем позицию (правый нижний угол)
                    margin_right_px = int(margin_right_mm * scale * 3.78)
                    margin_bottom_px = int(margin_bottom_mm * scale * 3.78)
                    
                    stamp_x = doc_img.width - stamp_width_px - margin_right_px
                    stamp_y = doc_img.height - stamp_height_px - margin_bottom_px  # ← ИСПРАВЛЕНО
                    
                    # Накладываем печать
                    doc_img = doc_img.convert('RGBA')
                    stamp_x = max(0, stamp_x)
                    stamp_y = max(0, stamp_y)
                    
                    doc_img.paste(stamp_img, (stamp_x, stamp_y), stamp_img)
                    doc_img = doc_img.convert('RGB')
                    
                    self.preview_info.config(text="✅ Предпросмотр с печатью готов", fg="green")
                except Exception as e:
                    print(f"Ошибка при наложении печати: {e}")
                    self.preview_info.config(text="⚠️ Печать не добавлена", fg="orange")
            else:
                self.preview_info.config(text="📄 Документ загружен. Выберите печать", fg="green")
            
            preview_photo = ImageTk.PhotoImage(doc_img)
            self.preview_canvas.delete("all")
            
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()
            
            if canvas_width <= 1:
                canvas_width = max_preview_width
            if canvas_height <= 1:
                canvas_height = doc_img.height
            
            x = canvas_width // 2
            y = canvas_height // 2
            
            self.preview_canvas.create_image(x, y, image=preview_photo, anchor='center')
            self.preview_canvas.image = preview_photo
            
        except Exception as e:
            self.preview_info.config(text=f"❌ Ошибка: {str(e)[:80]}", fg="red")
            print(f"Ошибка предпросмотра: {e}")
            import traceback
            traceback.print_exc()
    
    def setup_ui(self):
        """Создает интерфейс настроек на левой панели"""
        main_container = tk.Frame(self.left_frame)
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Заголовок
        tk.Label(main_container, text="Постановка печати на документ", 
                font=self.title_font, fg="#2196F3").pack(pady=(0, 20))
        
        # 1. Документ
        doc_frame = tk.LabelFrame(main_container, text="1. Документ", 
                                  font=self.label_font, padx=self.padding, pady=self.padding)
        doc_frame.pack(pady=10, fill='x')
        
        doc_select = tk.Frame(doc_frame)
        doc_select.pack(fill='x', pady=5)
        
        self.doc_entry = tk.Entry(doc_select, font=self.entry_font)
        self.doc_entry.pack(side='left', padx=(0, 10), fill='x', expand=True)
        
        tk.Button(doc_select, text="Обзор...", command=self.select_document,
                 bg="#4CAF50", fg="white", font=self.button_font).pack(side='left')
        
        self.doc_type_label = tk.Label(doc_frame, text="", font=self.small_font, fg="blue")
        self.doc_type_label.pack(anchor='w', pady=(5, 0))
        
        # 2. Печать
        stamp_frame = tk.LabelFrame(main_container, text="2. Печать", 
                                    font=self.label_font, padx=self.padding, pady=self.padding)
        stamp_frame.pack(pady=10, fill='x')
        
        stamp_select = tk.Frame(stamp_frame)
        stamp_select.pack(fill='x', pady=5)
        
        self.stamp_entry = tk.Entry(stamp_select, font=self.entry_font)
        self.stamp_entry.pack(side='left', padx=(0, 10), fill='x', expand=True)
        
        tk.Button(stamp_select, text="Обзор...", command=self.select_stamp,
                 bg="#4CAF50", fg="white", font=self.button_font).pack(side='left')
        
        # Кнопки избранного
        fav_btns = tk.Frame(stamp_frame)
        fav_btns.pack(fill='x', pady=(10, 0))
        
        tk.Button(fav_btns, text="★ Добавить в избранное",
                 command=lambda: self.add_to_favorites(self.stamp_path) if self.stamp_path else None,
                 bg="#FFD700", font=self.button_font).pack(side='left', padx=(0, 10), fill='x', expand=True)
        
        tk.Button(fav_btns, text="🔄 Обновить настройки",
                 command=self.update_current_settings_to_favorite,
                 bg="#2196F3", fg="white", font=self.button_font).pack(side='left', fill='x', expand=True)
        
        # Избранное
        fav_main = tk.LabelFrame(main_container, text="★ Избранное (макс. 5)", 
                                 font=self.label_font, padx=self.padding, pady=self.padding)
        fav_main.pack(pady=10, fill='x')
        
        self.limit_label = tk.Label(fav_main, text=f"Использовано: {len(self.favorite_stamps)} из 5",
                                    font=self.small_font, fg="blue")
        self.limit_label.pack(anchor='w', pady=(0, 5))
        
        self.favorites_frame = tk.Frame(fav_main)
        self.favorites_frame.pack(fill='x')
        self.update_favorites_display()
        
        # 3. Параметры
        params_frame = tk.LabelFrame(main_container, text="3. Параметры печати", 
                                     font=self.label_font, padx=self.padding, pady=self.padding)
        params_frame.pack(pady=10, fill='x')
        
        # Размер
        size_row = tk.Frame(params_frame)
        size_row.pack(fill='x', pady=5)
        tk.Label(size_row, text="Размер печати (мм):", font=self.label_font, width=18, anchor='w').pack(side='left')
        self.size_var = tk.StringVar(value="40")
        size_entry = tk.Entry(size_row, textvariable=self.size_var, font=self.entry_font, width=10)
        size_entry.pack(side='left')
        size_entry.bind('<KeyRelease>', lambda e: self.update_preview())
        
        # Отступ справа
        right_row = tk.Frame(params_frame)
        right_row.pack(fill='x', pady=5)
        tk.Label(right_row, text="Отступ справа (мм):", font=self.label_font, width=18, anchor='w').pack(side='left')
        self.margin_right_var = tk.StringVar(value="50")
        right_entry = tk.Entry(right_row, textvariable=self.margin_right_var, font=self.entry_font, width=10)
        right_entry.pack(side='left')
        right_entry.bind('<KeyRelease>', lambda e: self.update_preview())
        
        # Отступ снизу
        bottom_row = tk.Frame(params_frame)
        bottom_row.pack(fill='x', pady=5)
        tk.Label(bottom_row, text="Отступ снизу (мм):", font=self.label_font, width=18, anchor='w').pack(side='left')
        self.margin_bottom_var = tk.StringVar(value="50")
        bottom_entry = tk.Entry(bottom_row, textvariable=self.margin_bottom_var, font=self.entry_font, width=10)
        bottom_entry.pack(side='left')
        bottom_entry.bind('<KeyRelease>', lambda e: self.update_preview())
        
        # Кнопка печати
        self.stamp_button = tk.Button(main_container, text="🖨️ ПОСТАВИТЬ ПЕЧАТЬ",
                                      command=self.add_stamp, bg="#2196F3", fg="white",
                                      font=self.button_font, height=2)
        self.stamp_button.pack(pady=20, fill='x')
        
        # Статус
        self.status_label = tk.Label(main_container, text="Выберите файлы",
                                     font=self.small_font, fg="gray")
        self.status_label.pack(pady=5)
    
    def select_document(self):
        filename = filedialog.askopenfilename(
            title="Выберите PDF документ",
            filetypes=[("PDF файлы", "*.pdf"), ("Все файлы", "*.*")]
        )
        if filename:
            self.document_path = filename
            self.doc_type_label.config(text="📄 PDF документ", fg="blue")
            self.doc_entry.delete(0, tk.END)
            self.doc_entry.insert(0, filename)
            self.update_status()
            self.update_preview()
    
    def select_stamp(self):
        filename = filedialog.askopenfilename(
            title="Выберите изображение печати",
            filetypes=[("Изображения", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if filename:
            self.stamp_path = filename
            self.stamp_entry.delete(0, tk.END)
            self.stamp_entry.insert(0, filename)
            self.update_status()
            self.update_preview()
    
    def update_status(self):
        if not self.document_path:
            self.status_label.config(text="Выберите PDF документ", fg="gray")
        elif not self.stamp_path:
            self.status_label.config(text="Выберите изображение печати", fg="orange")
        else:
            self.status_label.config(text="✅ Все файлы выбраны", fg="green")
        self.limit_label.config(text=f"Использовано: {len(self.favorite_stamps)} из 5")
    
    def apply_opacity(self, image, opacity):
        if opacity >= 1.0:
            return image
        if image.mode == 'RGBA':
            r, g, b, a = image.split()
            a = a.point(lambda p: p * opacity)
            return Image.merge('RGBA', (r, g, b, a))
        image = image.convert('RGBA')
        r, g, b, a = image.split()
        a = a.point(lambda p: p * opacity)
        return Image.merge('RGBA', (r, g, b, a))
    
    def add_stamp(self):
        if not self.document_path or not self.stamp_path:
            messagebox.showerror("Ошибка", "Выберите файлы!")
            return
        
        try:
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
            
            doc = fitz.open(self.document_path)
            stamp_pil = Image.open(self.stamp_path)
            
            # Конвертируем мм в points (1 мм = 2.83 points)
            stamp_width = stamp_width_mm * 2.83
            margin_right = margin_right_mm * 2.83
            margin_bottom = margin_bottom_mm * 2.83
            scale_factor = self.quality_dpi / 72
            
            # Сохраняем пропорции изображения
            original_width, original_height = stamp_pil.size
            aspect_ratio = original_height / original_width
            stamp_height = stamp_width * aspect_ratio  # ← вычисляем высоту
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                rect = page.rect
                
                # Позиция печати: правый нижний угол
                stamp_x = rect.width - stamp_width - margin_right
                stamp_y = rect.height - stamp_height - margin_bottom  # ← используем stamp_height
                
                # Масштабируем печать с сохранением пропорций
                stamp_resized = stamp_pil.resize(
                    (int(stamp_width * scale_factor), 
                    int(stamp_width * scale_factor * aspect_ratio)),
                    Image.Resampling.LANCZOS
                )
                
                stamp_bytes = io.BytesIO()
                stamp_resized.save(stamp_bytes, format='PNG')
                stamp_bytes.seek(0)
                
                # Вставляем печать с правильными размерами
                page.insert_image(
                    fitz.Rect(stamp_x, stamp_y, stamp_x + stamp_width, stamp_y + stamp_height),
                    pixmap=fitz.Pixmap(stamp_bytes.read())
                )
            
            doc.save(self.output_path, garbage=4, deflate=True)
            doc.close()
            
            self.status_label.config(text="✅ Готово!", fg="green")
            messagebox.showinfo("Успех", f"Файл сохранен:\n{self.output_path}")
            
        except Exception as e:
            self.status_label.config(text="❌ Ошибка", fg="red")
            messagebox.showerror("Ошибка", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = StampApp(root)
    root.mainloop()