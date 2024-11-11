import tkinter as tk
from tkinter import ttk
import os
from pathlib import Path
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import markdown
from tkhtmlview import HTMLLabel

class ResultsViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Esports Manager Results Viewer")
        self.geometry("1200x800")
        
        # Create main container
        self.main_container = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel for navigation
        self.left_panel = ttk.Frame(self.main_container)
        self.main_container.add(self.left_panel)
        
        # Search frame
        self.search_frame = ttk.Frame(self.left_panel)
        self.search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_tree)
        self.search_entry = ttk.Entry(self.search_frame, textvariable=self.search_var)
        self.search_entry.pack(fill=tk.X)
        
        # Create treeview
        self.tree = ttk.Treeview(self.left_panel)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar for tree
        self.tree_scroll = ttk.Scrollbar(self.left_panel, orient="vertical", command=self.tree.yview)
        self.tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=self.tree_scroll.set)
        
        # Right panel for content
        self.right_panel = ttk.Frame(self.main_container)
        self.main_container.add(self.right_panel)
        
        # Frame for content with scrollbar
        self.content_frame = ttk.Frame(self.right_panel)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create both text widget and HTML label
        self.content_text = tk.Text(self.content_frame, wrap=tk.WORD, padx=10, pady=10)
        self.html_label = HTMLLabel(self.content_frame, padx=10, pady=10)
        
        # Scrollbar for content
        self.text_scroll = ttk.Scrollbar(self.content_frame, orient="vertical")
        self.text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure scrollbar for both widgets
        self.content_text.configure(yscrollcommand=self.text_scroll.set)
        self.text_scroll.configure(command=self.content_text.yview)
        
        # Bind tree selection
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        
        # Initialize file watcher
        self.setup_file_watcher()
        
        # Load initial data
        self.refresh_tree()

    def setup_file_watcher(self):
        self.observer = Observer()
        event_handler = ResultsFileHandler(self)
        self.observer.schedule(event_handler, "previous_results", recursive=True)
        self.observer.start()

    def add_directory_to_tree(self, path, parent=""):
        """Recursively add directory contents to tree"""
        try:
            for item in sorted(path.iterdir()):
                if item.is_dir():
                    # Create directory node
                    dir_id = self.tree.insert(parent, "end", text=item.name)
                    # Recursively add its contents
                    self.add_directory_to_tree(item, dir_id)
                else:
                    # Add file node
                    self.tree.insert(parent, "end", text=item.name, values=(str(item),))
        except PermissionError:
            pass  # Skip directories we can't access

    def refresh_tree(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Load directory structure
        results_path = Path("previous_results")
        if not results_path.exists():
            return
        
        # Recursively populate tree
        self.add_directory_to_tree(results_path)

    def filter_tree(self, *args):
        search_term = self.search_var.get().lower()
        self.refresh_tree()  # Reset tree
        
        if not search_term:
            return
            
        def check_item_and_children(item):
            matches = False
            item_text = self.tree.item(item)['text'].lower()
            
            # Check children first
            for child in self.tree.get_children(item):
                if check_item_and_children(child):
                    matches = True
                
            # If neither item nor children match, detach
            if not matches and not search_term in item_text:
                self.tree.detach(item)
                return False
                
            return True
        
        # Check all top-level items
        for item in self.tree.get_children():
            check_item_and_children(item)

    def show_content(self, file_path, content):
        """Display content either as markdown or plain text"""
        # Hide both widgets initially
        self.content_text.pack_forget()
        self.html_label.pack_forget()
        
        if file_path.suffix.lower() == '.md':
            # Convert markdown to HTML and display in HTML label
            html_content = markdown.markdown(content)
            self.html_label.pack(fill=tk.BOTH, expand=True)
            self.html_label.set_html(html_content)
        else:
            # Display plain text
            self.content_text.pack(fill=tk.BOTH, expand=True)
            self.content_text.delete(1.0, tk.END)
            self.content_text.insert(tk.END, content)

    def on_select(self, event):
        selected_items = self.tree.selection()
        if not selected_items:
            return
            
        selected_item = selected_items[0]
        file_path = self.tree.item(selected_item)['values']
        
        if file_path:  # If it's a file (not a directory)
            file_path = Path(file_path[0])
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.show_content(file_path, content)
            except Exception as e:
                self.content_text.delete(1.0, tk.END)
                self.content_text.insert(tk.END, f"Error reading file: {str(e)}")

class ResultsFileHandler(FileSystemEventHandler):
    def __init__(self, gui):
        self.gui = gui
        self.last_refresh = 0
        self.refresh_cooldown = 1.0  # Seconds

    def on_any_event(self, event):
        current_time = time.time()
        if current_time - self.last_refresh >= self.refresh_cooldown:
            self.gui.after(100, self.gui.refresh_tree)
            self.last_refresh = current_time

if __name__ == "__main__":
    app = ResultsViewer()
    app.mainloop()
