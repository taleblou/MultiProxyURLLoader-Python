import os
import random
import tkinter as tk
from tkinter import messagebox, Label, Button, Entry, ttk
import requests
import threading

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Load Random")
        self.proxyList = []
        self.proxyIndex = 0
        self.count = 0
        self.duration = 10  # Default duration in seconds

        # GUI Components
        self.proxy_progress = ttk.Progressbar(self, orient='horizontal', mode='determinate')
        self.proxy_progress.pack(pady=10)

        self.run_label = Label(self, text="0")
        self.run_label.pack()

        self.success_label = Label(self, text="0")
        self.success_label.pack()

        self.url_entry = Entry(self, width=50)
        self.url_entry.pack(pady=5)
        self.url_entry.insert(0, "https://taleblou.ir/")

        self.url_count_entry = Entry(self, width=10)
        self.url_count_entry.pack(pady=5)
        self.url_count_entry.insert(0, "10")

        self.duration_entry = Entry(self, width=10)
        self.duration_entry.pack(pady=5)
        self.duration_entry.insert(0, "10")

        self.run_button = Button(self, text="Run", command=self.start_process)
        self.run_button.pack(pady=5)

        self.stop_button = Button(self, text="Stop", state=tk.DISABLED, command=self.stop_process)
        self.stop_button.pack(pady=5)

        # Load proxy lists in the background
        self.load_proxy_list()

    def load_proxy_list(self):
        proxy_urls = [
            "https://raw.githubusercontent.com/mmpx12/proxy-list/refs/heads/master/http.txt",
            "https://raw.githubusercontent.com/mmpx12/proxy-list/refs/heads/master/https.txt"
        ]
        proxy_files = ["http.txt", "https.txt"]

        def load_proxies():
            for url, filename in zip(proxy_urls, proxy_files):
                try:
                    response = requests.get(url)
                    response.raise_for_status()
                    with open(filename, 'wb') as f:
                        f.write(response.content)
                except requests.exceptions.RequestException as e:
                    messagebox.showerror("Error", f"Failed to load proxy list from {url}: {e}")

            combined_proxies = []
            for filename in proxy_files:
                if os.path.exists(filename):
                    with open(filename, 'r') as f:
                        combined_proxies.extend(f.read().splitlines())

            if not combined_proxies:
                if os.path.exists("temp.txt"):
                    with open("temp.txt", 'r') as f:
                        combined_proxies.extend(f.read().splitlines())
                else:
                    messagebox.showerror("Error", "No proxies available.")
                    return

            random.shuffle(combined_proxies)
            self.proxyList = combined_proxies
            self.proxy_progress['maximum'] = len(self.proxyList)
            self.proxy_progress['value'] = 0

        threading.Thread(target=load_proxies).start()

    def start_process(self):
        self.stop_button.config(state=tk.NORMAL)
        self.run_button.config(state=tk.DISABLED)
        self.duration = int(self.duration_entry.get())
        self.run_async()

    def stop_process(self):
        self.run_label.config(text="0")
        self.success_label.config(text="0")
        self.proxyIndex = 0
        self.proxy_progress['value'] = 0
        self.stop_button.config(state=tk.DISABLED)
        self.run_button.config(state=tk.NORMAL)

    def run_async(self):
        url_count = int(self.url_count_entry.get())
        for _ in range(url_count):
            self.after(self.duration * 1000, self.load_url_with_proxy)

    def load_url_with_proxy(self):
        proxy = self.get_current_proxy()
        if not proxy:
            return

        proxies = {
            "http": proxy,
            "https": proxy
        }
        try:
            response = requests.get(self.url_entry.get(), proxies=proxies, timeout=10)
            if response.status_code == 200:
                self.count += 1
                self.success_label.config(text=str(self.count))
            else:
                print(f"Proxy failed with status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")

        self.proxy_progress['value'] = self.proxyIndex
        self.run_label.config(text=str(self.proxyIndex))

    def get_current_proxy(self):
        if self.proxyIndex >= len(self.proxyList):
            self.proxyIndex = 0
        proxy = self.proxyList[self.proxyIndex]
        self.proxyIndex += 1
        return proxy

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()