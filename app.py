import sqlite3
import customtkinter as ctk
from tkinter import messagebox, ttk


# Inisialisasi database
conn = sqlite3.connect("sistem_akademik.db")
cursor = conn.cursor()

# Membuat tabel jika belum ada
cursor.execute("""
CREATE TABLE IF NOT EXISTS mahasiswa (
    nim TEXT PRIMARY KEY,
    nama TEXT NOT NULL,
    jurusan TEXT NOT NULL,
    semester INTEGER NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS mata_kuliah (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nim TEXT NOT NULL,
    nama_mk TEXT NOT NULL,
    sks INTEGER NOT NULL,
    nilai REAL NOT NULL,
    FOREIGN KEY (nim) REFERENCES mahasiswa (nim)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS admin (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL
)
""")
conn.commit()

# Daftar mata kuliah dengan SKS
COURSES = {
    'INTERAKSI MANUSIA DAN KOMPUTER': 3,
    'KEWIRAUSAHAAN I': 2,
    'KOMUNIKASI DAN ETIKA PROFESI': 3,
    'MATHEMATICAL TOOLS FOR DATA SCIENCE': 3,
    'NATURAL LANGUAGE PROCESSING (NLP)': 3,
    'PEMROGRAMAN BERORIENTASI OBJEK': 3,
    'PENGANTAR DATA MINING': 3,
    'DASAR KEAMANAN KOMPUTER': 3,
    'STATISTIK DAN PROBABILITAS': 3,
    'PENDIDIKAN AGAMA ISLAM': 2,
    'BAHASA INGGRIS I': 2,
    'KALKULUS': 3,
    'ALGORITMA DAN PEMROGRAMAN': 3,
    'SISTEM BASIS DATA': 3,
    'PANCASILA': 2,
    'BAHASA INGGRIS II': 2,
    'MATEMATIKA DISKRIT': 3,
    'STRUKTUR DATA': 3,
    'PRAKTIKUM ALGORITMA DAN STRUKTUR DATA': 3,
    'ARSITEKTUR KOMPUTER': 3,
    'CONA PAS I': 3,
    'PEMROGRAMAN WEB I': 3,
    'REKAYASA PERANGKAT LUNAK': 3,
    'PEMROGRAMAN PL/SQL': 3,
    'ALGORITMA LANJUT': 3,
    'PENGANTAR DATA SCIENCE': 3,
    'ALJABAR LINIER': 3,
    'SISTEM OPERASI': 3,
    'PENGANTAR KECERDASAN BUATAN': 3,
    'PEMROGRAMAN WEB ENTERPRISE': 3,
    'ANALISA BERORIENTASI OBJEK': 3,
    'MACHINE LEARNING': 3,
    'PEMROGRAMAN SMART WEB': 3,
    'PEMODELAN 2D/3D': 4,
    'PENGOLAHAN CITRA': 3,
    'KEWARGANEGARAAN': 2,
    'MOBILE PROGRAMMING': 3,
    'KOMPUTASI AWAN': 3
}

# Fungsi membuat akun admin awal (default)
def buat_akun_admin_awal():
    cursor.execute("SELECT * FROM admin")
    if not cursor.fetchall():
        cursor.execute("INSERT INTO admin (username, password) VALUES (?, ?)", ("admin", "admin123"))
        conn.commit()

# Fungsi hitung IPK
def hitung_ipk(nim):
    cursor.execute("SELECT sks, nilai FROM mata_kuliah WHERE nim = ?", (nim,))
    data = cursor.fetchall()
    if not data:
        return 0.0, 0
    total_sks = sum(d[0] for d in data)
    total_nilai = sum(d[0] * d[1] for d in data)
    ipk = total_nilai / total_sks if total_sks > 0 else 0.0
    return round(ipk, 2), total_sks

# Fungsi untuk menampilkan frame tertentu
def tampilkan_frame(frame):
    for widget in root.winfo_children():
        widget.pack_forget()
    frame.pack(fill="both", expand=True)

# Fungsi untuk admin menambah mata kuliah
def tambah_mata_kuliah():
    frame = ctk.CTkFrame(root)
    buat_navbar(frame, is_admin=True)

    container = ctk.CTkFrame(frame, corner_radius=10)
    container.pack(pady=20, padx=20, fill="both", expand=True)

    # Dropdown untuk memilih mahasiswa
    ctk.CTkLabel(container, text="Pilih Mahasiswa", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
    
    # Ambil daftar mahasiswa dari database
    cursor.execute("SELECT nim, nama FROM mahasiswa")
    mahasiswa_list = cursor.fetchall()
    
    # Buat dictionary untuk menyimpan nama dan NIM
    mahasiswa_dict = {f"{nim} - {nama}": nim for nim, nama in mahasiswa_list}
    
    # Dropdown untuk memilih mahasiswa
    mahasiswa_var = ctk.StringVar()
    if mahasiswa_dict:
        mahasiswa_dropdown = ctk.CTkOptionMenu(container, variable=mahasiswa_var, values=list(mahasiswa_dict.keys()))
        mahasiswa_dropdown.pack(pady=5)
    else:
        ctk.CTkLabel(container, text="Tidak ada mahasiswa terdaftar").pack(pady=5)
        return

    # Form input mata kuliah
    input_frame = ctk.CTkFrame(container)
    input_frame.pack(pady=10, padx=10, fill="x")

    ctk.CTkLabel(input_frame, text="Mata Kuliah").grid(row=0, column=0, padx=5, pady=5)
    
    # Buat dropdown untuk mata kuliah
    mata_kuliah_var = ctk.StringVar()
    mata_kuliah_dropdown = ctk.CTkOptionMenu(input_frame, variable=mata_kuliah_var, 
                                           values=list(COURSES.keys()))
    mata_kuliah_dropdown.grid(row=0, column=1, padx=5, pady=5)

    # SKS akan otomatis terisi
    ctk.CTkLabel(input_frame, text="SKS").grid(row=1, column=0, padx=5, pady=5)
    sks_label = ctk.CTkLabel(input_frame, text="")
    sks_label.grid(row=1, column=1, padx=5, pady=5)

    def update_sks(*args):
        selected_course = mata_kuliah_var.get()
        sks = COURSES.get(selected_course, 0)
        sks_label.configure(text=str(sks))

    mata_kuliah_var.trace_add('write', update_sks)

    ctk.CTkLabel(input_frame, text="Nilai").grid(row=2, column=0, padx=5, pady=5)
    nilai_entry = ctk.CTkEntry(input_frame)
    nilai_entry.grid(row=2, column=1, padx=5, pady=5)

    def simpan_mata_kuliah():
        try:
            selected = mahasiswa_var.get()
            nim = mahasiswa_dict[selected]
            nama_mk = mata_kuliah_var.get()
            sks = COURSES[nama_mk]
            nilai = float(nilai_entry.get())

            if not (0 <= nilai <= 4.0):
                raise ValueError("Nilai harus antara 0 dan 4.0")

            cursor.execute("""
                INSERT INTO mata_kuliah (nim, nama_mk, sks, nilai)
                VALUES (?, ?, ?, ?)
            """, (nim, nama_mk, sks, nilai))
            conn.commit()
            messagebox.showinfo("Sukses", "Mata kuliah berhasil ditambahkan!")
            
            # Reset nilai
            nilai_entry.delete(0, 'end')
            
            # Refresh tabel
            for item in tree.get_children():
                tree.delete(item)
                
            cursor.execute("""
                SELECT m.nim, mhs.nama, m.nama_mk, m.sks, m.nilai
                FROM mata_kuliah m
                JOIN mahasiswa mhs ON m.nim = mhs.nim
                ORDER BY m.nim, m.nama_mk
            """)
            for row in cursor.fetchall():
                tree.insert("", "end", values=row)
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan: {str(e)}")

    ctk.CTkButton(input_frame, text="Simpan", command=simpan_mata_kuliah).grid(row=3, column=0, columnspan=2, pady=10)

    # Tabel mata kuliah yang sudah ada
    table_frame = ctk.CTkFrame(container)
    table_frame.pack(pady=10, padx=10, fill="both", expand=True)

    ctk.CTkLabel(table_frame, text="Daftar Mata Kuliah yang Sudah Ada", 
                 font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)

    tree = ttk.Treeview(table_frame, columns=("NIM", "Nama", "Mata Kuliah", "SKS", "Nilai"), 
                        show="headings")
    tree.heading("NIM", text="NIM")
    tree.heading("Nama", text="Nama")
    tree.heading("Mata Kuliah", text="Mata Kuliah")
    tree.heading("SKS", text="SKS")
    tree.heading("Nilai", text="Nilai")

    # Set column widths
    tree.column("NIM", width=100)
    tree.column("Nama", width=150)
    tree.column("Mata Kuliah", width=250)
    tree.column("SKS", width=50)
    tree.column("Nilai", width=50)

    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)

    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Fungsi hapus mata kuliah
    def hapus_mata_kuliah():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Peringatan", "Pilih mata kuliah yang akan dihapus!")
            return
            
        if messagebox.askyesno("Konfirmasi", "Apakah Anda yakin ingin menghapus mata kuliah ini?"):
            try:
                item = tree.item(selected_item)
                nim = item['values'][0]
                nama_mk = item['values'][2]
                
                cursor.execute("""
                    DELETE FROM mata_kuliah 
                    WHERE nim = ? AND nama_mk = ?
                """, (nim, nama_mk))
                conn.commit()
                
                tree.delete(selected_item)
                messagebox.showinfo("Sukses", "Mata kuliah berhasil dihapus!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Gagal menghapus mata kuliah: {str(e)}")

    # Tombol hapus
    ctk.CTkButton(table_frame, text="Hapus", command=hapus_mata_kuliah).pack(pady=5)

    # Ambil dan tampilkan data
    cursor.execute("""
        SELECT m.nim, mhs.nama, m.nama_mk, m.sks, m.nilai
        FROM mata_kuliah m
        JOIN mahasiswa mhs ON m.nim = mhs.nim
        ORDER BY m.nim, m.nama_mk
    """)
    for row in cursor.fetchall():
        tree.insert("", "end", values=row)

    tampilkan_frame(frame)

# Fungsi halaman profil mahasiswa
def halaman_profil_mahasiswa(nim):
    frame = ctk.CTkFrame(root)
    buat_navbar(frame, nim)

    cursor.execute("SELECT nama, jurusan, semester FROM mahasiswa WHERE nim = ?", (nim,))
    mahasiswa = cursor.fetchone()

    container = ctk.CTkFrame(frame, corner_radius=10)
    container.pack(pady=20, padx=20, fill="both", expand=True)

    ctk.CTkLabel(container, text="Profil Mahasiswa", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, columnspan=2, pady=10)

    ctk.CTkLabel(container, text="Nama").grid(row=1, column=0, sticky="e", padx=5, pady=5)
    nama_entry = ctk.CTkEntry(container)
    nama_entry.insert(0, mahasiswa[0])
    nama_entry.grid(row=1, column=1, padx=5, pady=5)

    ctk.CTkLabel(container, text="Jurusan").grid(row=2, column=0, sticky="e", padx=5, pady=5)
    jurusan_entry = ctk.CTkEntry(container)
    jurusan_entry.insert(0, mahasiswa[1])
    jurusan_entry.grid(row=2, column=1, padx=5, pady=5)

    ctk.CTkLabel(container, text="Semester").grid(row=3, column=0, sticky="e", padx=5, pady=5)
    semester_entry = ctk.CTkEntry(container)
    semester_entry.insert(0, mahasiswa[2])
    semester_entry.grid(row=3, column=1, padx=5, pady=5)

    def simpan_perubahan():
        nama = nama_entry.get()
        jurusan = jurusan_entry.get()
        try:
            semester = int(semester_entry.get())
            cursor.execute("""
                UPDATE mahasiswa SET nama = ?, jurusan = ?, semester = ?
                WHERE nim = ?
            """, (nama, jurusan, semester, nim))
            conn.commit()
            messagebox.showinfo("Sukses", "Profil berhasil diperbarui!")
        except ValueError:
            messagebox.showerror("Error", "Semester harus berupa angka!")

    ctk.CTkButton(container, text="Simpan Perubahan", command=simpan_perubahan).grid(row=4, column=0, columnspan=2, pady=10)

    tampilkan_frame(frame)

# Fungsi halaman mata kuliah
def halaman_mata_kuliah(nim):
    frame = ctk.CTkFrame(root)
    buat_navbar(frame, nim)

    container = ctk.CTkFrame(frame, corner_radius=10)
    container.pack(pady=20, padx=20, fill="both", expand=True)

    # Label untuk IPK
    ipk, total_sks = hitung_ipk(nim)
    ipk_frame = ctk.CTkFrame(container)
    ipk_frame.pack(fill="x", padx=10, pady=10)
    
    ctk.CTkLabel(ipk_frame, text=f"IPK: {ipk}", font=ctk.CTkFont(size=14, weight="bold"), text_color="green").pack(side="left", padx=10)
    ctk.CTkLabel(ipk_frame, text=f"Total SKS: {total_sks}", font=ctk.CTkFont(size=14, weight="bold"), text_color="blue").pack(side="right", padx=10)

    # Tabel mata kuliah
    ctk.CTkLabel(container, text="Daftar Mata Kuliah dan Nilai", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

    # Frame untuk tabel
    table_frame = ctk.CTkFrame(container)
    table_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Treeview untuk menampilkan data
    tree = ttk.Treeview(table_frame, columns=("Mata Kuliah", "SKS", "Nilai"), show="headings")
    tree.heading("Mata Kuliah", text="Mata Kuliah")
    tree.heading("SKS", text="SKS")
    tree.heading("Nilai", text="Nilai")
    
    # Set column widths
    tree.column("Mata Kuliah", width=200)
    tree.column("SKS", width=100)
    tree.column("Nilai", width=100)
    
    # Add scrollbar
    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    
    # Pack the treeview and scrollbar
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Ambil dan tampilkan data
    cursor.execute("""
        SELECT nama_mk, sks, nilai 
        FROM mata_kuliah 
        WHERE nim = ? 
        ORDER BY nama_mk
    """, (nim,))
    
    for row in cursor.fetchall():
        tree.insert("", "end", values=row)

    tampilkan_frame(frame)

# Fungsi halaman utama mahasiswa
def mahasiswa_ui(nim):
    frame = ctk.CTkFrame(root)
    buat_navbar(frame, nim)

    container = ctk.CTkFrame(frame, corner_radius=10)
    container.pack(pady=20, padx=20, fill="both", expand=True)

    cursor.execute("SELECT nama, jurusan, semester FROM mahasiswa WHERE nim = ?", (nim,))
    mahasiswa = cursor.fetchone()
    ipk, total_sks = hitung_ipk(nim)

    if mahasiswa:
        nama, jurusan, semester = mahasiswa

        # Membuat tiga tabel horizontal untuk Nama, Jurusan, dan Semester
        data_frame = ctk.CTkFrame(container, corner_radius=10)
        data_frame.pack(pady=10, padx=10, fill="x")
        
        ctk.CTkLabel(data_frame, text=f"Nama: {nama}", font=ctk.CTkFont(size=12)).grid(row=0, column=0, padx=10, pady=5)
        ctk.CTkLabel(data_frame, text=f"Jurusan: {jurusan}", font=ctk.CTkFont(size=12)).grid(row=0, column=1, padx=10, pady=5)
        ctk.CTkLabel(data_frame, text=f"Semester: {semester}", font=ctk.CTkFont(size=12)).grid(row=0, column=2, padx=10, pady=5)

        # Membuat dua tabel di bagian bawah untuk IPK dan Total SKS
        bottom_frame = ctk.CTkFrame(container, corner_radius=10)
        bottom_frame.pack(pady=10, padx=10, fill="both", expand=True)

        ipk_frame = ctk.CTkFrame(bottom_frame, corner_radius=10, border_width=2, border_color="blue")
        ipk_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(ipk_frame, text=f"IPK: {ipk}", font=ctk.CTkFont(size=24, weight="bold"), text_color="green").pack(padx=50, pady=50)

        sks_frame = ctk.CTkFrame(bottom_frame, corner_radius=10, border_width=2, border_color="blue")
        sks_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(sks_frame, text=f"Total SKS: {total_sks}", font=ctk.CTkFont(size=24, weight="bold"), text_color="blue").pack(padx=50, pady=50)

        # Menambahkan kutipan di bawah IPK dan SKS
        quote_frame = ctk.CTkFrame(container, corner_radius=10)
        quote_frame.pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(quote_frame, text="\"Pendidikan adalah senjata paling ampuh untuk mengubah dunia.\" — Nelson Mandela",
                     font=ctk.CTkFont(size=14), text_color="gray").pack(pady=5)

        # Menyesuaikan tata letak grid
        bottom_frame.grid_columnconfigure(0, weight=1)
        bottom_frame.grid_columnconfigure(1, weight=1)

    tampilkan_frame(frame)

# Fungsi halaman utama admin
def admin_ui():
    frame = ctk.CTkFrame(root)
    buat_navbar(frame, is_admin=True)

    container = ctk.CTkFrame(frame, corner_radius=10)
    container.pack(pady=20, padx=20, fill="both", expand=True)

    ctk.CTkLabel(container, text="Selamat datang, Admin", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
    
    # Menambahkan statistik
    stats_frame = ctk.CTkFrame(container, corner_radius=10)
    stats_frame.pack(pady=10, padx=10, fill="x")

    # Mengambil statistik dari database
    cursor.execute("SELECT COUNT(*) FROM mahasiswa")
    total_mahasiswa = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM mata_kuliah")
    total_mk = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(nilai) FROM mata_kuliah")
    rata_nilai = cursor.fetchone()[0] or 0

    # Menampilkan statistik
    ctk.CTkLabel(stats_frame, text=f"Total Mahasiswa: {total_mahasiswa}", font=ctk.CTkFont(size=14)).pack(pady=5)
    ctk.CTkLabel(stats_frame, text=f"Total Mata Kuliah: {total_mk}", font=ctk.CTkFont(size=14)).pack(pady=5)
    ctk.CTkLabel(stats_frame, text=f"Rata-rata Nilai: {rata_nilai:.2f}", font=ctk.CTkFont(size=14)).pack(pady=5)

    # Tombol-tombol menu
    menu_frame = ctk.CTkFrame(container, corner_radius=10)
    menu_frame.pack(pady=20, padx=10, fill="x")

    ctk.CTkButton(menu_frame, text="Tambah Mahasiswa", command=tambah_mahasiswa).pack(pady=5, fill="x")
    ctk.CTkButton(menu_frame, text="Lihat Mahasiswa", command=lihat_mahasiswa).pack(pady=5, fill="x")
    ctk.CTkButton(menu_frame, text="Input Nilai", command=tambah_mata_kuliah).pack(pady=5, fill="x")

    tampilkan_frame(frame)

# Fungsi tambah mahasiswa
def tambah_mahasiswa():
    frame = ctk.CTkFrame(root)
    buat_navbar(frame, is_admin=True)

    container = ctk.CTkFrame(frame, corner_radius=10)
    container.pack(pady=20, padx=20, fill="both", expand=True)

    ctk.CTkLabel(container, text="Tambah Mahasiswa", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, columnspan=2, pady=10)

    ctk.CTkLabel(container, text="NIM").grid(row=1, column=0, sticky="e", padx=5, pady=5)
    nim_entry = ctk.CTkEntry(container)
    nim_entry.grid(row=1, column=1, padx=5, pady=5)

    ctk.CTkLabel(container, text="Nama").grid(row=2, column=0, sticky="e", padx=5, pady=5)
    nama_entry = ctk.CTkEntry(container)
    nama_entry.grid(row=2, column=1, padx=5, pady=5)

    ctk.CTkLabel(container, text="Jurusan").grid(row=3, column=0, sticky="e", padx=5, pady=5)
    jurusan_entry = ctk.CTkEntry(container)
    jurusan_entry.grid(row=3, column=1, padx=5, pady=5)

    ctk.CTkLabel(container, text="Semester").grid(row=4, column=0, sticky="e", padx=5, pady=5)
    semester_entry = ctk.CTkEntry(container)
    semester_entry.grid(row=4, column=1, padx=5, pady=5)

    def simpan_mahasiswa():
        nim = nim_entry.get()
        nama = nama_entry.get()
        jurusan = jurusan_entry.get()
        
        # Validasi input
        if not all([nim, nama, jurusan, semester_entry.get()]):
            messagebox.showerror("Error", "Semua field harus diisi!")
            return
            
        try:
            semester = int(semester_entry.get())
            if semester <= 0:
                raise ValueError("Semester harus lebih besar dari 0")
                
            cursor.execute("INSERT INTO mahasiswa (nim, nama, jurusan, semester) VALUES (?, ?, ?, ?)", 
                         (nim, nama, jurusan, semester))
            conn.commit()
            messagebox.showinfo("Sukses", "Mahasiswa berhasil ditambahkan!")
            
            # Reset form
            nim_entry.delete(0, 'end')
            nama_entry.delete(0, 'end')
            jurusan_entry.delete(0, 'end')
            semester_entry.delete(0, 'end')
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "NIM sudah terdaftar!")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    ctk.CTkButton(container, text="Simpan", command=simpan_mahasiswa).grid(row=5, column=0, columnspan=2, pady=10)

    tampilkan_frame(frame)

# Fungsi melihat daftar mahasiswa
def lihat_mahasiswa():
    frame = ctk.CTkFrame(root)
    buat_navbar(frame, is_admin=True)

    container = ctk.CTkFrame(frame, corner_radius=10)
    container.pack(pady=20, padx=20, fill="both", expand=True)

    # Label judul
    ctk.CTkLabel(container, text="Daftar Mahasiswa", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

    # Frame untuk tabel
    table_frame = ctk.CTkFrame(container)
    table_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Treeview untuk menampilkan data
    tree = ttk.Treeview(table_frame, columns=("NIM", "Nama", "Jurusan", "Semester", "IPK"), show="headings")
    tree.heading("NIM", text="NIM")
    tree.heading("Nama", text="Nama")
    tree.heading("Jurusan", text="Jurusan")
    tree.heading("Semester", text="Semester")
    tree.heading("IPK", text="IPK")

    # Scrollbar
    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)

    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Ambil dan tampilkan data
    cursor.execute("SELECT nim, nama, jurusan, semester FROM mahasiswa ORDER BY nim")
    for row in cursor.fetchall():
        nim, nama, jurusan, semester = row
        ipk, _ = hitung_ipk(nim)
        tree.insert("", "end", values=(nim, nama, jurusan, semester, f"{ipk:.2f}"))

    def edit_selected():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Peringatan", "Pilih mahasiswa yang ingin diedit!")
            return
        item = tree.item(selected_item)
        nim = item['values'][0]
        halaman_edit_mahasiswa(nim)

    def hapus_selected():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Peringatan", "Pilih mahasiswa yang ingin dihapus!")
            return
        item = tree.item(selected_item)
        nim = item['values'][0]
        if messagebox.askyesno("Konfirmasi", f"Apakah Anda yakin ingin menghapus mahasiswa dengan NIM {nim}?"):
            try:
                cursor.execute("DELETE FROM mata_kuliah WHERE nim = ?", (nim,))
                cursor.execute("DELETE FROM mahasiswa WHERE nim = ?", (nim,))
                conn.commit()
                tree.delete(selected_item)
                messagebox.showinfo("Sukses", "Mahasiswa berhasil dihapus!")
            except Exception as e:
                messagebox.showerror("Error", f"Gagal menghapus mahasiswa: {str(e)}")

    # Frame untuk tombol-tombol
    button_frame = ctk.CTkFrame(container)
    button_frame.pack(fill="x", pady=10)

    ctk.CTkButton(button_frame, text="Edit", command=edit_selected).pack(side="left", padx=5)
    ctk.CTkButton(button_frame, text="Hapus", command=hapus_selected).pack(side="left", padx=5)

    tampilkan_frame(frame)

# Fungsi halaman edit mahasiswa
def halaman_edit_mahasiswa(nim):
    frame = ctk.CTkFrame(root)
    buat_navbar(frame, is_admin=True)

    container = ctk.CTkFrame(frame, corner_radius=10)
    container.pack(pady=20, padx=20, fill="both", expand=True)

    ctk.CTkLabel(container, text="Edit Mahasiswa", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

    # Ambil data mahasiswa
    cursor.execute("SELECT nama, jurusan, semester FROM mahasiswa WHERE nim = ?", (nim,))
    mahasiswa = cursor.fetchone()

    if mahasiswa:
        nama, jurusan, semester = mahasiswa

        form_frame = ctk.CTkFrame(container)
        form_frame.pack(pady=10, padx=10, fill="x")

        # NIM (readonly)
        ctk.CTkLabel(form_frame, text="NIM").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        nim_label = ctk.CTkLabel(form_frame, text=nim)
        nim_label.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        # Nama
        ctk.CTkLabel(form_frame, text="Nama").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        nama_entry = ctk.CTkEntry(form_frame)
        nama_entry.insert(0, nama)
        nama_entry.grid(row=1, column=1, padx=5, pady=5)

        # Jurusan
        ctk.CTkLabel(form_frame, text="Jurusan").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        jurusan_entry = ctk.CTkEntry(form_frame)
        jurusan_entry.insert(0, jurusan)
        jurusan_entry.grid(row=2, column=1, padx=5, pady=5)

        # Semester
        ctk.CTkLabel(form_frame, text="Semester").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        semester_entry = ctk.CTkEntry(form_frame)
        semester_entry.insert(0, semester)
        semester_entry.grid(row=3, column=1, padx=5, pady=5)

        def simpan_perubahan():
            try:
                semester_baru = int(semester_entry.get())
                if semester_baru <= 0:
                    raise ValueError("Semester harus lebih besar dari 0")

                cursor.execute("""
                    UPDATE mahasiswa 
                    SET nama = ?, jurusan = ?, semester = ?
                    WHERE nim = ?
                """, (nama_entry.get(), jurusan_entry.get(), semester_baru, nim))
                conn.commit()
                messagebox.showinfo("Sukses", "Data mahasiswa berhasil diperbarui!")
                lihat_mahasiswa()
            except ValueError as e:
                messagebox.showerror("Error", str(e))
            except Exception as e:
                messagebox.showerror("Error", f"Terjadi kesalahan: {str(e)}")

        # Tombol simpan
        ctk.CTkButton(form_frame, text="Simpan Perubahan", command=simpan_perubahan).grid(row=4, column=0, columnspan=2, pady=10)

    tampilkan_frame(frame)

# Fungsi buat navbar
def buat_navbar(window, nim=None, is_admin=False):
    navbar = ctk.CTkFrame(window)
    navbar.pack(fill="x")

    ctk.CTkLabel(navbar, text="Sistem Akademik", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=10, pady=5)

    if is_admin:
        ctk.CTkButton(navbar, text="Dashboard", command=admin_ui).pack(side="left", padx=5)
        ctk.CTkButton(navbar, text="Lihat Mahasiswa", command=lihat_mahasiswa).pack(side="left", padx=5)
        ctk.CTkButton(navbar, text="Tambah Mahasiswa", command=tambah_mahasiswa).pack(side="left", padx=5)
        ctk.CTkButton(navbar, text="Input Nilai", command=tambah_mata_kuliah).pack(side="left", padx=5)
    else:
        ctk.CTkButton(navbar, text="Dashboard", command=lambda: mahasiswa_ui(nim)).pack(side="left", padx=5)
        ctk.CTkButton(navbar, text="Profil", command=lambda: halaman_profil_mahasiswa(nim)).pack(side="left", padx=5)
        ctk.CTkButton(navbar, text="Mata Kuliah", command=lambda: halaman_mata_kuliah(nim)).pack(side="left", padx=5)

    ctk.CTkButton(navbar, text="Logout", command=main, fg_color="red", text_color="white").pack(side="right", padx=10)


# Fungsi login
def login():
    nim = nim_entry.get()
    cursor.execute("SELECT * FROM mahasiswa WHERE nim = ?", (nim,))
    mahasiswa = cursor.fetchone()
    if mahasiswa:
        messagebox.showinfo("Login Berhasil", f"Selamat datang, {mahasiswa[1]}!")
        mahasiswa_ui(nim)
    elif nim == "admin":
        admin_ui()
    else:
        messagebox.showerror("Login Gagal", "NIM tidak ditemukan!")

# Fungsi utama untuk menampilkan halaman login
def main():
    global nim_entry
    frame = ctk.CTkFrame(root)

    panel = ctk.CTkFrame(frame, corner_radius=10)
    panel.pack(pady=50, padx=20)

    # Logo atau judul
    title_frame = ctk.CTkFrame(panel)
    title_frame.pack(pady=10, padx=20)
    
    ctk.CTkLabel(title_frame, text="Sistem Akademik", 
                 font=ctk.CTkFont(size=24, weight="bold")).pack()
    ctk.CTkLabel(title_frame, text="Manajemen Data Mahasiswa", 
                 font=ctk.CTkFont(size=14)).pack()

    # Form login
    login_frame = ctk.CTkFrame(panel)
    login_frame.pack(pady=20, padx=20)

    ctk.CTkLabel(login_frame, text="NIM / Admin", 
                 font=ctk.CTkFont(size=14)).pack(pady=5)
    nim_entry = ctk.CTkEntry(login_frame, width=200)
    nim_entry.pack(pady=5)

    ctk.CTkButton(login_frame, text="Login", 
                  command=login, width=200).pack(pady=20)

    # Info penggunaan
    info_frame = ctk.CTkFrame(panel)
    info_frame.pack(pady=10, padx=20, fill="x")
    
    ctk.CTkLabel(info_frame, text="Gunakan NIM untuk login sebagai mahasiswa\n" +
                               "atau 'admin' untuk login sebagai admin", 
                 font=ctk.CTkFont(size=12)).pack(pady=5)

    buat_akun_admin_awal()
    tampilkan_frame(frame)

# Inisialisasi root window
ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")
root = ctk.CTk()
root.title("Sistem Akademik")
root.geometry("900x600")

# Menambahkan ikon (opsional)
try:
    root.iconbitmap("icon.ico")  # Ganti dengan path ikon Anda
except:
    pass

# Center window on screen
window_width = 900
window_height = 600
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
center_x = int(screen_width/2 - window_width/2)
center_y = int(screen_height/2 - window_height/2)
root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

# Jalankan aplikasi
main()
root.mainloop()

# Tutup koneksi database saat aplikasi ditutup
conn.close()