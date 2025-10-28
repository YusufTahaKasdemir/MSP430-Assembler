import serial
import serial.tools.list_ports
import time
import os
import subprocess
import tkinter as tk
from tkinter import messagebox, filedialog, ttk

class MSP430Hardware:
    """MSP430 donanımıyla iletişim kurmak için sınıf"""
    
    def __init__(self, status_callback=None):
        self.serial_port = None
        self.connected = False
        self.device_path = None
        self.baud_rate = 9600  # Varsayılan baud rate
        self.status_callback = status_callback
        self.device_info = {}
        
    def find_msp430_devices(self):
        """Sisteme bağlı MSP430 cihazlarını bulur"""
        devices = []
        ports = serial.tools.list_ports.comports()
        
        for port in ports:
            # MSP430 kartları genellikle "MSP430" veya "Texas Instruments" olarak tanınır
            # Bu filtrelemeyi gerçek cihazlarınıza göre ayarlayın
            if "MSP430" in port.description or "Texas Instruments" in port.description:
                devices.append({
                    'port': port.device,
                    'description': port.description,
                    'hwid': port.hwid
                })
            # MSP430 Launchpad'ler genellikle FT232 UART çipi kullanır
            elif "FT232" in port.description:
                devices.append({
                    'port': port.device,
                    'description': port.description,
                    'hwid': port.hwid
                })
        
        return devices
    
    def list_all_serial_ports(self):
        """Tüm seri portları listeler"""
        return [
            {
                'port': port.device,
                'description': port.description,
                'hwid': port.hwid
            }
            for port in serial.tools.list_ports.comports()
        ]
    
    def connect(self, port, baud_rate=9600):
        """Belirlenen porta bağlanır"""
        try:
            self.serial_port = serial.Serial(port, baud_rate, timeout=1)
            self.connected = True
            self.device_path = port
            self.baud_rate = baud_rate
            
            # Bağlantı bilgilerini kaydet
            self.device_info = {
                'port': port,
                'baud_rate': baud_rate,
                'connection_time': time.ctime()
            }
            
            self._update_status(f"MSP430 cihazına bağlandı: {port}")
            return True
            
        except serial.SerialException as e:
            self._update_status(f"Bağlantı hatası: {str(e)}")
            return False
    
    def disconnect(self):
        """Bağlantıyı kapatır"""
        if self.serial_port and self.connected:
            self.serial_port.close()
            self.connected = False
            self._update_status("MSP430 cihazından bağlantı kesildi")
            return True
        return False
    
    def upload_code(self, hex_file_path):
        """Derlenmiş hex dosyasını MSP430'a yükler"""
        # Gerçek uygulamada, MSP-FET veya MSP430 Flasher gibi programları
        # çağırmak gerekebilir. Burada basit bir simülasyon yapıyoruz.
        
        if not os.path.exists(hex_file_path):
            self._update_status(f"Hata: Dosya bulunamadı: {hex_file_path}")
            return False
            
        self._update_status(f"Kod yükleniyor: {hex_file_path}")
        
        try:
            # Gerçek uygulamada aşağıdaki komutu uygun MSP430 programlayıcı komutuyla değiştirin
            # Örnek: mspdebug rf2500 "prog {hex_file_path}"
            # Şimdilik sadece simülasyon yapıyoruz
            
            time.sleep(2)  # Yükleme simülasyonu
            self._update_status("Kod başarıyla yüklendi!")
            return True
            
        except Exception as e:
            self._update_status(f"Kod yükleme hatası: {str(e)}")
            return False
    
    def reset_device(self):
        """MSP430 cihazını resetler"""
        if not self.connected:
            self._update_status("Hata: Cihaza bağlı değil")
            return False
            
        try:
            # Gerçek bir implementasyonda DTR/RTS pinleri manipüle edilebilir
            # veya özel reset komutu gönderilebilir
            self.serial_port.setDTR(False)
            time.sleep(0.1)
            self.serial_port.setDTR(True)
            
            self._update_status("Cihaz resetlendi")
            return True
            
        except Exception as e:
            self._update_status(f"Reset hatası: {str(e)}")
            return False
    
    def read_data(self, num_bytes=100):
        """Cihazdan veri okur"""
        if not self.connected:
            self._update_status("Hata: Cihaza bağlı değil")
            return None
            
        try:
            data = self.serial_port.read(num_bytes)
            return data
            
        except Exception as e:
            self._update_status(f"Veri okuma hatası: {str(e)}")
            return None
    
    def send_command(self, command):
        """Cihaza komut gönderir"""
        if not self.connected:
            self._update_status("Hata: Cihaza bağlı değil")
            return False
            
        try:
            self.serial_port.write(command.encode())
            return True
            
        except Exception as e:
            self._update_status(f"Komut gönderme hatası: {str(e)}")
            return False
    
    def get_device_status(self):
        """Cihaz durumunu sorgular"""
        status = {
            'connected': self.connected,
            'port': self.device_path,
            'baud_rate': self.baud_rate,
            'info': self.device_info
        }
        
        if self.connected:
            try:
                # Burada gerçek bir cihaz sorgusu yapılabilir
                status['online'] = True
            except:
                status['online'] = False
        
        return status
    
    def _update_status(self, message):
        """Durum güncellemelerini callback ile iletir"""
        if self.status_callback:
            self.status_callback(message)
        print(f"MSP430 Donanım: {message}")


class HardwareInterface:
    """MSP430 donanım arayüzü"""
    
    def __init__(self, parent):
        self.parent = parent
        self.hardware = MSP430Hardware(self.update_status)
        self.status_messages = []
        
        # Ana pencere
        self.window = tk.Toplevel(parent)
        self.window.title("MSP430 Hardware Interface")
        self.window.geometry("800x600")
        self.window.configure(bg="#1e1e1e")
        
        # Üst frame - başlık ve temel bilgiler
        self.top_frame = tk.Frame(self.window, bg="#1e1e1e")
        self.top_frame.pack(fill=tk.X, padx=15, pady=10)
        
        self.title_label = tk.Label(self.top_frame, 
                                   text="MSP430 Hardware Control Panel", 
                                   font=("Impact", 16), 
                                   bg="#1e1e1e", 
                                   fg="#ffffff")
        self.title_label.pack(pady=5)
        
        self.status_label = tk.Label(self.top_frame, 
                                    text="Status: Not connected", 
                                    font=("Arial", 10), 
                                    bg="#1e1e1e", 
                                    fg="#aaaaaa")
        self.status_label.pack(pady=5)
        
        # Orta frame - ekran ve kontroller
        self.main_frame = tk.Frame(self.window, bg="#1e1e1e")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        
        # Sol panel - cihaz listesi ve kontroller
        self.left_panel = tk.Frame(self.main_frame, bg="#2d2d2d", width=250)
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        self.left_panel.pack_propagate(False)
        
        # Cihaz başlığı
        self.devices_title = tk.Label(self.left_panel, 
                                    text="Devices", 
                                    font=("Arial", 11, "bold"), 
                                    bg="#2d2d2d", 
                                    fg="#ffffff")
        self.devices_title.pack(pady=10, padx=5, anchor=tk.W)
        
        # Cihaz listesi
        self.devices_frame = tk.Frame(self.left_panel, bg="#2d2d2d")
        self.devices_frame.pack(fill=tk.X, padx=5)
        
        self.device_listbox = tk.Listbox(self.devices_frame, 
                                       bg="#121212", 
                                       fg="#ffffff", 
                                       height=12, 
                                       font=("Courier New", 10))
        self.device_listbox.pack(fill=tk.X, padx=5, pady=5)
        
        # Yenile butonu
        self.refresh_button = tk.Button(self.devices_frame, 
                                       text="Refresh Devices", 
                                       bg="#ff5722", 
                                       fg="#ffffff", 
                                       font=("Arial", 10), 
                                       command=self.refresh_devices)
        self.refresh_button.pack(fill=tk.X, padx=5, pady=5)
        
        # Bağlan butonu
        self.connect_button = tk.Button(self.devices_frame, 
                                      text="Connect", 
                                      bg="#4CAF50", 
                                      fg="#ffffff",
                                      disabledforeground="#ffffff", 
                                      font=("Arial", 10), 
                                      command=self.connect_to_selected)
        self.connect_button.pack(fill=tk.X, padx=5, pady=5)
        
        # Bağlantıyı Kes butonu
        self.disconnect_button = tk.Button(self.devices_frame, 
                                         text="Disconnect", 
                                         bg="#f44336", 
                                         fg="#ffffff",
                                         disabledforeground="#ffffff", 
                                         font=("Arial", 10), 
                                         command=self.disconnect)
        self.disconnect_button.pack(fill=tk.X, padx=5, pady=5)
        
        # Sağ panel - kod yükleme ve izleme
        self.right_panel = tk.Frame(self.main_frame, bg="#1e1e1e")
        self.right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Kod yükleme kısmı
        self.upload_frame = tk.LabelFrame(self.right_panel, 
                                        text="Upload Code", 
                                        bg="#1e1e1e", 
                                        fg="#ffffff", 
                                        font=("Arial", 10))
        self.upload_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Dosya seçme
        self.file_frame = tk.Frame(self.upload_frame, bg="#1e1e1e")
        self.file_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.file_label = tk.Label(self.file_frame, 
                                  text="Hex File:", 
                                  bg="#1e1e1e", 
                                  fg="#ffffff", 
                                  font=("Arial", 10))
        self.file_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.file_entry = tk.Entry(self.file_frame, 
                                 bg="#121212", 
                                 fg="#ffffff", 
                                 font=("Courier New", 10), 
                                 width=40)
        self.file_entry.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        
        self.browse_button = tk.Button(self.file_frame, 
                                     text="Browse", 
                                     bg="#ff5722", 
                                     fg="#ffffff", 
                                     font=("Arial", 10), 
                                     command=self.browse_hex_file)
        self.browse_button.pack(side=tk.LEFT)
        
        # Yükleme butonu
        self.upload_button = tk.Button(self.upload_frame, 
                                     text="Upload Code", 
                                     bg="#4CAF50", 
                                     fg="#ffffff",
                                     disabledforeground="#ffffff", 
                                     font=("Arial", 10), 
                                     command=self.upload_code)
        self.upload_button.pack(fill=tk.X, padx=5, pady=5)
        
        # Reset butonu
        self.reset_button = tk.Button(self.upload_frame, 
                                    text="Reset Device", 
                                    bg="#ff9800", 
                                    fg="#ffffff",
                                    disabledforeground="#ffffff", 
                                    font=("Arial", 10), 
                                    command=self.reset_device)
        self.reset_button.pack(fill=tk.X, padx=5, pady=5)
        
        # İzleme kısmı
        self.monitoring_frame = tk.LabelFrame(self.right_panel, 
                                           text="Device Monitoring", 
                                           bg="#1e1e1e", 
                                           fg="#ffffff", 
                                           font=("Arial", 10))
        self.monitoring_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Durum mesajları
        self.monitoring_text = tk.Text(self.monitoring_frame, 
                                     bg="#121212", 
                                     fg="#ffffff", 
                                     font=("Courier New", 10), 
                                     height=10)
        self.monitoring_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Veri gönderme
        self.send_frame = tk.Frame(self.monitoring_frame, bg="#1e1e1e")
        self.send_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.send_label = tk.Label(self.send_frame, 
                                  text="Command:", 
                                  bg="#1e1e1e", 
                                  fg="#ffffff", 
                                  font=("Arial", 10))
        self.send_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.send_entry = tk.Entry(self.send_frame, 
                                 bg="#121212", 
                                 fg="#ffffff", 
                                 font=("Courier New", 10))
        self.send_entry.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        
        self.send_button = tk.Button(self.send_frame, 
                                   text="Send", 
                                   bg="#2196F3", 
                                   fg="#ffffff",
                                   disabledforeground="#ffffff", 
                                   font=("Arial", 10), 
                                   command=self.send_command)
        self.send_button.pack(side=tk.LEFT)
        
        # Alt durum çubuğu
        self.status_bar = tk.Frame(self.window, bg="#2d2d2d", height=25)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_text = tk.Label(self.status_bar, 
                                   text="Ready", 
                                   bg="#2d2d2d", 
                                   fg="#aaaaaa", 
                                   font=("Arial", 9), 
                                   anchor=tk.W)
        self.status_text.pack(side=tk.LEFT, padx=10)
        
        # Bağlantı zamanı
        self.time_label = tk.Label(self.status_bar, 
                                  text="Connection time: 00:00:00", 
                                  bg="#2d2d2d", 
                                  fg="#aaaaaa", 
                                  font=("Arial", 9))
        self.time_label.pack(side=tk.RIGHT, padx=10)
        
        # Pencere kapatılınca bağlantıyı kes
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Başlangıçta cihazları listele
        self.refresh_devices()
        
        # Bağlantı durumuna göre UI güncelleme
        self.update_ui_state()
    
    def refresh_devices(self):
        """Bağlı cihazları yeniler"""
        self.device_listbox.delete(0, tk.END)
        
        # MSP430 cihazlarını ara
        msp_devices = self.hardware.find_msp430_devices()
        
        if msp_devices:
            for device in msp_devices:
                self.device_listbox.insert(tk.END, f"{device['port']} - {device['description']}")
            
            self.update_status(f"{len(msp_devices)} MSP430 device(s) found")
        else:
            # MSP430 yoksa tüm seri portları göster
            all_ports = self.hardware.list_all_serial_ports()
            
            if all_ports:
                for port in all_ports:
                    self.device_listbox.insert(tk.END, f"{port['port']} - {port['description']}")
                
                self.update_status("No MSP430 device found. Listing all serial ports.")
            else:
                self.update_status("No serial ports found!")
    
    def connect_to_selected(self):
        """Seçili cihaza bağlanır"""
        selection = self.device_listbox.curselection()
        
        if not selection:
            messagebox.showwarning("Warning", "Please select a device")
            return
            
        selected_text = self.device_listbox.get(selection[0])
        port = selected_text.split(" - ")[0]
        
        if self.hardware.connect(port):
            self.update_status(f"Connected to port {port}")
            self.update_ui_state(True)
            self.start_connection_timer()
        else:
            messagebox.showerror("Connection Error", f"Could not connect to port {port}")
    
    def disconnect(self):
        """Bağlantıyı keser"""
        if self.hardware.disconnect():
            self.update_status("Disconnected")
            self.update_ui_state(False)
    
    def browse_hex_file(self):
        """Hex dosyası seçim diyaloğu"""
        file_path = filedialog.askopenfilename(
            title="Select Hex File",
            filetypes=[("Hex files", "*.hex"), ("All files", "*.*")]
        )
        
        if file_path:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)
    
    def upload_code(self):
        """Seçilen hex dosyasını cihaza yükler"""
        file_path = self.file_entry.get()
        
        if not file_path:
            messagebox.showwarning("Warning", "Please select a hex file")
            return
            
        if not self.hardware.connected:
            messagebox.showwarning("Warning", "Please connect to a device first")
            return
        
        self.update_status(f"Uploading code: {file_path}")
        
        # Yükleme işlemi için yükleme animasyonu başlat
        self.upload_button.config(text="Uploading...", state=tk.DISABLED, disabledforeground="#ffffff")
        
        # Gerçek yükleme işlemi
        if self.hardware.upload_code(file_path):
            messagebox.showinfo("Success", "Code uploaded successfully!")
        else:
            messagebox.showerror("Error", "An error occurred while uploading the code")
        
        # UI'ı sıfırla
        self.upload_button.config(text="Upload Code", state=tk.NORMAL)
    
    def reset_device(self):
        """Cihazı resetler"""
        if not self.hardware.connected:
            messagebox.showwarning("Warning", "Please connect to a device first")
            return
            
        if self.hardware.reset_device():
            self.update_status("Device reset completed")
    
    def send_command(self):
        """Cihaza komut gönderir"""
        if not self.hardware.connected:
            messagebox.showwarning("Warning", "Please connect to a device first")
            return
            
        command = self.send_entry.get()
        
        if not command:
            return
            
        if self.hardware.send_command(command):
            self.monitoring_text.insert(tk.END, f">>> {command}\n")
            self.send_entry.delete(0, tk.END)
            
            # Cevabı bekle ve göster
            time.sleep(0.1)
            data = self.hardware.read_data()
            
            if data:
                self.monitoring_text.insert(tk.END, f"<<< {data.decode('utf-8', errors='ignore')}\n")
    
    def update_status(self, message):
        """Durum mesajını günceller"""
        self.status_messages.append(message)
        self.status_text.config(text=message)
        
        # Monitör paneline ekle
        timestamp = time.strftime("%H:%M:%S")
        self.monitoring_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.monitoring_text.see(tk.END)  # Otomatik kaydır
    
    def update_ui_state(self, connected=False):
        """UI durumunu bağlantı durumuna göre günceller"""
        if connected:
            self.status_label.config(text=f"Status: Connected ({self.hardware.device_path})")
            self.connect_button.config(state=tk.DISABLED)
            self.disconnect_button.config(state=tk.NORMAL)
            self.upload_button.config(state=tk.NORMAL)
            self.reset_button.config(state=tk.NORMAL)
            self.send_button.config(state=tk.NORMAL)
        else:
            self.status_label.config(text="Status: Not connected")
            self.connect_button.config(state=tk.NORMAL)
            self.disconnect_button.config(state=tk.DISABLED, disabledforeground="#ffffff")
            self.upload_button.config(state=tk.DISABLED, disabledforeground="#ffffff")
            self.reset_button.config(state=tk.DISABLED, disabledforeground="#ffffff")
            self.send_button.config(state=tk.DISABLED, disabledforeground="#ffffff")
            self.stop_connection_timer()
    
    def start_connection_timer(self):
        """Bağlantı süresini gösteren zamanlayıcıyı başlatır"""
        self.connection_start_time = time.time()
        self.update_connection_time()
    
    def stop_connection_timer(self):
        """Zamanlayıcıyı durdurur"""
        if hasattr(self, 'timer_id'):
            self.window.after_cancel(self.timer_id)
        self.time_label.config(text="Connection time: 00:00:00")
    
    def update_connection_time(self):
        """Bağlantı süresini günceller"""
        if hasattr(self, 'connection_start_time'):
            elapsed = time.time() - self.connection_start_time
            hours, remainder = divmod(int(elapsed), 3600)
            minutes, seconds = divmod(remainder, 60)
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            self.time_label.config(text=f"Connection time: {time_str}")
            
            # Her saniye güncelle
            self.timer_id = self.window.after(1000, self.update_connection_time)
    
    def on_close(self):
        """Pencere kapatıldığında bağlantıyı kes"""
        if self.hardware.connected:
            self.hardware.disconnect()
        
        self.window.destroy() 