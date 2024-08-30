import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import threading
import tkinter as tk
from tkinter import messagebox
import os
import webbrowser
import time

IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp')
WEBPAGE_EXTENSIONS = ('.html', '.htm', '.php', '.asp', '.aspx', '.jsp', '.jspx', '.cgi', '.pl')

def get_links(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        links = [a.get('href') for a in soup.find_all('a', href=True)]
        absolute_links = [urljoin(url, link) for link in links]
        return absolute_links
    except Exception as e:
        print(f"Hata: {str(e)}")
        return []

def is_valid_url(url):
    parsed_url = urlparse(url)
    return (parsed_url.path.endswith(WEBPAGE_EXTENSIONS) or not parsed_url.path or '.' not in parsed_url.path.split('/')[-1]) and not parsed_url.path.endswith(IMAGE_EXTENSIONS)

def crawl_site(root_url, progress_var, max_depth=-1):
    visited = set()
    queue = [(root_url, 0)]
    domain = urlparse(root_url).netloc
    total_links = 0

    while queue:
        url, depth = queue.pop(0)
        if max_depth != -1 and depth > max_depth:
            continue
        if url in visited:
            continue
        visited.add(url)

        if domain not in url:
            continue

        if not is_valid_url(url):
            continue

        links = get_links(url)
        for link in links:
            if link not in visited and domain in link:
                queue.append((link, depth + 1))
                total_links += 1
                update_progress(progress_var, total_links)

    return visited

def update_progress(progress_var, total_links):
    progress_var.set(min(total_links, 100))  
    color = "red" if total_links < 33 else "yellow" if total_links < 66 else "green"
    progress_bar.config(fg=color)
    root.update_idletasks()

def create_sitemap(start_url, visited):
    filename = "sitemap.xml"
    with open(filename, 'w', encoding='utf-8') as file:
        file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        file.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for url in visited:
            file.write(f'<url><loc>{url}</loc></url>\n')
        file.write('</urlset>\n')
    messagebox.showinfo("Başarılı", f"Sitemap '{filename}' olarak kaydedildi!")
    webbrowser.open(f"file://{os.path.realpath(filename)}")

def save_site_to_file(site_url):
    with open("site.txt", "a") as file:
        file.write(site_url + "\n")
    messagebox.showinfo("Kaydedildi", f"Site '{site_url}' site.txt dosyasına kaydedildi.")

def load_sites_from_file():
    if os.path.exists("site.txt"):
        with open("site.txt", "r") as file:
            sites = file.read().splitlines()
        return sites
    return []

def start_crawling():
    start_time = time.time()
    root_url = url_entry.get()
    if not root_url:
        messagebox.showerror("Hata", "Lütfen site URL'sini girin.")
        return

    progress_var.set(0)
    visited_links = crawl_site(root_url, progress_var)
    create_sitemap(root_url, visited_links)

    end_time = time.time()
    duration = end_time - start_time

    start_time_label.config(text=f"Başlangıç Zamanı: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}")
    end_time_label.config(text=f"Bitiş Zamanı: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))}")
    duration_label.config(text=f"Geçen Süre: {duration:.2f} saniye")

def start_crawling_thread():
    threading.Thread(target=start_crawling).start()

root = tk.Tk()
root.title("Sitemap Oluşturucu")
root.geometry("600x500")

try:
    root.iconphoto(False, tk.PhotoImage(file='favicon.png'))
except Exception as e:
    print(f"Favicon hatası: {e}")

try:
    logo = tk.PhotoImage(file="logo.png")
    logo_label = tk.Label(root, image=logo)
    logo_label.pack(pady=10)
except Exception as e:
    print(f"Logo hatası: {e}")

tk.Label(root, text="Kayıtlı Siteler:").pack(pady=5)
sites = load_sites_from_file()
site_choice = tk.StringVar(root)
site_choice.set("Manuel URL Girişi")  
if sites:
    site_option_menu = tk.OptionMenu(root, site_choice, *sites, "Manuel URL Girişi")
else:
    site_option_menu = tk.OptionMenu(root, site_choice, "Manuel URL Girişi")
site_option_menu.pack(pady=5)

tk.Label(root, text="Web sitesi URL'si:").pack(pady=5)
url_entry = tk.Entry(root, width=50)
url_entry.pack()

def update_url_entry(*args):
    selected_site = site_choice.get()
    if selected_site != "Manuel URL Girişi":
        url_entry.delete(0, tk.END)
        url_entry.insert(0, selected_site)

site_choice.trace('w', update_url_entry)

progress_var = tk.IntVar()
progress_bar = tk.Scale(root, variable=progress_var, from_=0, to=100, orient="horizontal", length=400)
progress_bar.pack(pady=20)

start_time_label = tk.Label(root, text="Başlangıç Zamanı: ")
start_time_label.pack()
end_time_label = tk.Label(root, text="Bitiş Zamanı: ")
end_time_label.pack()
duration_label = tk.Label(root, text="Geçen Süre: ")
duration_label.pack()

start_button = tk.Button(root, text="Sitemap Oluştur", command=start_crawling_thread)
start_button.pack(pady=10)

save_button = tk.Button(root, text="Siteyi Kaydet", command=lambda: save_site_to_file(url_entry.get()))
save_button.pack(pady=5)

root.mainloop()
