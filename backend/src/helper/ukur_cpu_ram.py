import os
import psutil
import threading

"""
Teknik ukur intinya
nanti melakukan ukur lalu hasil masukin ke list setiap 0.5 detik
lalu nanti dihitung rata rata nya
lumayan panjang kodenya karena pakai threading supaya atur nanti bisa di stop nya di line keberapa pengambilan datanya
"""

def proses_berat(durasi=5):
    """
    FUNGSI UNTUK NYOBAK AJA
    """
    import time
    mulai = time.time()
    while time.time() - mulai < durasi:
        sum(i * i for i in range(100_000))

def ukur_performa(interval=0.5):
    process = psutil.Process(os.getpid())
    sampling_ukur_cpu = []
    sampling_ukur_ram = []
    selesai = threading.Event()

    def monitor():
        while not selesai.is_set():
            sampling_ukur_cpu.append(process.cpu_percent(interval=interval))
            sampling_ukur_ram.append(process.memory_info().rss / (1024 ** 2))
            selesai.wait(0.5)

    process.cpu_percent()
    thread = threading.Thread(target=monitor)
    thread.start()

    def stop():
        selesai.set()
        thread.join()

        rata_rata_pemakaian_cpu = sum(sampling_ukur_cpu) / len(sampling_ukur_cpu) if sampling_ukur_cpu else 0
        rata_rata_pemakaian_ram = sum(sampling_ukur_ram) / len(sampling_ukur_ram) if sampling_ukur_ram else 0

        return rata_rata_pemakaian_cpu, rata_rata_pemakaian_ram

    return stop

