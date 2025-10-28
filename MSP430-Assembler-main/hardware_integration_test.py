import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import traceback

# MSP430 donanım entegrasyonu import
try:
    import msp430_integration
    import msp430_hardware
    import msp430_simulator
    import msp430_bridge
    HARDWARE_AVAILABLE = True
except Exception as e:
    HARDWARE_AVAILABLE = False
    error_details = traceback.format_exc()

def create_test_gui():
    """Test GUI oluşturur"""
    # Ana pencere
    root = tk.Tk()
    root.title("MSP430 Donanım Entegrasyonu Test Arayüzü")
    root.geometry("800x600")
    root.configure(bg="#1e1e1e")
    
    # Başlık
    title_label = tk.Label(root, 
                         text="MSP430 Donanım Test Arayüzü", 
                         font=("Impact", 24), 
                         bg="#1e1e1e", 
                         fg="#ffffff")
    title_label.pack(pady=20)
    
    # Durum bilgisi
    status_frame = tk.LabelFrame(root, 
                               text="Donanım Durumu", 
                               font=("Arial", 12, "bold"), 
                               bg="#1e1e1e", 
                               fg="#ffffff", 
                               padx=10, 
                               pady=10)
    status_frame.pack(fill=tk.X, padx=20, pady=10)
    
    if HARDWARE_AVAILABLE:
        hardware_status = tk.Label(status_frame, 
                                text="✓ MSP430 donanım modülleri başarıyla yüklendi", 
                                font=("Arial", 12), 
                                bg="#1e1e1e", 
                                fg="#4CAF50")
    else:
        hardware_status = tk.Label(status_frame, 
                                text="✗ MSP430 donanım modülleri yüklenemedi", 
                                font=("Arial", 12), 
                                bg="#1e1e1e", 
                                fg="#F44336")
    hardware_status.pack(anchor=tk.W)
    
    # Test seçenekleri
    test_frame = tk.LabelFrame(root, 
                             text="Test Seçenekleri", 
                             font=("Arial", 12, "bold"), 
                             bg="#1e1e1e", 
                             fg="#ffffff", 
                             padx=10, 
                             pady=10)
    test_frame.pack(fill=tk.X, padx=20, pady=10)
    
    # Butonlar
    test_menu_button = tk.Button(test_frame, 
                               text="Menü Entegrasyonunu Test Et", 
                               font=("Arial", 12), 
                               bg="#ff5722", 
                               fg="#ffffff", 
                               padx=10, 
                               pady=5,
                               command=test_menu_integration,
                               state=tk.NORMAL if HARDWARE_AVAILABLE else tk.DISABLED)
    test_menu_button.pack(fill=tk.X, pady=5)
    
    test_hardware_button = tk.Button(test_frame, 
                                  text="Donanım Arayüzünü Test Et", 
                                  font=("Arial", 12), 
                                  bg="#ff5722", 
                                  fg="#ffffff", 
                                  padx=10, 
                                  pady=5,
                                  command=test_hardware_interface,
                                  state=tk.NORMAL if HARDWARE_AVAILABLE else tk.DISABLED)
    test_hardware_button.pack(fill=tk.X, pady=5)
    
    test_simulator_button = tk.Button(test_frame, 
                                   text="Simülatörü Test Et", 
                                   font=("Arial", 12), 
                                   bg="#ff5722", 
                                   fg="#ffffff", 
                                   padx=10, 
                                   pady=5,
                                   command=test_simulator,
                                   state=tk.NORMAL if HARDWARE_AVAILABLE else tk.DISABLED)
    test_simulator_button.pack(fill=tk.X, pady=5)
    
    test_bridge_button = tk.Button(test_frame, 
                                text="Köprü Modülünü Test Et", 
                                font=("Arial", 12), 
                                bg="#ff5722", 
                                fg="#ffffff", 
                                padx=10, 
                                pady=5,
                                command=test_bridge,
                                state=tk.NORMAL if HARDWARE_AVAILABLE else tk.DISABLED)
    test_bridge_button.pack(fill=tk.X, pady=5)
    
    # Çıktı alanı
    output_frame = tk.LabelFrame(root, 
                               text="Test Çıktıları", 
                               font=("Arial", 12, "bold"), 
                               bg="#1e1e1e", 
                               fg="#ffffff", 
                               padx=10, 
                               pady=10)
    output_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    output_text = scrolledtext.ScrolledText(output_frame, 
                                          width=80, 
                                          height=10, 
                                          font=("Consolas", 10), 
                                          bg="#121212", 
                                          fg="#ffffff")
    output_text.pack(fill=tk.BOTH, expand=True, pady=5)
    
    # Eğer donanım modülleri yüklenemezse hata mesajını göster
    if not HARDWARE_AVAILABLE:
        output_text.insert(tk.END, "MSP430 donanım modülleri yüklenirken hata oluştu:\n\n")
        output_text.insert(tk.END, error_details)
        output_text.insert(tk.END, "\nSorun giderme önerileri:\n")
        output_text.insert(tk.END, "1. Python sürümünüzün uyumlu olduğundan emin olun (Python 3.6+)\n")
        output_text.insert(tk.END, "2. Gerekli bağımlılıkları yükleyin: pip install pyserial\n")
        output_text.insert(tk.END, "3. Tüm modül dosyalarının aynı dizinde olduğunu kontrol edin\n")
    else:
        output_text.insert(tk.END, "MSP430 donanım modülleri başarıyla yüklendi.\n\n")
        output_text.insert(tk.END, "Testleri çalıştırmak için yukarıdaki butonları kullanın.\n")
    
    # Butonlar
    button_frame = tk.Frame(root, bg="#1e1e1e")
    button_frame.pack(pady=10)
    
    close_button = tk.Button(button_frame, 
                           text="Kapat", 
                           font=("Arial", 12), 
                           bg="#F44336", 
                           fg="#ffffff", 
                           padx=20, 
                           pady=5, 
                           command=root.destroy)
    close_button.pack(side=tk.RIGHT, padx=5)
    
    return root, output_text

def test_menu_integration():
    """Menü entegrasyonunu test eder"""
    test_root = tk.Toplevel()
    test_root.title("Menü Entegrasyonu Testi")
    test_root.geometry("500x300")
    test_root.configure(bg="#1e1e1e")
    
    # Menü çubuğu oluştur
    menu_bar = tk.Menu(test_root)
    
    # Donanım entegrasyonu
    try:
        msp430_integration.integrate_hardware_interface(test_root, menu_bar)
        status_label = tk.Label(test_root, 
                              text="✓ Donanım menüsü başarıyla entegre edildi!\nDonanım menüsüne tıklayarak test edin.", 
                              font=("Arial", 12), 
                              bg="#1e1e1e", 
                              fg="#4CAF50")
        status_label.pack(pady=20)
    except Exception as e:
        error_text = f"Hata: {str(e)}"
        error_label = tk.Label(test_root, 
                             text=error_text, 
                             font=("Arial", 12), 
                             bg="#1e1e1e", 
                             fg="#F44336",
                             wraplength=400)
        error_label.pack(pady=20)
        traceback.print_exc()
    
    test_root.config(menu=menu_bar)
    
    # Kapat butonu
    close_button = tk.Button(test_root, 
                           text="Kapat", 
                           font=("Arial", 10), 
                           bg="#F44336", 
                           fg="#ffffff", 
                           command=test_root.destroy)
    close_button.pack(side=tk.BOTTOM, pady=20)

def test_hardware_interface():
    """Donanım arayüzünü test eder"""
    try:
        interface = msp430_hardware.HardwareInterface(tk.Tk())
        # İstersek burada daha fazla donanım işlemi test edilebilir
    except Exception as e:
        messagebox.showerror("Hata", f"Donanım arayüzü açılırken bir hata oluştu: {str(e)}")
        traceback.print_exc()

def test_simulator():
    """Simülatörü test eder"""
    try:
        simulator = msp430_simulator.MSP430Simulator(tk.Tk())
        # İstersek burada daha fazla simülatör işlemi test edilebilir
    except Exception as e:
        messagebox.showerror("Hata", f"Simülatör açılırken bir hata oluştu: {str(e)}")
        traceback.print_exc()

def test_bridge():
    """Köprü modülünü test eder"""
    # Bu test sadece modülleri oluşturmayı içerir
    try:
        bridge = msp430_bridge.MSP430Bridge()
        messagebox.showinfo("Bilgi", "Köprü modülü başarıyla oluşturuldu!")
    except Exception as e:
        messagebox.showerror("Hata", f"Köprü modülü oluşturulurken bir hata oluştu: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    print("Python sürümü:", sys.version)
    print("Çalışma dizini:", os.getcwd())
    
    # GUI oluştur
    root, output_text = create_test_gui()
    
    # Modül bilgilerini göster
    if HARDWARE_AVAILABLE:
        output_text.insert(tk.END, f"\nMSP430 Donanım sürümü: {getattr(msp430_hardware, '__version__', 'Bilinmiyor')}\n")
        output_text.insert(tk.END, f"MSP430 Simülatör sürümü: {getattr(msp430_simulator, '__version__', 'Bilinmiyor')}\n")
        output_text.insert(tk.END, f"MSP430 Köprü sürümü: {getattr(msp430_bridge, '__version__', 'Bilinmiyor')}\n")
        output_text.insert(tk.END, f"MSP430 Entegrasyon sürümü: {getattr(msp430_integration, '__version__', 'Bilinmiyor')}\n")
    
    # GUI döngüsünü başlat
    root.mainloop() 