"""
GUI Version - Single-Page Web Analyzer
=======================================
GUI version for easier usage.

Course: Theory of Computation
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
from web_analyzer import WebAnalyzer
from regex_visualizer import RegexVisualizer


class WebAnalyzerGUI:
    """
    GUI for the Web Analyzer.
    Easier to use than the command line version.
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("🌐 Single-Page Web Analyzer - TOC Project")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        self.analyzer = None
        self.create_widgets()
        
    def create_widgets(self):
        """Create all widgets."""
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(
            header_frame, 
            text="🌐 Single-Page Web Analyzer", 
            font=('Arial', 18, 'bold')
        ).pack(side=tk.LEFT)
        
        ttk.Label(
            header_frame,
            text="📚 Theory of Computation Project",
            font=('Arial', 10)
        ).pack(side=tk.RIGHT)
        
        # URL Input Frame
        url_frame = ttk.LabelFrame(main_frame, text="URL Input", padding="5")
        url_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        url_frame.columnconfigure(1, weight=1)
        
        ttk.Label(url_frame, text="URL:").grid(row=0, column=0, padx=5)
        self.url_entry = ttk.Entry(url_frame, width=60)
        self.url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        self.url_entry.insert(0, "https://")
        
        # Buttons Frame
        btn_frame = ttk.Frame(url_frame)
        btn_frame.grid(row=0, column=2, padx=5)
        
        self.analyze_btn = ttk.Button(
            btn_frame, 
            text="🔍 Analyze", 
            command=self.start_analysis
        )
        self.analyze_btn.pack(side=tk.LEFT, padx=2)
        
        self.clear_btn = ttk.Button(
            btn_frame,
            text="🗑️ Clear",
            command=self.clear_results
        )
        self.clear_btn.pack(side=tk.LEFT, padx=2)
        
        # Options Frame
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="5")
        options_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.extract_emails = tk.BooleanVar(value=True)
        self.extract_phones = tk.BooleanVar(value=True)
        self.extract_urls = tk.BooleanVar(value=True)
        self.extract_ips = tk.BooleanVar(value=True)
        self.extract_social = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(options_frame, text="📧 Emails", variable=self.extract_emails).pack(side=tk.LEFT, padx=10)
        ttk.Checkbutton(options_frame, text="📞 Phones", variable=self.extract_phones).pack(side=tk.LEFT, padx=10)
        ttk.Checkbutton(options_frame, text="🔗 URLs", variable=self.extract_urls).pack(side=tk.LEFT, padx=10)
        ttk.Checkbutton(options_frame, text="🌐 IPs", variable=self.extract_ips).pack(side=tk.LEFT, padx=10)
        ttk.Checkbutton(options_frame, text="📱 Social", variable=self.extract_social).pack(side=tk.LEFT, padx=10)
        
        # Results Notebook (Tabs)
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Results Tab
        results_frame = ttk.Frame(notebook, padding="5")
        notebook.add(results_frame, text="📊 Results")
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        self.results_text = scrolledtext.ScrolledText(
            results_frame, 
            wrap=tk.WORD, 
            width=100, 
            height=25,
            font=('Consolas', 10)
        )
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Emails Tab
        emails_frame = ttk.Frame(notebook, padding="5")
        notebook.add(emails_frame, text="📧 Emails")
        emails_frame.columnconfigure(0, weight=1)
        emails_frame.rowconfigure(0, weight=1)
        
        self.emails_list = tk.Listbox(emails_frame, font=('Consolas', 10))
        self.emails_list.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        emails_scroll = ttk.Scrollbar(emails_frame, orient=tk.VERTICAL, command=self.emails_list.yview)
        emails_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.emails_list.configure(yscrollcommand=emails_scroll.set)
        
        # URLs Tab
        urls_frame = ttk.Frame(notebook, padding="5")
        notebook.add(urls_frame, text="🔗 URLs")
        urls_frame.columnconfigure(0, weight=1)
        urls_frame.rowconfigure(0, weight=1)
        
        self.urls_list = tk.Listbox(urls_frame, font=('Consolas', 10))
        self.urls_list.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        urls_scroll = ttk.Scrollbar(urls_frame, orient=tk.VERTICAL, command=self.urls_list.yview)
        urls_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.urls_list.configure(yscrollcommand=urls_scroll.set)
        
        # Regex Patterns Tab
        regex_frame = ttk.Frame(notebook, padding="5")
        notebook.add(regex_frame, text="📚 Regex Patterns")
        regex_frame.columnconfigure(0, weight=1)
        regex_frame.rowconfigure(0, weight=1)
        
        self.regex_text = scrolledtext.ScrolledText(
            regex_frame,
            wrap=tk.WORD,
            width=100,
            height=25,
            font=('Consolas', 9)
        )
        self.regex_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.show_regex_explanation()
        
        # Status Bar
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var)
        self.status_label.pack(side=tk.LEFT)
        
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate', length=200)
        self.progress.pack(side=tk.RIGHT)
        
        # Export Button
        export_btn = ttk.Button(status_frame, text="💾 Export CSV", command=self.export_results)
        export_btn.pack(side=tk.RIGHT, padx=10)
        
    def start_analysis(self):
        """Start analysis in a separate thread."""
        url = self.url_entry.get().strip()
        
        if not url or url == "https://":
            messagebox.showwarning("Warning", "Please enter a URL")
            return
            
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, url)
        
        self.analyze_btn.config(state='disabled')
        self.progress.start()
        self.status_var.set("Analyzing...")
        
        # Run in separate thread
        thread = threading.Thread(target=self.analyze_url, args=(url,))
        thread.daemon = True
        thread.start()
        
    def analyze_url(self, url):
        """Analyze the URL."""
        try:
            self.analyzer = WebAnalyzer(url)
            results = self.analyzer.analyze()
            
            if results:
                self.root.after(0, self.display_results)
            else:
                self.root.after(0, lambda: messagebox.showerror("Error", "Unable to analyze the web page"))
                
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
        finally:
            self.root.after(0, self.analysis_complete)
            
    def analysis_complete(self):
        """Called when analysis is complete."""
        self.analyze_btn.config(state='normal')
        self.progress.stop()
        self.status_var.set("Complete")
        
    def display_results(self):
        """Display the results."""
        self.clear_results()
        
        if not self.analyzer:
            return
            
        results = self.analyzer.results
        stats = self.analyzer.get_statistics()
        
        # Main results tab
        text = []
        text.append("=" * 60)
        text.append(f"📊 Analysis Results: {self.analyzer.url}")
        text.append("=" * 60)
        text.append(f"\n📄 Page Title: {results['page_title']}")
        text.append(f"📝 Meta Description: {results['meta_description'][:100]}...")
        
        text.append(f"\n\n📈 Summary Statistics")
        text.append("-" * 40)
        text.append(f"📧 Emails: {stats['total_emails']}")
        text.append(f"📞 Phones: {stats['total_phones']}")
        text.append(f"🔗 URLs: {stats['total_urls']}")
        text.append(f"   - Internal: {stats['internal_links']}")
        text.append(f"   - External: {stats['external_links']}")
        text.append(f"🌐 IP Addresses: {stats['total_ips']}")
        text.append(f"📱 Social Platforms: {stats['total_social_platforms']}")
        
        if results['phones']:
            text.append(f"\n\n📞 Phone numbers found ({len(results['phones'])} items):")
            text.append("-" * 40)
            for i, phone in enumerate(results['phones'][:20], 1):
                text.append(f"  {i}. {phone}")
                
        if results['ip_addresses']:
            text.append(f"\n\n🌐 IP Addresses ({len(results['ip_addresses'])} items):")
            text.append("-" * 40)
            for i, ip in enumerate(results['ip_addresses'][:10], 1):
                text.append(f"  {i}. {ip}")
                
        if results['social_media']:
            text.append(f"\n\n📱 Social Media:")
            text.append("-" * 40)
            for platform, links in results['social_media'].items():
                text.append(f"  {platform.capitalize()}: {len(links)} links")
        
        self.results_text.insert(tk.END, "\n".join(text))
        
        # Emails list
        for email in results['emails']:
            self.emails_list.insert(tk.END, email)
            
        # URLs list
        for url in results['urls']:
            self.urls_list.insert(tk.END, url)
            
    def clear_results(self):
        """Clear all results."""
        self.results_text.delete(1.0, tk.END)
        self.emails_list.delete(0, tk.END)
        self.urls_list.delete(0, tk.END)
        
    def show_regex_explanation(self):
        """Show regex pattern explanations."""
        explanation = """Regex Patterns Used in This Project
====================================

1. EMAIL:  [a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}
2. PHONE:  0[0-9]{1,2}[-.\\s]?[0-9]{3}[-.\\s]?[0-9]{4}
3. URL:    https?://[a-zA-Z0-9][-a-zA-Z0-9]*(?:\\.[a-zA-Z0-9][-a-zA-Z0-9]*)+
4. IP:     \\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}...
5. HREF:   href=["\\'](.*?)["\\'"]
6. SRC:    src=["\\'](.*?)["\\'"]
7. TITLE:  <title[^>]*>([^<]+)</title>
8. META:   <meta[^>]+name=['"]description['"][^>]+content=['"]([^'"]+)['"]
"""
        self.regex_text.insert(tk.END, explanation)
        
    def export_results(self):
        """Export results to CSV."""
        if not self.analyzer or not self.analyzer.results:
            messagebox.showwarning("Warning", "No data to export")
            return
            
        folder = filedialog.askdirectory(title="Select folder to save files")
        if folder:
            import os
            original_dir = os.getcwd()
            try:
                os.chdir(folder)
                self.analyzer.export_to_csv()
                messagebox.showinfo("Success", f"Files saved to {folder}")
            finally:
                os.chdir(original_dir)


def main():
    """Run GUI application"""
    root = tk.Tk()
    app = WebAnalyzerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
