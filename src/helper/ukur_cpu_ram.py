
import os
import psutil

"""
DIGUNAKAN SEBAGAI BANTUAN UNTUK MENGUKUR PERFORMA SERVER SAAT MENJALANKAN TUGAS 
"""

def ukur_performa_server():
    return {
        "penggunaan_cpu": process.cpu_percent(),
        

        #dari byte e mb ya dibagi 1024 terus dibagi 1024 lagi 
        "penggunaan_ram_mb": process.memory_info().rss / (1024 ** 2),
    }

hasil_ukur =ukur_performa_server()
print(hasil_ukur)