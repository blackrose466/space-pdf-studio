import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import os
import sys
import threading
from datetime import datetime
import random

class SpacePDFStudio:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 SPACE PDF STUDIO")
        self.root.geometry("1200x750")
        #self.root.configure(bg='#0a0a1a')
        
        # Set window icon (optional)
        try:
            icon_path = os.path.join(os.path.expanduser("~"), "Downloads", "pdf_icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass
        
        # Find Ghostscript and LibreOffice
        self.gs_path = self.find_ghostscript()
        self.libreoffice_path = self.find_libreoffice()
        
        # Default output to Downloads
        self.default_output = os.path.join(os.path.expanduser("~"), "Downloads")
        
        # Color scheme
        self.colors = {
            'accent': '#00d4ff',
            'accent2': '#9b4dff',
            'text': '#ffffff',
            'text_dim': '#b0b0ff',
            'bg_dark': '#0a0a1a',
            'bg_medium': '#0f0f25',
            'bg_light': '#151530'
        }
        
        self.setup_ui()
        self.update_status()
    
    def find_ghostscript(self):
        """Auto-detect Ghostscript"""
        possible_paths = [
            r"C:\Program Files\gs\gs10.07.0\bin\gswin64c.exe",
            r"C:\Program Files\gs\gs10.04.0\bin\gswin64c.exe",
            r"C:\Program Files\gs\gs10.03.0\bin\gswin64c.exe",
            r"C:\Program Files (x86)\gs\gs10.07.0\bin\gswin32c.exe",
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        try:
            import shutil
            return shutil.which('gswin64c') or shutil.which('gswin32c')
        except:
            return None
    
    def find_libreoffice(self):
        """Auto-detect LibreOffice"""
        possible_paths = [
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        try:
            import shutil
            return shutil.which('soffice')
        except:
            return None
    
    def setup_ui(self):
        """Setup the user interface"""
        
        # Header
        header = tk.Frame(self.root, bg=self.colors['bg_dark'], height=80)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        title = tk.Label(header, text="🚀 SPACE PDF STUDIO", 
                        font=('Helvetica', 28, 'bold'),
                        fg=self.colors['accent'], bg=self.colors['bg_dark'])
        title.pack(pady=15)
        
        # Notebook (tabs)
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background=self.colors['bg_medium'], borderwidth=0)
        style.configure('TNotebook.Tab', background=self.colors['bg_dark'], 
                       foreground=self.colors['accent'], padding=[15, 5],
                       font=('Helvetica', 10))
        style.map('TNotebook.Tab', background=[('selected', self.colors['accent2'])],
                 foreground=[('selected', 'white')])
        
        self.notebook = ttk.Notebook(self.root, style='TNotebook')
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_compress_tab()
        self.create_convert_tab()
        self.create_images_tab()
        self.create_merge_tab()
        self.create_extract_tab()
        self.create_security_tab()
        self.create_ocr_tab()
        self.create_metadata_tab()
        self.create_batch_tab()
        
        # Status bar
        status = tk.Frame(self.root, bg=self.colors['bg_dark'], height=30)
        status.pack(fill='x', side='bottom')
        status.pack_propagate(False)
        
        self.status_label = tk.Label(status, text="🟢 SYSTEM READY", 
                                     font=('Consolas', 9),
                                     fg=self.colors['accent'], bg=self.colors['bg_dark'])
        self.status_label.pack(side='left', padx=10)
        
        self.progress = ttk.Progressbar(status, mode='indeterminate', length=200)
        self.progress.pack(side='right', padx=10)
    
    def create_scrollable_frame(self, parent):
        """Create a scrollable frame for tabs"""
        canvas = tk.Canvas(parent, bg=self.colors['bg_medium'], highlightthickness=0)
        scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg_medium'])
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        return scrollable_frame
    
    def create_file_entry(self, parent, label_text, file_types):
        """Create a file selection row"""
        frame = tk.Frame(parent, bg=self.colors['bg_medium'])
        frame.pack(fill='x', padx=20, pady=5)
        
        label = tk.Label(frame, text=label_text, width=15, anchor='w',
                        fg=self.colors['text'], bg=self.colors['bg_medium'])
        label.pack(side='left')
        
        entry = tk.Entry(frame, bg=self.colors['bg_dark'], fg=self.colors['text'],
                        font=('Consolas', 10), relief='flat', bd=1)
        entry.pack(side='left', fill='x', expand=True, padx=(5, 5))
        
        btn = tk.Button(frame, text="Browse", command=lambda: self.browse_file(entry, file_types),
                       bg=self.colors['bg_light'], fg=self.colors['accent'],
                       cursor='hand2', bd=0, padx=10)
        btn.pack(side='right')
        
        return entry
    
    def create_output_entry(self, parent, label_text, default_name):
        """Create output file selection row"""
        frame = tk.Frame(parent, bg=self.colors['bg_medium'])
        frame.pack(fill='x', padx=20, pady=5)
        
        label = tk.Label(frame, text=label_text, width=15, anchor='w',
                        fg=self.colors['text'], bg=self.colors['bg_medium'])
        label.pack(side='left')
        
        entry = tk.Entry(frame, bg=self.colors['bg_dark'], fg=self.colors['text'],
                        font=('Consolas', 10), relief='flat', bd=1)
        entry.pack(side='left', fill='x', expand=True, padx=(5, 5))
        entry.insert(0, os.path.join(self.default_output, default_name))
        
        btn = tk.Button(frame, text="Save As", command=lambda: self.browse_save(entry),
                       bg=self.colors['bg_light'], fg=self.colors['accent'],
                       cursor='hand2', bd=0, padx=10)
        btn.pack(side='right')
        
        return entry
    
    def create_log_area(self, parent):
        """Create log text area"""
        frame = tk.Frame(parent, bg=self.colors['bg_dark'])
        frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        log = tk.Text(frame, bg='#050510', fg=self.colors['text_dim'],
                     font=('Consolas', 9), relief='flat', wrap='word')
        log.pack(fill='both', expand=True, side='left')
        
        scroll = tk.Scrollbar(frame, command=log.yview)
        scroll.pack(side='right', fill='y')
        log.config(yscrollcommand=scroll.set)
        
        return log
    
    def browse_file(self, entry, file_types):
        filename = filedialog.askopenfilename(filetypes=file_types)
        if filename:
            entry.delete(0, tk.END)
            entry.insert(0, filename)
    
    def browse_save(self, entry):
        filename = filedialog.asksaveasfilename(defaultextension=".pdf",
                                                filetypes=[("PDF files", "*.pdf")])
        if filename:
            entry.delete(0, tk.END)
            entry.insert(0, filename)
    
    def log_message(self, log_widget, message, is_error=False):
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = "✅" if not is_error else "❌"
        log_widget.insert(tk.END, f"[{timestamp}] {prefix} {message}\n")
        log_widget.see(tk.END)
        self.root.update()
    
    def start_progress(self):
        self.progress.start(10)
    
    def stop_progress(self):
        self.progress.stop()
    
    def update_status(self):
        gs_status = "🟢" if self.gs_path else "🔴"
        lo_status = "🟢" if self.libreoffice_path else "🔴"
        self.status_label.config(text=f"Ghostscript: {gs_status} | LibreOffice: {lo_status}")
        self.root.after(30000, self.update_status)
    
    # ============= COMPRESS TAB =============
    def create_compress_tab(self):
        tab = tk.Frame(self.notebook, bg=self.colors['bg_medium'])
        self.notebook.add(tab, text="📦 COMPRESS")
        
        scrollable = self.create_scrollable_frame(tab)
        
        tk.Label(scrollable, text="PDF Compression Tool", font=('Helvetica', 14, 'bold'),
                fg=self.colors['accent'], bg=self.colors['bg_medium']).pack(pady=10)
        
        self.compress_input = self.create_file_entry(scrollable, "Input PDF:", [("PDF", "*.pdf")])
        self.compress_output = self.create_output_entry(scrollable, "Output PDF:", "compressed.pdf")
        
        tk.Label(scrollable, text="Compression Level:", fg=self.colors['text'], 
                bg=self.colors['bg_medium']).pack(anchor='w', padx=20, pady=(10,0))
        
        self.compress_level = ttk.Combobox(scrollable, values=[
            'Screen (Smallest)', 'Ebook (Recommended)', 'Printer (Quality)', 'Prepress (Maximum)'
        ], width=30)
        self.compress_level.pack(anchor='w', padx=20, pady=5)
        self.compress_level.current(1)
        
        btn = tk.Button(scrollable, text="🚀 COMPRESS PDF", command=self.compress_pdf,
                       bg=self.colors['accent2'], fg='white', font=('Helvetica', 11, 'bold'),
                       padx=20, pady=8, cursor='hand2', bd=0)
        btn.pack(pady=20)
        
        self.compress_log = self.create_log_area(scrollable)
    
    def compress_pdf(self):
        if not self.gs_path:
            messagebox.showerror("Error", "Ghostscript not found!")
            return
        
        input_file = self.compress_input.get()
        output_file = self.compress_output.get()
        
        if not input_file or not output_file:
            messagebox.showerror("Error", "Select input and output files!")
            return
        
        level_map = {
            'Screen (Smallest)': '/screen',
            'Ebook (Recommended)': '/ebook',
            'Printer (Quality)': '/printer',
            'Prepress (Maximum)': '/prepress'
        }
        setting = level_map.get(self.compress_level.get(), '/ebook')
        
        def run():
            self.start_progress()
            self.log_message(self.compress_log, f"Compressing: {os.path.basename(input_file)}")
            
            cmd = [self.gs_path, '-sDEVICE=pdfwrite', f'-dPDFSETTINGS={setting}',
                   '-dNOPAUSE', '-dQUIET', '-dBATCH', f'-sOutputFile={output_file}', input_file]
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    in_size = os.path.getsize(input_file) / (1024*1024)
                    out_size = os.path.getsize(output_file) / (1024*1024)
                    saved = ((in_size - out_size) / in_size) * 100 if in_size > 0 else 0
                    self.log_message(self.compress_log, f"Done! {in_size:.2f}MB → {out_size:.2f}MB ({saved:.1f}% saved)")
                else:
                    self.log_message(self.compress_log, f"Error: {result.stderr}", True)
            except Exception as e:
                self.log_message(self.compress_log, f"Error: {str(e)}", True)
            finally:
                self.stop_progress()
        
        threading.Thread(target=run, daemon=True).start()
    
    # ============= CONVERT TAB =============
    def create_convert_tab(self):
        tab = tk.Frame(self.notebook, bg=self.colors['bg_medium'])
        self.notebook.add(tab, text="🔄 CONVERT")
        
        scrollable = self.create_scrollable_frame(tab)
        
        tk.Label(scrollable, text="Document to PDF Converter", font=('Helvetica', 14, 'bold'),
                fg=self.colors['accent'], bg=self.colors['bg_medium']).pack(pady=10)
        
        self.convert_input = self.create_file_entry(scrollable, "Input File:", 
                                                    [("Documents", "*.docx *.doc *.odt *.xlsx *.pptx"), ("All", "*.*")])
        self.convert_output = self.create_output_entry(scrollable, "Output PDF:", "converted.pdf")
        
        btn = tk.Button(scrollable, text="🚀 CONVERT TO PDF", command=self.convert_to_pdf,
                       bg=self.colors['accent2'], fg='white', font=('Helvetica', 11, 'bold'),
                       padx=20, pady=8, cursor='hand2', bd=0)
        btn.pack(pady=20)
        
        self.convert_log = self.create_log_area(scrollable)
    
    def convert_to_pdf(self):
        if not self.libreoffice_path:
            messagebox.showerror("Error", "LibreOffice not found!")
            return
        
        input_file = self.convert_input.get()
        output_file = self.convert_output.get()
        output_dir = os.path.dirname(output_file)
        
        def run():
            self.start_progress()
            self.log_message(self.convert_log, f"Converting: {os.path.basename(input_file)}")
            
            cmd = [self.libreoffice_path, '--headless', '--convert-to', 'pdf', '--outdir', output_dir, input_file]
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                generated = os.path.join(output_dir, os.path.splitext(os.path.basename(input_file))[0] + '.pdf')
                
                if os.path.exists(generated) and generated != output_file:
                    import shutil
                    shutil.move(generated, output_file)
                
                if os.path.exists(output_file):
                    self.log_message(self.convert_log, f"Conversion complete!")
                else:
                    self.log_message(self.convert_log, f"Conversion failed!", True)
            except Exception as e:
                self.log_message(self.convert_log, f"Error: {str(e)}", True)
            finally:
                self.stop_progress()
        
        threading.Thread(target=run, daemon=True).start()
    
    # ============= IMAGES TAB =============
    def create_images_tab(self):
        tab = tk.Frame(self.notebook, bg=self.colors['bg_medium'])
        self.notebook.add(tab, text="🖼️ PDF TO IMAGES")
        
        scrollable = self.create_scrollable_frame(tab)
        
        tk.Label(scrollable, text="Extract Images from PDF", font=('Helvetica', 14, 'bold'),
                fg=self.colors['accent'], bg=self.colors['bg_medium']).pack(pady=10)
        
        self.images_input = self.create_file_entry(scrollable, "Input PDF:", [("PDF", "*.pdf")])
        
        frame = tk.Frame(scrollable, bg=self.colors['bg_medium'])
        frame.pack(fill='x', padx=20, pady=5)
        
        tk.Label(frame, text="Output Folder:", width=15, anchor='w',
                fg=self.colors['text'], bg=self.colors['bg_medium']).pack(side='left')
        
        self.images_output = tk.Entry(frame, bg=self.colors['bg_dark'], fg=self.colors['text'],
                                      font=('Consolas', 10), relief='flat', bd=1)
        self.images_output.pack(side='left', fill='x', expand=True, padx=(5, 5))
        self.images_output.insert(0, self.default_output)
        
        btn = tk.Button(frame, text="Browse", command=self.browse_images_output,
                       bg=self.colors['bg_light'], fg=self.colors['accent'],
                       cursor='hand2', bd=0, padx=10)
        btn.pack(side='right')
        
        options = tk.Frame(scrollable, bg=self.colors['bg_medium'])
        options.pack(fill='x', padx=20, pady=10)
        
        tk.Label(options, text="Format:", fg=self.colors['text'], bg=self.colors['bg_medium']).pack(side='left', padx=5)
        self.img_format = ttk.Combobox(options, values=['JPEG', 'PNG'], width=10)
        self.img_format.pack(side='left', padx=5)
        self.img_format.current(0)
        
        tk.Label(options, text="DPI:", fg=self.colors['text'], bg=self.colors['bg_medium']).pack(side='left', padx=5)
        self.dpi = ttk.Combobox(options, values=['72', '150', '300'], width=10)
        self.dpi.pack(side='left', padx=5)
        self.dpi.current(1)
        
        btn = tk.Button(scrollable, text="🚀 EXTRACT IMAGES", command=self.pdf_to_images,
                       bg=self.colors['accent2'], fg='white', font=('Helvetica', 11, 'bold'),
                       padx=20, pady=8, cursor='hand2', bd=0)
        btn.pack(pady=20)
        
        self.images_log = self.create_log_area(scrollable)
    
    def browse_images_output(self):
        folder = filedialog.askdirectory()
        if folder:
            self.images_output.delete(0, tk.END)
            self.images_output.insert(0, folder)
    
    def pdf_to_images(self):
        if not self.gs_path:
            messagebox.showerror("Error", "Ghostscript not found!")
            return
        
        input_file = self.images_input.get()
        output_folder = self.images_output.get()
        
        fmt_map = {'JPEG': 'jpeg', 'PNG': 'png16m'}
        ext_map = {'JPEG': 'jpg', 'PNG': 'png'}
        device = fmt_map.get(self.img_format.get(), 'jpeg')
        ext = ext_map.get(self.img_format.get(), 'jpg')
        pattern = os.path.join(output_folder, f"page_%d.{ext}")
        
        def run():
            self.start_progress()
            self.log_message(self.images_log, f"Extracting images from {os.path.basename(input_file)}")
            
            cmd = [self.gs_path, '-dBATCH', '-dNOPAUSE', f'-r{self.dpi.get()}',
                   f'-sDEVICE={device}', f'-sOutputFile={pattern}', input_file]
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    self.log_message(self.images_log, f"Images saved to {output_folder}")
                else:
                    self.log_message(self.images_log, f"Error: {result.stderr}", True)
            except Exception as e:
                self.log_message(self.images_log, f"Error: {str(e)}", True)
            finally:
                self.stop_progress()
        
        threading.Thread(target=run, daemon=True).start()
    
    # ============= MERGE TAB =============
    def create_merge_tab(self):
        tab = tk.Frame(self.notebook, bg=self.colors['bg_medium'])
        self.notebook.add(tab, text="🔗 MERGE")
        
        scrollable = self.create_scrollable_frame(tab)
        
        tk.Label(scrollable, text="Merge PDF Files", font=('Helvetica', 14, 'bold'),
                fg=self.colors['accent'], bg=self.colors['bg_medium']).pack(pady=10)
        
        list_frame = tk.Frame(scrollable, bg=self.colors['bg_dark'])
        list_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        scroll = tk.Scrollbar(list_frame)
        scroll.pack(side='right', fill='y')
        
        self.merge_list = tk.Listbox(list_frame, bg=self.colors['bg_dark'], fg=self.colors['text'],
                                     selectbackground=self.colors['accent2'], height=8,
                                     yscrollcommand=scroll.set)
        self.merge_list.pack(fill='both', expand=True)
        scroll.config(command=self.merge_list.yview)
        
        btn_frame = tk.Frame(scrollable, bg=self.colors['bg_medium'])
        btn_frame.pack(pady=5)
        
        for text, cmd in [("➕ Add PDFs", self.add_pdfs), ("❌ Remove", self.remove_pdf), ("🗑️ Clear", self.clear_pdfs)]:
            btn = tk.Button(btn_frame, text=text, command=cmd, bg=self.colors['bg_light'],
                           fg=self.colors['accent'], cursor='hand2', bd=0, padx=15)
            btn.pack(side='left', padx=5)
        
        self.merge_output = self.create_output_entry(scrollable, "Output PDF:", "merged.pdf")
        
        btn = tk.Button(scrollable, text="🚀 MERGE PDFS", command=self.merge_pdfs,
                       bg=self.colors['accent2'], fg='white', font=('Helvetica', 11, 'bold'),
                       padx=20, pady=8, cursor='hand2', bd=0)
        btn.pack(pady=20)
        
        self.merge_log = self.create_log_area(scrollable)
    
    def add_pdfs(self):
        files = filedialog.askopenfilenames(filetypes=[("PDF", "*.pdf")])
        for f in files:
            self.merge_list.insert(tk.END, f)
    
    def remove_pdf(self):
        for i in reversed(self.merge_list.curselection()):
            self.merge_list.delete(i)
    
    def clear_pdfs(self):
        self.merge_list.delete(0, tk.END)
    
    def merge_pdfs(self):
        if not self.gs_path:
            messagebox.showerror("Error", "Ghostscript not found!")
            return
        
        files = list(self.merge_list.get(0, tk.END))
        output = self.merge_output.get()
        
        if not files:
            messagebox.showerror("Error", "Add PDF files to merge!")
            return
        
        def run():
            self.start_progress()
            self.log_message(self.merge_log, f"Merging {len(files)} PDFs")
            
            cmd = [self.gs_path, '-dBATCH', '-dNOPAUSE', '-sDEVICE=pdfwrite', f'-sOutputFile={output}'] + files
            
            try:
                subprocess.run(cmd, capture_output=True)
                size = os.path.getsize(output) / (1024*1024)
                self.log_message(self.merge_log, f"Merged! Output size: {size:.2f} MB")
            except Exception as e:
                self.log_message(self.merge_log, f"Error: {str(e)}", True)
            finally:
                self.stop_progress()
        
        threading.Thread(target=run, daemon=True).start()
    
    # ============= EXTRACT TAB =============
    def create_extract_tab(self):
        tab = tk.Frame(self.notebook, bg=self.colors['bg_medium'])
        self.notebook.add(tab, text="✂️ EXTRACT")
        
        scrollable = self.create_scrollable_frame(tab)
        
        tk.Label(scrollable, text="Extract PDF Pages", font=('Helvetica', 14, 'bold'),
                fg=self.colors['accent'], bg=self.colors['bg_medium']).pack(pady=10)
        
        self.extract_input = self.create_file_entry(scrollable, "Input PDF:", [("PDF", "*.pdf")])
        
        frame = tk.Frame(scrollable, bg=self.colors['bg_medium'])
        frame.pack(fill='x', padx=20, pady=5)
        
        tk.Label(frame, text="Page Range:", width=15, anchor='w',
                fg=self.colors['text'], bg=self.colors['bg_medium']).pack(side='left')
        
        self.page_range = tk.Entry(frame, bg=self.colors['bg_dark'], fg=self.colors['text'],
                                   font=('Consolas', 10), relief='flat', bd=1)
        self.page_range.pack(side='left', fill='x', expand=True, padx=(5, 5))
        self.page_range.insert(0, "1-10")
        
        self.extract_output = self.create_output_entry(scrollable, "Output PDF:", "extracted.pdf")
        
        btn = tk.Button(scrollable, text="🚀 EXTRACT PAGES", command=self.extract_pages,
                       bg=self.colors['accent2'], fg='white', font=('Helvetica', 11, 'bold'),
                       padx=20, pady=8, cursor='hand2', bd=0)
        btn.pack(pady=20)
        
        self.extract_log = self.create_log_area(scrollable)
    
    def extract_pages(self):
        if not self.gs_path:
            messagebox.showerror("Error", "Ghostscript not found!")
            return
        
        input_file = self.extract_input.get()
        output_file = self.extract_output.get()
        pages = self.page_range.get()
        
        def run():
            self.start_progress()
            self.log_message(self.extract_log, f"Extracting pages: {pages}")
            
            cmd = [self.gs_path, '-dBATCH', '-dNOPAUSE', '-sDEVICE=pdfwrite',
                   f'-sOutputFile={output_file}', input_file]
            
            if '-' in pages:
                start, end = pages.split('-')[0], pages.split('-')[1]
                cmd.insert(2, f'-dFirstPage={start}')
                cmd.insert(3, f'-dLastPage={end}')
            
            try:
                subprocess.run(cmd, capture_output=True)
                self.log_message(self.extract_log, f"Extracted to {output_file}")
            except Exception as e:
                self.log_message(self.extract_log, f"Error: {str(e)}", True)
            finally:
                self.stop_progress()
        
        threading.Thread(target=run, daemon=True).start()
    
    # ============= SECURITY TAB =============
    def create_security_tab(self):
        tab = tk.Frame(self.notebook, bg=self.colors['bg_medium'])
        self.notebook.add(tab, text="🔒 SECURITY")
        
        scrollable = self.create_scrollable_frame(tab)
        
        tk.Label(scrollable, text="PDF Password Protection", font=('Helvetica', 14, 'bold'),
                fg=self.colors['accent'], bg=self.colors['bg_medium']).pack(pady=10)
        
        self.sec_input = self.create_file_entry(scrollable, "Input PDF:", [("PDF", "*.pdf")])
        self.sec_output = self.create_output_entry(scrollable, "Output PDF:", "secured.pdf")
        
        frame = tk.Frame(scrollable, bg=self.colors['bg_medium'])
        frame.pack(fill='x', padx=20, pady=5)
        
        tk.Label(frame, text="Password:", width=15, anchor='w',
                fg=self.colors['text'], bg=self.colors['bg_medium']).pack(side='left')
        
        self.password = tk.Entry(frame, bg=self.colors['bg_dark'], fg=self.colors['text'],
                                 show='*', font=('Consolas', 10), relief='flat', bd=1)
        self.password.pack(side='left', fill='x', expand=True, padx=(5, 5))
        
        btn = tk.Button(scrollable, text="🚀 ADD PASSWORD", command=self.secure_pdf,
                       bg=self.colors['accent2'], fg='white', font=('Helvetica', 11, 'bold'),
                       padx=20, pady=8, cursor='hand2', bd=0)
        btn.pack(pady=20)
        
        self.sec_log = self.create_log_area(scrollable)
    
    def secure_pdf(self):
        if not self.gs_path:
            messagebox.showerror("Error", "Ghostscript not found!")
            return
        
        input_file = self.sec_input.get()
        output_file = self.sec_output.get()
        password = self.password.get()
        
        if not password:
            messagebox.showerror("Error", "Enter a password!")
            return
        
        def run():
            self.start_progress()
            
            cmd = [self.gs_path, '-sDEVICE=pdfwrite', '-dNOPAUSE', '-dQUIET', '-dBATCH',
                   f'-sOwnerPassword={password}', f'-sUserPassword={password}',
                   f'-sOutputFile={output_file}', input_file]
            
            try:
                subprocess.run(cmd, capture_output=True)
                self.log_message(self.sec_log, f"Password protected! Password: {password}")
            except Exception as e:
                self.log_message(self.sec_log, f"Error: {str(e)}", True)
            finally:
                self.stop_progress()
        
        threading.Thread(target=run, daemon=True).start()
    
    # ============= OCR TAB =============
    def create_ocr_tab(self):
        tab = tk.Frame(self.notebook, bg=self.colors['bg_medium'])
        self.notebook.add(tab, text="📝 OCR")
        
        scrollable = self.create_scrollable_frame(tab)
        
        tk.Label(scrollable, text="Extract Text from PDF", font=('Helvetica', 14, 'bold'),
                fg=self.colors['accent'], bg=self.colors['bg_medium']).pack(pady=10)
        
        self.ocr_input = self.create_file_entry(scrollable, "Input PDF:", [("PDF", "*.pdf")])
        
        frame = tk.Frame(scrollable, bg=self.colors['bg_medium'])
        frame.pack(fill='x', padx=20, pady=5)
        
        tk.Label(frame, text="Output TXT:", width=15, anchor='w',
                fg=self.colors['text'], bg=self.colors['bg_medium']).pack(side='left')
        
        self.ocr_output = tk.Entry(frame, bg=self.colors['bg_dark'], fg=self.colors['text'],
                                   font=('Consolas', 10), relief='flat', bd=1)
        self.ocr_output.pack(side='left', fill='x', expand=True, padx=(5, 5))
        self.ocr_output.insert(0, os.path.join(self.default_output, "extracted_text.txt"))
        
        btn_save = tk.Button(frame, text="Save As", command=self.browse_ocr_output,
                            bg=self.colors['bg_light'], fg=self.colors['accent'],
                            cursor='hand2', bd=0, padx=10)
        btn_save.pack(side='right')
        
        btn = tk.Button(scrollable, text="🚀 EXTRACT TEXT", command=self.extract_text,
                       bg=self.colors['accent2'], fg='white', font=('Helvetica', 11, 'bold'),
                       padx=20, pady=8, cursor='hand2', bd=0)
        btn.pack(pady=20)
        
        self.ocr_log = self.create_log_area(scrollable)
    
    def browse_ocr_output(self):
        filename = filedialog.asksaveasfilename(defaultextension=".txt",
                                                filetypes=[("Text files", "*.txt")])
        if filename:
            self.ocr_output.delete(0, tk.END)
            self.ocr_output.insert(0, filename)
    
    def extract_text(self):
        if not self.gs_path:
            messagebox.showerror("Error", "Ghostscript not found!")
            return
        
        input_file = self.ocr_input.get()
        output_file = self.ocr_output.get()
        
        def run():
            self.start_progress()
            
            cmd = [self.gs_path, '-dBATCH', '-dNOPAUSE', '-sDEVICE=txtwrite',
                   f'-sOutputFile={output_file}', input_file]
            
            try:
                subprocess.run(cmd, capture_output=True)
                self.log_message(self.ocr_log, f"Text extracted to {output_file}")
            except Exception as e:
                self.log_message(self.ocr_log, f"Error: {str(e)}", True)
            finally:
                self.stop_progress()
        
        threading.Thread(target=run, daemon=True).start()
    
    # ============= METADATA TAB =============
    def create_metadata_tab(self):
        tab = tk.Frame(self.notebook, bg=self.colors['bg_medium'])
        self.notebook.add(tab, text="ℹ️ METADATA")
        
        scrollable = self.create_scrollable_frame(tab)
        
        tk.Label(scrollable, text="PDF Information", font=('Helvetica', 14, 'bold'),
                fg=self.colors['accent'], bg=self.colors['bg_medium']).pack(pady=10)
        
        self.meta_input = self.create_file_entry(scrollable, "Input PDF:", [("PDF", "*.pdf")])
        
        btn = tk.Button(scrollable, text="🚀 VIEW METADATA", command=self.view_metadata,
                       bg=self.colors['accent2'], fg='white', font=('Helvetica', 11, 'bold'),
                       padx=20, pady=8, cursor='hand2', bd=0)
        btn.pack(pady=20)
        
        self.meta_log = self.create_log_area(scrollable)
    
    def view_metadata(self):
        input_file = self.meta_input.get()
        
        if not os.path.exists(input_file):
            messagebox.showerror("Error", "File not found!")
            return
        
        size = os.path.getsize(input_file) / (1024*1024)
        modified = datetime.fromtimestamp(os.path.getmtime(input_file))
        
        self.log_message(self.meta_log, f"File: {os.path.basename(input_file)}")
        self.log_message(self.meta_log, f"Size: {size:.2f} MB")
        self.log_message(self.meta_log, f"Modified: {modified.strftime('%Y-%m-%d %H:%M:%S')}")
        self.log_message(self.meta_log, f"Path: {input_file}")
    
    # ============= BATCH TAB =============
    def create_batch_tab(self):
        tab = tk.Frame(self.notebook, bg=self.colors['bg_medium'])
        self.notebook.add(tab, text="📊 BATCH")
        
        scrollable = self.create_scrollable_frame(tab)
        
        tk.Label(scrollable, text="Batch Processing", font=('Helvetica', 14, 'bold'),
                fg=self.colors['accent'], bg=self.colors['bg_medium']).pack(pady=10)
        
        frame = tk.Frame(scrollable, bg=self.colors['bg_medium'])
        frame.pack(fill='x', padx=20, pady=5)
        
        tk.Label(frame, text="Input Folder:", width=15, anchor='w',
                fg=self.colors['text'], bg=self.colors['bg_medium']).pack(side='left')
        
        self.batch_input = tk.Entry(frame, bg=self.colors['bg_dark'], fg=self.colors['text'],
                                    font=('Consolas', 10), relief='flat', bd=1)
        self.batch_input.pack(side='left', fill='x', expand=True, padx=(5, 5))
        
        btn = tk.Button(frame, text="Browse", command=self.browse_batch_input,
                       bg=self.colors['bg_light'], fg=self.colors['accent'],
                       cursor='hand2', bd=0, padx=10)
        btn.pack(side='right')
        
        frame2 = tk.Frame(scrollable, bg=self.colors['bg_medium'])
        frame2.pack(fill='x', padx=20, pady=5)
        
        tk.Label(frame2, text="Output Folder:", width=15, anchor='w',
                fg=self.colors['text'], bg=self.colors['bg_medium']).pack(side='left')
        
        self.batch_output = tk.Entry(frame2, bg=self.colors['bg_dark'], fg=self.colors['text'],
                                     font=('Consolas', 10), relief='flat', bd=1)
        self.batch_output.pack(side='left', fill='x', expand=True, padx=(5, 5))
        self.batch_output.insert(0, self.default_output)
        
        btn = tk.Button(frame2, text="Browse", command=self.browse_batch_output,
                       bg=self.colors['bg_light'], fg=self.colors['accent'],
                       cursor='hand2', bd=0, padx=10)
        btn.pack(side='right')
        
        self.batch_action = ttk.Combobox(scrollable, values=['Compress All PDFs', 'Convert to PDF'], width=30)
        self.batch_action.pack(pady=10)
        self.batch_action.current(0)
        
        btn = tk.Button(scrollable, text="🚀 START BATCH", command=self.batch_process,
                       bg=self.colors['accent2'], fg='white', font=('Helvetica', 11, 'bold'),
                       padx=20, pady=8, cursor='hand2', bd=0)
        btn.pack(pady=20)
        
        self.batch_log = self.create_log_area(scrollable)
    
    def browse_batch_input(self):
        folder = filedialog.askdirectory()
        if folder:
            self.batch_input.delete(0, tk.END)
            self.batch_input.insert(0, folder)
    
    def browse_batch_output(self):
        folder = filedialog.askdirectory()
        if folder:
            self.batch_output.delete(0, tk.END)
            self.batch_output.insert(0, folder)
    
    def batch_process(self):
        input_folder = self.batch_input.get()
        output_folder = self.batch_output.get()
        action = self.batch_action.get()
        
        if not input_folder:
            messagebox.showerror("Error", "Select input folder!")
            return
        
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        def run():
            self.start_progress()
            
            if 'Compress' in action and self.gs_path:
                files = [f for f in os.listdir(input_folder) if f.lower().endswith('.pdf')]
                for i, f in enumerate(files):
                    self.log_message(self.batch_log, f"Processing {i+1}/{len(files)}: {f}")
                    in_path = os.path.join(input_folder, f)
                    out_path = os.path.join(output_folder, f"compressed_{f}")
                    cmd = [self.gs_path, '-sDEVICE=pdfwrite', '-dPDFSETTINGS=/ebook',
                           '-dNOPAUSE', '-dQUIET', '-dBATCH', f'-sOutputFile={out_path}', in_path]
                    subprocess.run(cmd, capture_output=True)
                self.log_message(self.batch_log, f"Batch complete! Processed {len(files)} files")
            
            elif 'Convert' in action and self.libreoffice_path:
                files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.docx', '.doc', '.odt'))]
                for i, f in enumerate(files):
                    self.log_message(self.batch_log, f"Converting {i+1}/{len(files)}: {f}")
                    in_path = os.path.join(input_folder, f)
                    cmd = [self.libreoffice_path, '--headless', '--convert-to', 'pdf', '--outdir', output_folder, in_path]
                    subprocess.run(cmd, capture_output=True)
                self.log_message(self.batch_log, f"Batch complete! Converted {len(files)} files")
            
            self.stop_progress()
        
        threading.Thread(target=run, daemon=True).start()

def create_gradient(self):
    """Create diagonal gradient from #FF2CDF to #0014FF"""
    width = self.root.winfo_width()
    height = self.root.winfo_height()
    
    if width < 10:
        width = 1200
        height = 800
    
    self.gradient_canvas.delete("gradient")
    
    max_dist = math.sqrt(width**2 + height**2)
    
    for y in range(height):
        for x in range(width):
            # Distance from top-left corner
            dist = math.sqrt(x**2 + y**2)
            ratio = min(1.0, dist / max_dist)
            
            r = int(255 * (1 - ratio) + 0 * ratio)
            g = int(44 * (1 - ratio) + 20 * ratio)
            b = int(223 * (1 - ratio) + 255 * ratio)
            
            color = f'#{r:02x}{g:02x}{b:02x}'
            self.gradient_canvas.create_line(x, y, x+1, y, fill=color, tags="gradient")

		



if __name__ == "__main__":
    root = tk.Tk()
    app = SpacePDFStudio(root)
    root.mainloop()
