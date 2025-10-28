import os
import time
import tkinter as tk
from tkinter import messagebox
from msp430_hardware import HardwareInterface

# Simülatör entegrasyonu için
try:
    from msp430_simulator import MSP430Simulator
    SIMULATOR_AVAILABLE = True
except ImportError:
    SIMULATOR_AVAILABLE = False

def integrate_hardware_interface(root, menu_bar=None):
    """MSP430 donanım arayüzünü ana uygulamaya entegre eder"""
    
    # Menü yoksa oluştur
    if menu_bar is None:
        menu_bar = tk.Menu(root)
        root.config(menu=menu_bar)
    
    # Donanım menüsü
    hardware_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Hardware", menu=hardware_menu)
    
    # Menü seçenekleri
    hardware_menu.add_command(label="MSP430 Hardware Interface", 
                           command=lambda: open_hardware_interface(root))
    
    hardware_menu.add_separator()
    hardware_menu.add_command(label="Help", 
                           command=show_hardware_help)
    
    return menu_bar

def open_hardware_interface(root):
    """Donanım arayüzünü açar"""
    try:
        interface = HardwareInterface(root)
        return interface
    except Exception as e:
        messagebox.showerror("Hata", f"Donanım arayüzü açılırken bir hata oluştu: {str(e)}")
        return None

def open_simulator(root):
    """MSP430 görsel simülatörünü açar"""
    try:
        if SIMULATOR_AVAILABLE:
            simulator = MSP430Simulator(root)
            return simulator
        else:
            messagebox.showwarning("Uyarı", "MSP430 simülatörü mevcut değil!")
            return None
    except Exception as e:
        messagebox.showerror("Hata", f"Simülatör açılırken bir hata oluştu: {str(e)}")
        return None

def show_hardware_help():
    """Donanım yardım penceresini gösterir"""
    help_window = tk.Toplevel()
    help_window.title("MSP430 Hardware Help")
    help_window.geometry("600x400")
    help_window.configure(bg="#1e1e1e")
    
    # Başlık
    title = tk.Label(help_window, 
                   text="MSP430 Hardware Integration Help", 
                   font=("Impact", 16), 
                   bg="#1e1e1e", 
                   fg="#ffffff")
    title.pack(pady=10)
    
    # Yardım metni
    help_text = tk.Text(help_window, 
                      font=("Arial", 10), 
                      bg="#121212", 
                      fg="#ffffff", 
                      wrap=tk.WORD, 
                      padx=10, 
                      pady=10)
    help_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
    
    # Yardım içeriği
    help_content = """
MSP430 Hardware Integration Usage:

1. ESTABLISH CONNECTION
   - Open the Hardware Interface window.
   - Click the "Refresh Devices" button to list connected MSP430 devices.
   - Select a device from the list and click "Connect".
   - When connected, connection information will appear in the status bar.

2. UPLOAD CODE
   - Compile your assembly code and create a hex file.
   - Use the "Browse" button to select the hex file.
   - Click "Upload Code" to send the code to the MSP430 device.
   - A notification will appear when the upload is complete.

3. DEVICE CONTROL
   - Use the "Reset Device" button to restart the MSP430.
   - You can write special commands in the command field and send them to the device.
   - Responses from the device will automatically be displayed in the monitoring area.

4. REQUIREMENTS
   - MSP430 Launchpad or compatible MSP430 development board
   - Appropriate USB drivers
   - For Windows: MSP430 Flasher or MSPDebug
   - For Linux/Mac: MSPDebug

5. TROUBLESHOOTING
   - If device is not detected: Check USB cable and drivers.
   - If code cannot be uploaded: Make sure the programmer is configured correctly.
   - Connection errors: Check COM ports and make sure no other applications are using the port.
"""
    
    help_text.insert(tk.END, help_content)
    help_text.config(state=tk.DISABLED)
    
    # Kapat butonu
    close_button = tk.Button(help_window, 
                           text="Close", 
                           bg="#ff5722", 
                           fg="#ffffff", 
                           font=("Arial", 10), 
                           command=help_window.destroy)
    close_button.pack(pady=10)

def check_hardware_requirements():
    """Donanım entegrasyonu için gerekli bileşenleri kontrol eder"""
    try:
        import serial
        return True, "Gerekli modüller yüklü."
    except ImportError:
        return False, "Pyserial modülü bulunamadı. 'pip install pyserial' komutu ile yükleyebilirsiniz."

def get_connected_devices():
    """Bağlı MSP430 cihazlarının listesini döndürür"""
    try:
        from msp430_hardware import MSP430Hardware
        hardware = MSP430Hardware()
        devices = hardware.find_msp430_devices()
        return devices
    except Exception as e:
        print(f"Bağlı cihazlar listelenirken hata: {str(e)}")
        return []