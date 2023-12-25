import sys
import pandas as pd
import tkinter as tk
from tkinter import simpledialog, messagebox
import socket

# Constants
ADMIN_PASSWORD = "admin123"
MAX_WEEKS = 14
CSV_FILE_PATH = 'presensi.csv'
SERVER_HOST = socket.gethostname()  # Ganti dengan IP server
SERVER_PORT = 5000

# Enums
class AttendanceStatus:
    Y = 'Y'
    I = 'I'
    S = 'S'
    A = 'A'

def read_data():
    try:
        data = pd.read_csv(CSV_FILE_PATH)
        return data.to_dict('records')
    except FileNotFoundError:
        messagebox.showerror("Error", f"File '{CSV_FILE_PATH}' tidak ditemukan. Buat file tersebut terlebih dahulu.")
        return None

def save_data(data):
    df = pd.DataFrame(data)
    df.to_csv(CSV_FILE_PATH, index=False)

def is_administrator():
    password = simpledialog.askstring("Administrator Password", "Masukkan kata sandi administrator:", show='*')
    return password == ADMIN_PASSWORD

def create_attendance(data, week):
    for student in data:
        print(f"Processing {student['nama']} ({student['nim']})")
        while True:
            attendance_status = simpledialog.askstring(
                f"Absen untuk {student['nama']} ({student['nim']})",
                f"Apakah hadir pada pertemuan ke-{week}? (Y/I/S/A): ").upper()
            if attendance_status in [AttendanceStatus.Y, AttendanceStatus.I, AttendanceStatus.S, AttendanceStatus.A]:
                break
            else:
                messagebox.showwarning("Warning", "Input tidak valid. Gunakan Y, I, S, atau A.")
        student[f'Pertemuan {week}'] = attendance_status
        print(f"{student['nama']} ({student['nim']}) attendance set to {attendance_status}")

def delete_attendance(data, week):
    for student in data:
        student[f'Pertemuan {week}'] = "-"

def update_attendance(data, week, nim, status):
    for student in data:
        if student['nim'] == nim:
            if status in [AttendanceStatus.Y, AttendanceStatus.I, AttendanceStatus.S, AttendanceStatus.A]:
                student[f'Pertemuan {week}'] = status
            else:
                messagebox.showwarning("Warning", "Input tidak valid. Gunakan Y, I, S, atau A.")

def show_attendance(data, week):
    try:
        df = pd.DataFrame(data)
        attendance_text = f"{'NIM':<15} {'Nama':<20} {'Kehadiran Pertemuan '+str(week):<25}\n"
        attendance_text += "-" * 60 + "\n"
        for _, row in df.iterrows():
            nim = row['nim']
            nama = row['nama']
            attendance = row[f'Pertemuan {week}']
            attendance_text += f"{nim:<15} {nama:<20} {attendance:<25}\n"
        messagebox.showinfo("Kehadiran", attendance_text)
    except KeyError:
        messagebox.showwarning("Warning", "Absensi belum dibuat, silahkan buat absensi terlebih dahulu.")
        
def send_message_to_server(message):
    try:
        client_socket = socket.socket()  # instantiate
        client_socket.connect((SERVER_HOST, SERVER_PORT))  # connect to the server
        client_socket.send(message.encode())  # send message

        data = client_socket.recv(1024).decode()  # receive response
        print('Received from server: ' + data)  # print response from server

        client_socket.close()  # close the connection
    except Exception as e:
        print(f"Error in sending message: {str(e)}")
        messagebox.showerror("Error", "Gagal terhubung ke server.")

def main():
    data = read_data()
    current_week = 14

    if data is None:
        sys.exit()

    root = tk.Tk()
    root.withdraw()  # Hide the main window

    while True:
        choice = simpledialog.askstring("Menu", f"\n{'Menu untuk Pertemuan ke-' + str(current_week)}\n"
                                                 "1. Buat Absen\n"
                                                 "2. Hapus Absen\n"
                                                 "3. Ubah Absen\n"
                                                 "4. Tampilkan Absen\n"
                                                 "5. Simpan Absen\n"
                                                 "6. Lanjut ke Pertemuan berikutnya\n"
                                                 "7. Absensi minggu sebelumnya\n"
                                                 "8. Kirim pesan ke server\n"
                                                 "9. Absensi pada pertemuan tertentu\n"
                                                 "10. Keluar\n\n"
                                                 "Pilih menu (1/2/3/4/5/6/7/8/9/10): ")

        try:
            if choice == '1':
                create_attendance(data, current_week)
                messagebox.showinfo("Info", "Absen berhasil dibuat.")

            elif choice == '2':
                if is_administrator():
                    delete_attendance(data, current_week)
                    messagebox.showinfo("Info", "Absen berhasil dihapus.")
                else:
                    messagebox.showwarning("Warning", "Anda tidak memiliki hak akses administrator.")

            elif choice == '3':
                if is_administrator():
                    nim = simpledialog.askstring("Ubah Absen", "Masukkan NIM mahasiswa:")
                    status = simpledialog.askstring("Ubah Absen", "Ubah absen menjadi (Y/I/S/A):").upper()
                    update_attendance(data, current_week, nim, status)
                    messagebox.showinfo("Info", "Absen berhasil diubah.")
                else:
                    messagebox.showwarning("Warning", "Anda tidak memiliki hak akses administrator.")

            elif choice == '4':
                show_attendance(data, current_week)

            elif choice == '5':
                save_data(data)
                messagebox.showinfo("Info", f"Data absen Pertemuan ke-{current_week} berhasil disimpan ke file {CSV_FILE_PATH}.")

            elif choice == '6':
                if current_week < MAX_WEEKS:
                    current_week += 1
                else:
                    messagebox.showwarning("Warning", f"Pertemuan hanya sampai minggu ke-{MAX_WEEKS}")

            elif choice == '7':
                if current_week > 1:
                    current_week -= 1
                else:
                    current_week = 0
                    
            elif choice == '8':
                while True:  # Loop untuk terus mengirim pesan ke server
                    message_to_send = simpledialog.askstring("Kirim Pesan", "Masukkan pesan yang akan dikirim ke server:")
                    if message_to_send:  # Jika ada pesan yang dimasukkan
                        send_message_to_server(message_to_send)  # Mengirim pesan ke server
                    else:  # Jika tidak ada pesan, keluar dari loop
                        break

            elif choice == '9':
                chosen_week = simpledialog.askinteger("Pertemuan Tertentu", "Masukkan nomor pertemuan:", minvalue=1, maxvalue=MAX_WEEKS)
                show_attendance(data, chosen_week)

            elif choice == '10':
                save_data(data)
                sys.exit()

            else:
                messagebox.showwarning("Warning", "Menu tidak valid. Pilih 1, 2, 3, 4, 5, 6, 7, 8, atau 9.")

        except ValueError:
            messagebox.showwarning("Warning", "Input tidak valid. Masukkan angka atau input yang sesuai.")

if __name__ == "__main__":
    main()
