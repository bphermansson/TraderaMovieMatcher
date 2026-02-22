#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import requests
from bs4 import BeautifulSoup
import threading
import urllib.parse
import re
import time
import concurrent.futures
import webbrowser
import uuid

class TraderaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tradera Movie Matcher")
        self.root.geometry("850x700") 
        
        style = ttk.Style()
        if 'clam' in style.theme_names():
            style.theme_use('clam')
            
        main_frame = ttk.Frame(root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        input_label = ttk.Label(main_frame, text="1. Skriv in filmer (en titel per rad):", font=("Ubuntu", 11, "bold"))
        input_label.pack(anchor="w", pady=(0, 5))
        
        self.input_text = scrolledtext.ScrolledText(main_frame, height=8, width=80, font=("Ubuntu", 11))
        self.input_text.pack(fill=tk.X, pady=(0, 5))
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        self.load_btn = ttk.Button(btn_frame, text="📂 Ladda Lista", command=self.load_search)
        self.load_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.save_btn = ttk.Button(btn_frame, text="💾 Spara Lista", command=self.save_search)
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        self.search_btn = ttk.Button(btn_frame, text="🔍 Hitta Säljare", command=self.start_search)
        self.search_btn.pack(side=tk.RIGHT)
        
        self.status_var = tk.StringVar(value="Status: Redo")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var, font=("Ubuntu", 10, "italic"), foreground="#555555")
        self.status_label.pack(anchor="w", pady=(5, 5))
        
        output_label = ttk.Label(main_frame, text="2. Matchande säljare:", font=("Ubuntu", 11, "bold"))
        output_label.pack(anchor="w", pady=(10, 5))
        
        self.output_text = scrolledtext.ScrolledText(main_frame, height=15, width=80, font=("Ubuntu", 11), state=tk.DISABLED)
        self.output_text.pack(fill=tk.BOTH, expand=True)

    def save_search(self):
        movies_text = self.input_text.get("1.0", tk.END).strip()
        if not movies_text:
            messagebox.showwarning("Tom lista", "Det finns inga filmer att spara!")
            return
            
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Textfiler", "*.txt"), ("Alla filer", "*.*")],
            title="Spara filmlista som"
        )
        
        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as file:
                    file.write(movies_text)
                self.status_var.set(f"Status: Sparade listan i {filepath}")
            except Exception as e:
                messagebox.showerror("Fel vid sparande", f"Kunde inte spara filen:\n{e}")

    def load_search(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("Textfiler", "*.txt"), ("Alla filer", "*.*")],
            title="Ladda filmlista"
        )
        
        if filepath:
            try:
                with open(filepath, 'r', encoding='utf-8') as file:
                    movies_text = file.read()
                
                self.input_text.delete("1.0", tk.END)
                self.input_text.insert(tk.END, movies_text)
                self.status_var.set(f"Status: Laddade lista från {filepath}")
            except Exception as e:
                messagebox.showerror("Fel vid laddning", f"Kunde inte ladda filen:\n{e}")

    def start_search(self):
        raw_movies = self.input_text.get("1.0", tk.END).strip().split('\n')
        
        movies = []
        seen = set()
        for m in raw_movies:
            clean_m = m.strip()
            if clean_m and clean_m.lower() not in seen:
                seen.add(clean_m.lower())
                movies.append(clean_m)
        
        if len(movies) < 1:
            messagebox.showwarning("Inmatningsfel", "Vänligen ange minst en filmtitel att söka efter.")
            return
            
        self.search_btn.config(state=tk.DISABLED)
        self.load_btn.config(state=tk.DISABLED)
        self.save_btn.config(state=tk.DISABLED)
        
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.config(state=tk.DISABLED)
        
        thread = threading.Thread(target=self.run_search, args=(movies,))
        thread.daemon = True
        thread.start()
        
    def run_search(self, movies):
        seller_inventory = {}  
        
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "sv-SE,sv;q=0.8,en-US;q=0.5,en;q=0.3",
        }
        
        session = requests.Session()
        
        for movie in movies:
            self.root.after(0, self.status_var.set, f"Status: Söker i Filmer (kategori 13) efter '{movie}'...")
            
            url = f"https://www.tradera.com/search?q={urllib.parse.quote_plus(movie)}&categoryId=13"
            
            try:
                response = session.get(url, headers=headers, timeout=15)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                if soup.title and "moment" in soup.title.text.lower():
                    self.update_result(f"[!] '{movie}': Tradera blockerade anslutningen tillfälligt.\n")
                    continue
                
                seen_items = {}
                for a in soup.find_all('a', href=re.compile(r'/item/')):
                    item_url = a.get('href', '')
                    if item_url.startswith('/'):
                        item_url = 'https://www.tradera.com' + item_url
                        
                    match = re.search(r'/item/[^/]+/(\d+)/', item_url)
                    if not match:
                        match = re.search(r'/item/(\d+)', item_url)
                        
                    if not match:
                        continue
                        
                    item_id = match.group(1)
                    title = a.text.strip()
                    
                    if not title:
                        img = a.find('img')
                        if img and img.get('alt'):
                            title = img.get('alt').strip()
                            
                    # --- NY BÄTTRE PRIS-AVSNING ---
                    price = "Pris okänt"
                    
                    # Klättra uppåt i HTML-trädet från länken tills vi hittar något som innehåller "kr"
                    container = a
                    for _ in range(5): 
                        if container.parent and container.parent.name not in ['body', 'html']:
                            container = container.parent
                            if re.search(r'\d\s*kr', container.text, re.IGNORECASE):
                                break
                    
                    if container:
                        # Rensa bort dolda html-mellanslag
                        c_text = container.text.replace('\xa0', ' ')
                        # Fånga siffror (även med mellanslag typ 1 200) följt av kr
                        prices = re.findall(r'(\d+(?:[ ]\d+)*)\s*kr', c_text, re.IGNORECASE)
                        if prices:
                            price = prices[0].strip() + " kr"
                    
                    if item_id not in seen_items:
                        seen_items[item_id] = {'url': item_url, 'title': title, 'price': price}
                    else:
                        if len(title) > len(seen_items[item_id]['title']):
                            seen_items[item_id]['title'] = title
                        if price != "Pris okänt":
                            seen_items[item_id]['price'] = price
                            
                items_to_check = list(seen_items.values())[:30] 
                
                if not items_to_check:
                    self.update_result(f"[-] '{movie}': Sökningen gav inga träffar i Filmer (kat 13).\n")
                    continue
                    
                self.root.after(0, self.status_var.set, f"Status: Läser av säljare inuti {len(items_to_check)} annonser ('{movie}')...")
                
                def fetch_seller(data):
                    try:
                        resp = session.get(data['url'], headers=headers, timeout=10)
                        if resp.status_code == 200:
                            item_soup = BeautifulSoup(resp.text, 'html.parser')
                            
                            title = data['title']
                            if not title or len(title) < 3:
                                h1 = item_soup.find('h1')
                                if h1:
                                    title = h1.text.strip()
                            if not title:
                                title = "Okänd titel"
                                
                            # Backup-koll för priset inne på själva annonsen
                            price = data['price']
                            if price == "Pris okänt":
                                meta_price = item_soup.find('meta', property=re.compile(r'price:amount', re.IGNORECASE))
                                if not meta_price:
                                    meta_price = item_soup.find('meta', attrs={'itemprop': 'price'})
                                    
                                if meta_price and meta_price.get('content'):
                                    price = meta_price.get('content').split('.')[0] + " kr"
                                
                            for link in item_soup.find_all('a', href=re.compile(r'/profile/')):
                                href = link.get('href', '')
                                seller_alias = href.rstrip('/').split('/')[-1]
                                if seller_alias and seller_alias.lower() not in ['reviews', 'ratings']:
                                    return urllib.parse.unquote(seller_alias), title, data['url'], price
                    except:
                        pass
                    return None, None, None, None

                found_count = 0
                with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                    results = executor.map(fetch_seller, items_to_check)
                    
                    for seller, title, item_url, price in results:
                        if seller:
                            if seller not in seller_inventory:
                                seller_inventory[seller] = {}
                            if movie not in seller_inventory[seller]:
                                seller_inventory[seller][movie] = []
                                
                            if not any(item['url'] == item_url for item in seller_inventory[seller][movie]):
                                seller_inventory[seller][movie].append({
                                    'title': title, 
                                    'url': item_url,
                                    'price': price
                                })
                                found_count += 1
                                
                if found_count == 0:
                    self.update_result(f"[-] '{movie}': Kunde inte hitta säljare för träffarna.\n")
                    
            except Exception as e:
                self.update_result(f"[!] Fel vid sökning av '{movie}': {e}\n")
                
            time.sleep(1) 
                
        self.root.after(0, self.status_var.set, "Status: Sammanställer resultat...")
        self.compile_results(seller_inventory, movies)

    def compile_results(self, seller_inventory, all_movies):
        matches_found = 0
        self.update_result("--- SÖKRESULTAT ---\n\n")
        
        sorted_sellers = sorted(seller_inventory.items(), key=lambda x: len(x[1]), reverse=True)
        
        for seller, movies_dict in sorted_sellers:
            if len(movies_dict) >= 1:
                matches_found += 1
                self.update_result(f"👤 SÄLJARE: {seller} (Har {len(movies_dict)} av {len(all_movies)} sökta filmer)\n")
                self.update_result("-" * 75 + "\n")
                
                for m_title, items in movies_dict.items():
                    self.update_result(f" 🎬 Sökning: '{m_title}' gav:\n")
                    for item in items:
                        clean_title = " ".join(item['title'].split())
                        # Skriver ut ✅ [Titel] (Pris: XX kr)
                        self.update_result(f"     ✅ {clean_title}  (Pris: {item['price']})   ")
                        self.insert_link("[Öppna annons]", item['url'])
                        self.update_result("\n")
                
                missing_movies = [m for m in all_movies if m not in movies_dict]
                if missing_movies:
                    self.update_result("\n ❌ Säljaren saknar följande filmer:\n")
                    for missing in missing_movies:
                        self.update_result(f"     ➔ {missing}\n")
                        
                self.update_result("\n")
                
        if matches_found == 0:
            self.update_result("Inga säljare hittades för någon av filmerna.\n")
            
        self.root.after(0, self.status_var.set, "Status: Klar!")
        self.root.after(0, self.enable_buttons)

    def enable_buttons(self):
        self.search_btn.config(state=tk.NORMAL)
        self.load_btn.config(state=tk.NORMAL)
        self.save_btn.config(state=tk.NORMAL)

    def update_result(self, text):
        def append():
            self.output_text.config(state=tk.NORMAL)
            self.output_text.insert(tk.END, text)
            self.output_text.see(tk.END)
            self.output_text.config(state=tk.DISABLED)
        self.root.after(0, append)

    def insert_link(self, text, url):
        def append(t=text, u=url):
            self.output_text.config(state=tk.NORMAL)
            
            tag_name = f"link_{uuid.uuid4().hex}"
            self.output_text.insert(tk.END, t, tag_name)
            
            self.output_text.tag_config(tag_name, foreground="#0055ff", underline=True)
            self.output_text.tag_bind(tag_name, "<Button-1>", lambda e, link=u: webbrowser.open(link))
            self.output_text.tag_bind(tag_name, "<Enter>", lambda e: self.output_text.config(cursor="hand2"))
            self.output_text.tag_bind(tag_name, "<Leave>", lambda e: self.output_text.config(cursor=""))
            
            self.output_text.see(tk.END)
            self.output_text.config(state=tk.DISABLED)
        self.root.after(0, append)

if __name__ == "__main__":
    root = tk.Tk()
    app = TraderaApp(root)
    root.mainloop()
