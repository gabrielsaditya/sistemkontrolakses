
import os
import psutil

"""
DIGUNAKAN SEBAGAI BANTUAN UNTUK MENGUKUR PERFORMA SERVER SAAT MENJALANKAN TUGAS 
"""

process = psutil.Process(os.getpid())

def ukur_performa_server():
    return {
        "penggunaan_cpu": process.cpu_percent(),
        "penggunaan_ram_mb": process.memory_info().rss / (1024 ** 2),
    }
