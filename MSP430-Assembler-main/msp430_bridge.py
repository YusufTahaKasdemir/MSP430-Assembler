import tkinter as tk
from tkinter import messagebox
import re
import os
import time
import threading

class MSP430Bridge:
    """MSP430 Assembly Converter ile simülatör arasında köprü görevi gören sınıf"""
    
    def __init__(self, memory_data=None, registers=None):
        self.memory_data = memory_data or {}
        self.registers = registers or {
            'R0': 0x0000,  # PC
            'R1': 0x0300,  # SP
            'R2': 0x0000,  # SR/CG1
            'R3': 0x0000,  # CG2
            'R4': 0x0000,
            'R5': 0x0000,
            'R6': 0x0000,
            'R7': 0x0000,
            'R8': 0x0000,
            'R9': 0x0000,
            'R10': 0x0000,
            'R11': 0x0000,
            'R12': 0x0000,
            'R13': 0x0000,
            'R14': 0x0000,
            'R15': 0x0000
        }
        self.simulator_instance = None
        self.hardware_instance = None
        self.animation_running = False
    
    def connect_simulator(self, simulator_instance):
        """Simülatör örneğiyle bağlantı kurar"""
        self.simulator_instance = simulator_instance
        return True
    
    def connect_hardware(self, hardware_instance):
        """Donanım arayüzü örneğiyle bağlantı kurar"""
        self.hardware_instance = hardware_instance
        return True
    
    def update_memory(self, memory_data):
        """Bellek verilerini günceller"""
        self.memory_data = memory_data
        
        # Simülatör bağlıysa, simülatör belleğini güncelle
        if self.simulator_instance:
            try:
                self.simulator_instance.memory = memory_data
                return True
            except Exception as e:
                print(f"Simülatör belleği güncellenirken hata: {str(e)}")
                return False
        return True
    
    def update_registers(self, registers):
        """Register değerlerini günceller"""
        self.registers = registers
        
        # Simülatör bağlıysa, simülatör registerlarını güncelle
        if self.simulator_instance:
            try:
                self.simulator_instance.register_values = registers
                return True
            except Exception as e:
                print(f"Simülatör registerleri güncellenirken hata: {str(e)}")
                return False
        return True
    
    def send_to_simulator(self, force_update=False):
        """Verileri simülatöre gönderir"""
        if not self.simulator_instance:
            return False
            
        try:
            # Bellek ve register verilerini güncelle
            self.simulator_instance.memory = self.memory_data
            self.simulator_instance.register_values = self.registers
            
            # Simülasyonu başlat/durma izni ver
            if force_update and hasattr(self.simulator_instance, 'write_to_terminal'):
                self.simulator_instance.write_to_terminal("Assembly kodundan yeni veriler alındı.")
                
                # Simülasyon çalışıyorsa durdur ve yeniden başlat
                if hasattr(self.simulator_instance, 'running') and self.simulator_instance.running:
                    self.simulator_instance.stop_simulation()
                    time.sleep(0.5)
                    self.simulator_instance.start_simulation()
                
            return True
            
        except Exception as e:
            print(f"Veriler simülatöre gönderilirken hata: {str(e)}")
            return False
    
    def send_to_hardware(self, hex_data):
        """Hex verilerini gerçek donanıma gönderir"""
        if not self.hardware_instance:
            return False
            
        try:
            # Geçici hex dosyası oluştur
            temp_hex_file = os.path.join(os.path.dirname(__file__), "temp_upload.hex")
            
            with open(temp_hex_file, "w") as f:
                f.write(hex_data)
            
            # Donanıma gönder
            if hasattr(self.hardware_instance, 'hardware') and hasattr(self.hardware_instance.hardware, 'upload_code'):
                return self.hardware_instance.hardware.upload_code(temp_hex_file)
                
            return False
            
        except Exception as e:
            print(f"Veriler donanıma gönderilirken hata: {str(e)}")
            return False
    
    def visualize_data_flow(self, parent, from_addr, to_addr, data_value):
        """Veri akışını görselleştiren animasyon oluşturur"""
        if self.animation_running:
            return
            
        self.animation_running = True
        
        # Animasyon penceresi
        animation_window = tk.Toplevel(parent)
        animation_window.title("Veri Akışı Görselleştirme")
        animation_window.geometry("600x300")
        animation_window.configure(bg="#0a0a0a")
        
        # Başlık
        title_label = tk.Label(animation_window, 
                             text="MSP430 Veri Akışı", 
                             font=("Impact", 18), 
                             bg="#0a0a0a", 
                             fg="#ffffff")
        title_label.pack(pady=10)
        
        # Animasyon canvas
        canvas = tk.Canvas(animation_window, width=560, height=200, bg="#0a0a0a", highlightthickness=0)
        canvas.pack(pady=10)
        
        # İki kutucuk çiz - bellek ve register
        mem_box = canvas.create_rectangle(50, 70, 150, 130, fill="#1a1a1a", outline="#4CAF50", width=2)
        reg_box = canvas.create_rectangle(410, 70, 510, 130, fill="#1a1a1a", outline="#2196F3", width=2)
        
        # Kutucuk etiketleri
        canvas.create_text(100, 50, text=f"Bellek: 0x{from_addr:04X}", fill="#ffffff", font=("Arial", 10))
        canvas.create_text(460, 50, text=f"Register: R{to_addr}", fill="#ffffff", font=("Arial", 10))
        
        # Değer etiketleri
        mem_value = canvas.create_text(100, 100, text=f"0x{data_value:04X}", fill="#4CAF50", font=("Courier New", 14, "bold"))
        reg_value = canvas.create_text(460, 100, text="????", fill="#2196F3", font=("Courier New", 14, "bold"))
        
        # Ok çiz
        arrow = canvas.create_line(150, 100, 410, 100, fill="#ff5722", width=3, arrow=tk.LAST)
        
        # Hareket eden veri noktası
        data_point = canvas.create_oval(140, 95, 150, 105, fill="#ff5722", outline="#ffffff")
        
        # Durum etiketi
        status_label = tk.Label(animation_window, 
                              text="Veri aktarılıyor...", 
                              font=("Arial", 10), 
                              bg="#0a0a0a", 
                              fg="#aaaaaa")
        status_label.pack(pady=5)
        
        # Animasyon fonksiyonu
        def animate():
            x = 140
            
            # İleri hareket
            while x < 400 and animation_window.winfo_exists():
                try:
                    canvas.coords(data_point, x, 95, x+10, 105)
                    canvas.update()
                    x += 5
                    time.sleep(0.03)
                except:
                    break
            
            # Hedefe ulaşıldı - register değerini güncelle
            try:
                if animation_window.winfo_exists():
                    canvas.itemconfig(reg_value, text=f"0x{data_value:04X}")
                    status_label.config(text="Veri aktarımı tamamlandı!")
                    time.sleep(1)
                    
                    if animation_window.winfo_exists():
                        animation_window.destroy()
            except:
                pass
                
            self.animation_running = False
        
        # Thread içinde çalıştır
        threading.Thread(target=animate, daemon=True).start()
    
    def highlight_execution(self, parent, line_number, instruction):
        """Kod yürütme işlemini görselleştiren animasyon oluşturur"""
        if self.animation_running:
            return
            
        self.animation_running = True
        
        # Animasyon penceresi
        animation_window = tk.Toplevel(parent)
        animation_window.title("Kod Yürütme Görselleştirme")
        animation_window.geometry("500x280")
        animation_window.configure(bg="#0a0a0a")
        
        # Başlık
        title_label = tk.Label(animation_window, 
                             text="MSP430 Kod Yürütme", 
                             font=("Impact", 18), 
                             bg="#0a0a0a", 
                             fg="#ffffff")
        title_label.pack(pady=10)
        
        # Kod görüntüleme alanı
        code_frame = tk.Frame(animation_window, bg="#1a1a1a", bd=1, relief=tk.SUNKEN)
        code_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Kod satırları
        for i in range(max(1, line_number-2), line_number+3):
            bg_color = "#2d2d2d" if i == line_number else "#1a1a1a"
            fg_color = "#ff5722" if i == line_number else "#ffffff"
            font_style = ("Courier New", 12, "bold") if i == line_number else ("Courier New", 12)
            
            line_frame = tk.Frame(code_frame, bg=bg_color)
            line_frame.pack(fill=tk.X)
            
            line_num = tk.Label(line_frame, 
                              text=f"{i:4d}:", 
                              font=("Courier New", 12), 
                              bg=bg_color, 
                              fg="#aaaaaa",
                              width=6, 
                              anchor=tk.E)
            line_num.pack(side=tk.LEFT, padx=(5, 0))
            
            code_text = instruction if i == line_number else f"// Örnek kod satırı {i}"
            code_label = tk.Label(line_frame, 
                                text=code_text, 
                                font=font_style, 
                                bg=bg_color, 
                                fg=fg_color,
                                anchor=tk.W,
                                padx=5)
            code_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Yürütme işareti
        indicator_frame = tk.Frame(animation_window, bg="#0a0a0a")
        indicator_frame.pack(fill=tk.X, padx=20, pady=10)
        
        indicator_label = tk.Label(indicator_frame, 
                                 text="Yürütülüyor:", 
                                 font=("Arial", 10), 
                                 bg="#0a0a0a", 
                                 fg="#ffffff")
        indicator_label.pack(side=tk.LEFT, padx=(0, 10))
        
        indicator_value = tk.Label(indicator_frame, 
                                 text=instruction, 
                                 font=("Courier New", 12, "bold"), 
                                 bg="#0a0a0a", 
                                 fg="#ff5722")
        indicator_value.pack(side=tk.LEFT)
        
        # Durum etiketi
        status_frame = tk.Frame(animation_window, bg="#0a0a0a")
        status_frame.pack(fill=tk.X, padx=20, pady=10)
        
        status_label = tk.Label(status_frame, 
                              text="İşlem yürütülüyor...", 
                              font=("Arial", 10), 
                              bg="#0a0a0a", 
                              fg="#aaaaaa")
        status_label.pack(side=tk.LEFT)
        
        # Animasyon fonksiyonu
        def animate():
            try:
                # İşlem süresi simülasyonu
                time.sleep(1.5)
                
                if animation_window.winfo_exists():
                    status_label.config(text="İşlem tamamlandı!")
                    time.sleep(0.8)
                
                if animation_window.winfo_exists():
                    animation_window.destroy()
            except:
                pass
                
            self.animation_running = False
        
        # Thread içinde çalıştır
        threading.Thread(target=animate, daemon=True).start()


# Bağımsız test için
if __name__ == "__main__":
    # Test verileri
    memory_data = {
        0x2000: 0x1234,
        0x2002: 0x5678,
        0x2004: 0x9ABC,
        0x2006: 0xDEF0
    }
    
    registers = {
        'R0': 0x0000,
        'R1': 0x0300,
        'R2': 0x0000,
        'R3': 0x0000,
        'R4': 0x1234,
        'R5': 0x5678,
        'R6': 0x0000,
        'R7': 0x0000,
        'R8': 0x0000,
        'R9': 0x0000,
        'R10': 0x0000,
        'R11': 0x0000,
        'R12': 0x0000,
        'R13': 0x0000,
        'R14': 0x0000,
        'R15': 0x0000
    }
    
    # Bridge örneği
    bridge = MSP430Bridge(memory_data, registers)
    
    # Test için basit GUI
    root = tk.Tk()
    root.title("MSP430 Bridge Test")
    root.geometry("400x300")
    root.configure(bg="#1e1e1e")
    
    # Test butonları
    tk.Button(root, 
            text="Veri Akışı Animasyonu", 
            command=lambda: bridge.visualize_data_flow(root, 0x2000, 4, 0x1234)).pack(pady=10)
    
    tk.Button(root, 
            text="Kod Yürütme Animasyonu", 
            command=lambda: bridge.highlight_execution(root, 10, "MOV.W #0x1234, R4")).pack(pady=10)
    
    root.mainloop()