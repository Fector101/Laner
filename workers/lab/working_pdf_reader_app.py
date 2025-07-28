import fitz  # PyMuPDF
from PIL import Image, ImageTk
import io
import tkinter as tk
from tkinter import ttk

class PDFViewer:
    def __init__(self, root, pdf_path):
        self.root = root
        self.root.title("PDF Viewer")
        
        # Set fixed window size (you can adjust these values)
        self.window_width = 1000
        self.window_height = 600
        self.root.geometry(f"{self.window_width}x{self.window_height}")
        self.root.minsize(800, 600)  # Minimum size the user can resize to
        
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        self.current_page = 0
        self.total_pages = len(self.doc)
        
        # Create main container with scrollbars
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbars
        self.hscroll = ttk.Scrollbar(self.main_frame, orient=tk.HORIZONTAL)
        self.vscroll = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL)
        
        # Create canvas with scrollbars
        self.canvas = tk.Canvas(
            self.main_frame,
            bg="white",
            xscrollcommand=self.hscroll.set,
            yscrollcommand=self.vscroll.set
        )
        
        self.hscroll.config(command=self.canvas.xview)
        self.vscroll.config(command=self.canvas.yview)
        
        # Grid layout for proper resizing
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.vscroll.grid(row=0, column=1, sticky="ns")
        self.hscroll.grid(row=1, column=0, sticky="ew")
        
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Navigation controls (separate frame at bottom)
        self.controls = ttk.Frame(root)
        self.controls.pack(fill=tk.X, padx=5, pady=5)
        
        self.prev_btn = ttk.Button(self.controls, text="Previous", command=self.prev_page)
        self.prev_btn.pack(side=tk.LEFT, padx=5)
        
        self.next_btn = ttk.Button(self.controls, text="Next", command=self.next_page)
        self.next_btn.pack(side=tk.LEFT, padx=5)
        
        self.page_label = ttk.Label(self.controls, text=f"Page {self.current_page + 1} of {self.total_pages}")
        self.page_label.pack(side=tk.LEFT, padx=5)
        
        # Display first page
        self.display_page()
    
    def display_page(self):
        # Get the page
        page = self.doc.load_page(self.current_page)
        
        # Calculate zoom to fit the fixed window size
        zoom_width = (self.window_width - 40) / page.rect.width
        zoom_height = (self.window_height - 100) / page.rect.height
        zoom = min(zoom_width, zoom_height)
        
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        
        # Convert to ImageTk
        img = Image.open(io.BytesIO(pix.tobytes()))
        self.tk_img = ImageTk.PhotoImage(img)
        
        # Update canvas
        self.canvas.delete("all")
        self.canvas.config(scrollregion=(0, 0, pix.width, pix.height))
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_img)
        
        # Center the image in the canvas
        self.canvas.xview_moveto(0.5 - (self.window_width/pix.width)/2)
        self.canvas.yview_moveto(0.5 - (self.window_height/pix.height)/2)
        
        self.page_label.config(text=f"Page {self.current_page + 1} of {self.total_pages}")
    
    def next_page(self):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.display_page()
    
    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.display_page()

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFViewer(root, "test.pdf")
    root.mainloop()