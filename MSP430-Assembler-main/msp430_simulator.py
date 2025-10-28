import tkinter as tk
from tkinter import Canvas, Frame, Label, Button
import math
import random
import time
import threading

class MSP430Simulator:
    """MSP430 kartını görsel olarak simüle eden sınıf"""
    
    def __init__(self, parent):
        self.parent = parent
        self.running = False
        self.led_states = [False] * 8  # 8 LED durumu
        self.register_values = {
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
        self.memory = {}  # Bellek simülasyonu
        
        # pencere kontrolü
        self.window = parent
        if not isinstance(parent, tk.Toplevel) and not isinstance(parent, tk.Tk):
            # Eğer parent bir pencere değilse, yeni bir pencere oluştur
            self.window = tk.Toplevel(parent)
        
        # Pencere ayarları
        if hasattr(self.window, 'title'):
            self.window.title("MSP430 Donanım Simülatörü") 
        if hasattr(self.window, 'geometry'):
            self.window.geometry("1000x800")
        if hasattr(self.window, 'configure'):
            self.window.configure(bg="#0a0a0a")
        
        # Başlık
        self.title_label = tk.Label(self.window, 
                                  text="MSP430 LaunchPad Simülatörü", 
                                  font=("Impact", 24), 
                                  bg="#0a0a0a", 
                                  fg="#ffffff")
        self.title_label.pack(pady=15)
        
        # Ana çerçeve
        self.main_frame = tk.Frame(self.window, bg="#0a0a0a")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Kart çerçevesi
        self.board_frame = tk.Frame(self.main_frame, bg="#222222", bd=2, relief=tk.RAISED)
        self.board_frame.pack(pady=20)
        
        # Kart kanvası
        self.board_canvas = Canvas(self.board_frame, 
                                 width=600, 
                                 height=400, 
                                 bg="#0a6522",  # Devre kartı yeşili
                                 highlightthickness=0)
        self.board_canvas.pack(padx=10, pady=10)
        
        # Microcontroller çipi çiz
        self.draw_mcu_chip()
        
        # LEDleri çiz
        self.led_objects = []
        self.draw_leds()
        
        # Butonları çiz
        self.draw_buttons()
        
        # Terminal ve durum paneli
        self.create_terminal()
        
        # Kontrol paneli
        self.create_control_panel()
        
        # Simülasyon zamanlayıcısı
        self.clock_thread = None
        self.stop_flag = threading.Event()
        
        # Pencere kapatılınca simülasyonu durdur
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def draw_mcu_chip(self):
        """MCU çipini çizer"""
        # Çip gövdesi
        self.board_canvas.create_rectangle(240, 180, 360, 280, 
                                        fill="#1a1a1a", 
                                        outline="#000000", 
                                        width=2)
        
        # Çip pinleri
        for i in range(10):
            # Sol pinler
            pin_y = 190 + i * 10
            self.board_canvas.create_line(230, pin_y, 240, pin_y, 
                                       fill="#cdcdcd", 
                                       width=2)
            
            # Sağ pinler
            self.board_canvas.create_line(360, pin_y, 370, pin_y, 
                                       fill="#cdcdcd", 
                                       width=2)
        
        # Çip işareti
        self.board_canvas.create_text(300, 230, 
                                    text="MSP430", 
                                    fill="#ffffff", 
                                    font=("Courier New", 12, "bold"))
        
        # Yarıçap işareti
        self.board_canvas.create_oval(245, 185, 255, 195, 
                                    fill="#1a1a1a", 
                                    outline="#ffffff")
    
    def draw_leds(self):
        """LED'leri çizer"""
        for i in range(8):
            x = 100 + i * 50
            y = 350
            
            # LED gövdesi
            led = self.board_canvas.create_oval(x-10, y-10, x+10, y+10, 
                                             fill="#321b1b",  # Kapalı LED rengi
                                             outline="#000000", 
                                             width=1,
                                             tags=f"led{i}")
            
            # LED bağlantı çizgileri
            self.board_canvas.create_line(x, y+10, x, y+30, 
                                       fill="#cdcdcd", 
                                       width=1)
            
            # LED etiketi
            self.board_canvas.create_text(x, y+40, 
                                       text=f"LED{i}", 
                                       fill="#ffffff", 
                                       font=("Arial", 8))
            
            self.led_objects.append(led)
    
    def draw_buttons(self):
        """Fiziksel butonları çizer"""
        # Reset butonu
        reset_x, reset_y = 450, 150
        self.reset_button_obj = self.board_canvas.create_oval(
            reset_x-15, reset_y-15, reset_x+15, reset_y+15,
            fill="#d32f2f",
            outline="#000000",
            width=2,
            tags="reset_button"
        )
        self.board_canvas.create_text(reset_x, reset_y, 
                                   text="RST", 
                                   fill="#ffffff", 
                                   font=("Arial", 8, "bold"))
        
        # Kullanıcı butonu
        user_x, user_y = 450, 250
        self.user_button_obj = self.board_canvas.create_oval(
            user_x-15, user_y-15, user_x+15, user_y+15,
            fill="#2e7d32",
            outline="#000000",
            width=2,
            tags="user_button"
        )
        self.board_canvas.create_text(user_x, user_y, 
                                   text="USR", 
                                   fill="#ffffff", 
                                   font=("Arial", 8, "bold"))
        
        # Butonlara tıklama olayları
        self.board_canvas.tag_bind("reset_button", "<Button-1>", self.reset_button_press)
        self.board_canvas.tag_bind("user_button", "<Button-1>", self.user_button_press)
    
    def create_terminal(self):
        """Terminal ve durum panelini oluşturur"""
        # Terminal çerçevesi
        self.terminal_frame = tk.LabelFrame(self.window, 
                                          text="Terminal", 
                                          font=("Arial", 10, "bold"), 
                                          bg="#0a0a0a", 
                                          fg="#ffffff")
        self.terminal_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Terminal metni
        self.terminal_text = tk.Text(self.terminal_frame, 
                                   width=80, 
                                   height=6, 
                                   bg="#000000", 
                                   fg="#00ff00", 
                                   font=("Consolas", 10))
        self.terminal_text.pack(padx=10, pady=10, fill=tk.X)
        
        # Terminal başlangıç metni
        self.write_to_terminal("MSP430 LaunchPad Simülatörü başlatıldı.")
        self.write_to_terminal("READY >")
    
    def create_control_panel(self):
        """Kontrol panelini oluşturur"""
        # Kontrol çerçevesi
        self.control_frame = tk.Frame(self.main_frame, bg="#222222", bd=2, relief=tk.RAISED)
        self.control_frame.pack(pady=20, fill=tk.X)
        
        # Simülasyon başlatma butonu
        self.start_button = tk.Button(self.control_frame, 
                                    text="Simülasyonu Başlat", 
                                    font=("Arial", 12, "bold"),
                                    bg="#4CAF50", 
                                    fg="white",
                                    command=self.start_simulation,
                                    padx=20,
                                    pady=10)
        self.start_button.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Simülasyon durdurma butonu
        self.stop_button = tk.Button(self.control_frame, 
                                   text="Simülasyonu Durdur", 
                                   font=("Arial", 12, "bold"),
                                   bg="#F44336", 
                                   fg="white",
                                   command=self.stop_simulation,
                                   padx=20,
                                   pady=10)
        self.stop_button.pack(side=tk.LEFT, padx=20, pady=10)
        
        # LED Kontrolleri
        self.led_frame = tk.Frame(self.control_frame, bg="#222222")
        self.led_frame.pack(side=tk.RIGHT, padx=20, pady=10)
        
        tk.Label(self.led_frame, text="LED Kontrolleri:", bg="#222222", fg="white", font=("Arial", 11)).pack(anchor=tk.W)
        
        # LED test butonları 
        self.led_test_button = tk.Button(self.led_frame, 
                                      text="LED Test", 
                                      bg="#2196F3", 
                                      fg="white", 
                                      font=("Arial", 10, "bold"),
                                      command=self.test_leds,
                                      padx=10,
                                      pady=5)
        self.led_test_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # LED'leri temizle butonu
        self.clear_leds_button = tk.Button(self.led_frame, 
                                        text="LED'leri Kapat", 
                                        bg="#607D8B", 
                                        fg="white", 
                                        font=("Arial", 10, "bold"),
                                        command=self.clear_leds,
                                        padx=10,
                                        pady=5)
        self.clear_leds_button.pack(side=tk.LEFT, padx=5, pady=5)
    
    def start_simulation(self):
        """Simülasyonu başlatır"""
        if not self.running:
            self.running = True
            self.write_to_terminal("Simülasyon başlatılıyor...")
            
            # Buton durumlarını güncelle
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            
            # Durdurma bayrağını temizle
            self.stop_flag.clear()
            
            # Simülasyon thread'ini başlat
            self.clock_thread = threading.Thread(target=self.simulation_loop)
            self.clock_thread.daemon = True
            self.clock_thread.start()
    
    def stop_simulation(self):
        """Simülasyonu durdurur"""
        if self.running:
            self.running = False
            self.write_to_terminal("Simülasyon durduruluyor...")
            
            # Durdurma bayrağını ayarla
            self.stop_flag.set()
            
            # Buton durumlarını güncelle
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
    
    def simulation_loop(self):
        """Simülasyon ana döngüsü"""
        while self.running and not self.stop_flag.is_set():
            # MCU simülasyonu - Burada basit bir LED yanıp sönme simülasyonu yapıyoruz
            # Gerçek bir uygulama daha karmaşık simülasyonlar içerebilir
            
            # Rastgele LED'leri aç/kapa
            led_index = random.randint(0, 7)
            self.toggle_led(led_index)
            
            # Rastgele register değerlerini değiştir
            reg = f"R{random.randint(4, 15)}"
            self.register_values[reg] = random.randint(0, 0xFFFF)
            
            # Terminal çıktısı
            if random.random() < 0.2:  # %20 olasılıkla mesaj yaz
                messages = [
                    "İşlem yürütülüyor...",
                    f"Register {reg} değeri: 0x{self.register_values[reg]:04X}",
                    f"LED{led_index} durumu değiştirildi.",
                    "Bellek adresi 0x0100 okunuyor...",
                    "I/O portu yapılandırılıyor...",
                    "Zamanlayıcı güncellendi."
                ]
                self.write_to_terminal(random.choice(messages))
            
            # Simülasyon hızı
            time.sleep(0.5)
        
        self.write_to_terminal("Simülasyon durduruldu.")
    
    def toggle_led(self, index):
        """Belirtilen LED'i aç/kapa"""
        if 0 <= index < 8:
            self.led_states[index] = not self.led_states[index]
            
            # LED rengini güncelle
            if self.led_states[index]:
                self.board_canvas.itemconfig(self.led_objects[index], fill="#ff0000")  # Açık
            else:
                self.board_canvas.itemconfig(self.led_objects[index], fill="#321b1b")  # Kapalı
    
    def test_leds(self):
        """Tüm LED'leri test için yakıp söndürür"""
        self.write_to_terminal("LED testi başlatılıyor...")
        
        # Tüm LED'leri sırayla aç
        def sequence():
            for i in range(8):
                self.led_states[i] = True
                self.board_canvas.itemconfig(self.led_objects[i], fill="#ff0000")
                self.window.update()
                time.sleep(0.1)
            
            time.sleep(0.5)
            
            # Tüm LED'leri sırayla kapat
            for i in range(8):
                self.led_states[i] = False
                self.board_canvas.itemconfig(self.led_objects[i], fill="#321b1b")
                self.window.update()
                time.sleep(0.1)
            
            self.write_to_terminal("LED testi tamamlandı.")
        
        # Thread olarak çalıştır
        threading.Thread(target=sequence, daemon=True).start()
    
    def clear_leds(self):
        """Tüm LED'leri kapatır"""
        for i in range(8):
            self.led_states[i] = False
            self.board_canvas.itemconfig(self.led_objects[i], fill="#321b1b")
        
        self.write_to_terminal("Tüm LED'ler kapatıldı.")
    
    def reset_button_press(self, event):
        """Reset butonuna basıldığında"""
        # Görsel efekt
        self.board_canvas.itemconfig(self.reset_button_obj, fill="#ff6659")
        self.window.after(100, lambda: self.board_canvas.itemconfig(self.reset_button_obj, fill="#d32f2f"))
        
        # İşlevi
        self.write_to_terminal("RESET butonu basıldı. Sistem yeniden başlatılıyor...")
        
        # Tüm LED'leri kapat
        self.clear_leds()
        
        # Register değerlerini sıfırla
        for reg in self.register_values:
            if reg == "R1":  # SP
                self.register_values[reg] = 0x0300
            else:
                self.register_values[reg] = 0x0000
        
        self.write_to_terminal("Sistem yeniden başlatıldı.")
    
    def user_button_press(self, event):
        """Kullanıcı butonuna basıldığında"""
        # Görsel efekt
        self.board_canvas.itemconfig(self.user_button_obj, fill="#60ad5e")
        self.window.after(100, lambda: self.board_canvas.itemconfig(self.user_button_obj, fill="#2e7d32"))
        
        # İşlevi - örneğin ilk LED'i aç/kapat
        self.toggle_led(0)
        self.write_to_terminal("Kullanıcı butonu basıldı. LED0 durumu değiştirildi.")
    
    def write_to_terminal(self, message):
        """Terminal penceresine mesaj yazar"""
        timestamp = time.strftime("%H:%M:%S")
        self.terminal_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.terminal_text.see(tk.END)  # Otomatik kaydır
    
    def on_close(self):
        """Pencere kapatıldığında simülasyonu durdur"""
        self.stop_simulation()
        self.window.destroy()


# Bağımsız test için
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Ana pencereyi gizle
    
    simulator = MSP430Simulator(root)
    
    root.mainloop()