# Project Requirement
1. Ringkasan Proyek
Nama Aplikasi: Rach Scope
Tujuan: Aplikasi monitoring roasting kopi desktop (serupa Artisan Scope) untuk memvisualisasikan suhu (BT/ET) dan RoR secara real-time. Aplikasi ini membaca data dari hardware HF2211 via Modbus TCP, mendukung perbandingan profil (background curve), serta dapat dikompilasi ke file executable.

2. Tech Stack
Bahasa: Python 3.9+
GUI Framework: PyQt5
Plotting: pyqtgraph (Wajib untuk performa real-time, bukan Matplotlib).
Hardware Interface: pymodbus (Modbus TCP), pyserial.
Data Handling: pandas (CSV handling), numpy (Kalkulasi RoR).
Build Tools: pyinstaller (Target: .exe untuk Windows, .dmg untuk MacOS).

3. Pemetaan Komponen UI (Qt Component Mapping)
Gunakan komponen spesifik berikut untuk membangun antarmuka:
| Bagian UI | Komponen PyQt | Catatan Implementasi |
| :--- | :--- | :--- |
| **Jendela Utama** | `QMainWindow` | Fondasi utama, menampung MenuBar, Toolbar, dan Status Bar. |
| **Menu Atas** | `QMenuBar`, `QMenu`, `QAction` | Menu standar File, Settings, Help. |
| **Toolbar** | `QToolBar`, `QAction` | Tombol aksi cepat: Start, Stop, Save, Load Profile, Settings. Gunakan ikon jika memungkinkan. |
| **Layout Utama** | `QHBoxLayout` | Membagi layar menjadi dua kolom (Kiri: Kontrol, Kanan: Grafik). |
| **Panel Kiri** | `QGroupBox` / `QFrame` | Wadah kontrol. Layout internal: `QVBoxLayout`. |
| **Tampilan Data** | `QLabel` | Gunakan **Styling HTML/CSS** untuk font besar (BT: Merah, ET: Biru, RoR: Hijau). |
| **Indikator Profil** | `QLabel` | Menampilkan nama file profil yang diload (misal: "Ref: roast_01.csv"). |
| **Tombol Aksi** | `QPushButton` | Tombol standar: Mark Event (Dry End, First Crack, Second Crack). |
| **Grafik Roasting** | `pyqtgraph.PlotWidget` | Area plotting utama. Sangat disarankan untuk performa. |
| **Log/Status** | `QStatusBar` | Menampilkan status koneksi IP dan pesan error di pojok kanan bawah. |


4. Visual Wireframe (Layout Target)
Referensi visual untuk peletakan komponen:
+---------------------------------------------------------------+
|  QMenuBar: [File] [Settings] [Help]                           |
+---------------------------------------------------------------+
|  QToolBar: [Start] [Stop] [Save] [Load Profile] [Settings] ⚙️         |
+---------------------------------------------------------------+
|               |                                               |
|  QGroupBox    |           pyqtgraph.PlotWidget                |
| (Panel Kiri)  |                                               |
|               |  Reference (Dashed) -->  |                    |
|  --LIVE DATA--|  Live Data (Solid) --->  |                    |
|  BT: 165.5 C  |  |    ________ (ET)       |                    |
|  ET: 198.2 C  |  | __/        \___ (BT)   |                    |
|  RoR: 12.5    |  |                \___/       |                    |
|  Time: 08:45  |  |________________________|_________________   |
|               |  Sumbu X (Waktu)                              |
|               |                                               |
|  --REFERENCE--|                                               |
|  Ref: profileA|                                               |
|               |                                               |
|  [MARK EVENT] |                                               |
+---------------------------------------------------------------+
|  QStatusBar: Status: Connected to 192.168.1.100 | Msg: Ready  |
+---------------------------------------------------------------+
atau bisa lihat di ui-reference.png


5. Clean Code Architecture
Struktur folder wajib untuk menjaga kode rapi dan on context
rach_scope/
├── main.py              # Entry point aplikasi.
├── requirements.txt     # Library dependencies.
├── RachScope.spec        # PyInstaller spec untuk build (.exe/.dmg)
├── BUILD.md             # Instruksi build untuk Windows & MacOS
├── settings.json        # Penyimpanan config hardware (otomatis dibuat di user home directory).
├── core/                # LAYER LOGIC (Backend)
│   ├── __init__.py
│   ├── config_manager.py# Load/Save settings.json.
│   ├── data_manager.py  # Kalkulasi RoR, menangani data live & referensi.
│   ├── hardware_reader.py # Class ModbusReader (Integrasi kode HF2211).
│   └── models.py        # Struktur data (RoastData).
├── ui/                  # LAYER VIEW (Frontend)
│   ├── __init__.py
│   ├── main_window.py   # Setup QMainWindow, toolbar, timer, integrasi komponen.
│   ├── control_panel.py # Widget Panel Kiri (Label + Tombol + Signals).
│   ├── plot_widget.py   # Widget Grafik (PyQtGraph + 6 lines: 3 Live Solid, 3 Ref Dashed).
│   └── settings_dialog.py # Dialog Pengaturan Hardware (IP, Port, Slave ID BT/ET, Register, Scale).
├── utils/
│   ├── __init__.py
│   ├── path_manager.py  # Cross-platform path handling (config/log/data ke user writable dir).
│   └── logger.py        # Setup logging ke file.
└── assets/              # Ikon dan logo aplikasi.

6. Fitur Tambahan yang Sudah Diimplementasi
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ FITUR                                                                  │ IMPLEMENTASI │
├─────────────────────────────────────────────────────────────────────────────────────┤
│ Data Management                                                       │ ✅ Selesai    │
│ └─ Menyimpan list data live (time, bt, et, ror)                     │ core/data_manager.py  │
│ └─ Menyimpan list data reference (hasil load CSV)                         │ core/data_manager.py  │
│ └─ Fungsi calculate_ror(): (bt_sekarang - bt_lalu) / (waktu...)       │ core/data_manager.py  │
│ └─ Fungsi save_csv(): Menyimpan data live ke file                        │ core/data_manager.py  │
│ └─ Fungsi load_csv(): Memuat data ke list reference                        │ core/data_manager.py  │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│ Plotting Features                                                    │ ✅ Selesai    │
│ └─ 6 garis plot: 3 untuk Live Data (Solid), 3 untuk Reference (Dashed)  │ ui/plot_widget.py  │
│ └─ Warna: BT Merah (#e74c3c), ET Biru (#3498db), RoR Hijau (#27ae60) │ ui/plot_widget.py  │
│ └─ Plot Widget dengan pyqtgraph untuk performa real-time                       │ ui/plot_widget.py  │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│ Event Marking                                                     │ ✅ Selesai    │
│ └─ Mark Event: Tombol -> Catat timestamp -> Gambar garis vertikal   │ ui/plot_widget.py  │
│ └─ Dry End / First Crack / Second Crack buttons                          │ ui/control_panel.py  │
│ └─ InfiniteLine vertical dengan label nama event dan suhu                    │ ui/plot_widget.py  │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│ Timer Loop (1 detik)                                            │ ✅ Selesai    │
│ └─ QTimer (1000ms) -> ModbusReader.read_once() -> DataManager.add_data()  │ ui/main_window.py  │
│ └─ Update grafik Live (Solid) di atas Background Curve (Dashed)         │ ui/main_window.py  │
│ └─ Error handling: Jika read_once gagal -> "Disconnected" di Status Bar     │ ui/main_window.py  │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│ Load Profile Feature                                               │ ✅ Selesai    │
│ └─ Tombol Load Profile -> DataManager.load_csv() -> Plot Reference        │ ui/main_window.py  │
│ └─ Update ref_label dengan nama profil                                  │ ui/main_window.py  │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│ Start Record                                                     │ ✅ Selesai    │
│ └─ Tombol Start -> Reset data live -> Mulai QTimer (1 detik)         │ ui/main_window.py  │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│ Hardware Reader (Modbus TCP)                                    │ ✅ Selesai    │
│ └─ Class ModbusReader untuk HF2211                                       │ core/hardware_reader.py  │
│ └─ Baca config dari parameter class, jangan hardcode IP/Register            │ core/hardware_reader.py  │
│ └─ Hapus loop while. Ganti jadi fungsi read_once()                    │ core/hardware_reader.py  │
│ └─ Dikomali timer, mengembalikan (bt, et)                             │ core/hardware_reader.py  │
│ └─ Pertahankan logging ke file                                            │ core/hardware_reader.py  │
│ └─ Dukung slave_id_bt dan slave_id_et terpisah                             │ core/hardware_reader.py  │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│ Settings Dialog                                                     │ ✅ Selesai    │
│ └─ ui/settings_dialog.py sebagai subclass QDialog                           │ ui/settings_dialog.py  │
│ └─ Gunakan QFormLayout untuk menata input                                │ ui/settings_dialog.py  │
│ └─ Input fields:                                                     │ ui/settings_dialog.py  │
│   ├─ IP Address (QLineEdit)                                               │ ui/settings_dialog.py  │
│   ├─ Port (QSpinBox, range 1-65535)                                    │ ui/settings_dialog.py  │
│   ├─ Slave ID for BT (QSpinBox, range 0-247)                            │ ui/settings_dialog.py  │
│   ├─ Slave ID for ET (QSpinBox, range 0-247)                            │ ui/settings_dialog.py  │
│   ├─ BT Register (QSpinBox)                                            │ ui/settings_dialog.py  │
│   ├─ ET Register (QSpinBox)                                            │ ui/settings_dialog.py  │
│   └─ Scale Factor (QDoubleSpinBox)                                         │ ui/settings_dialog.py  │
│ └─ QDialogButtonBox dengan tombol Save dan Cancel                         │ ui/settings_dialog.py  │
│ └─ Fungsi set_data(config_dict) dan get_data()                           │ ui/settings_dialog.py  │
│ └─ Tombol Settings di toolbar dan menu menunjuk ke on_hardware_settings() │ ui/main_window.py  │
│ └─ Load config awal dari ConfigManager ke dialog                          │ ui/main_window.py  │
│ └─ Save kembali ke ConfigManager dan tampilkan pesan sukses           │ ui/main_window.py  │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│ Cross-Platform File Handling                                      │ ✅ Selesai    │
│ └─ File log dan settings.json ditulis di folder user home dir (writable) │ utils/path_manager.py │
│ └─ Platform:                                                       │ utils/path_manager.py  │
│   ├─ Windows: %LOCALAPPDATA%\RachScope\settings.json                       │ utils/path_manager.py  │
│   ├─ MacOS: ~/Library/Preferences/RachScope/settings.json                     │ utils/path_manager.py  │
│   ├─ Linux: ~/.config/RachScope/settings.json                                │ utils/path_manager.py  │
│ └─ Log files di folder logs yang writeable                             │ utils/path_manager.py  │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│ Build Configuration                                               │ ✅ Selesai    │
│ └─ RachScope.spec untuk PyInstaller (onefile, noconsole, include assets) │ RachScope.spec  │
│ └─ BUILD.md dengan instruksi build untuk Windows (.exe) dan MacOS (.dmg)  │ BUILD.md  │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│ UI Layout Lengkap                                                  │ ✅ Selesai    │
│ └─ Panel Kiri: Label BT/ET/RoR (Merah/Biru/Hijau) dengan font besar       │ ui/control_panel.py │
│ └─ Panel Kiri: ref_label untuk profil referensi                             │ ui/control_panel.py  │
│ └─ Panel Kiri: QPushButton Mark Event                                     │ ui/control_panel.py  │
│ └─ Panel Kiri: Dry End / First Crack / Second Crack buttons                   │ ui/control_panel.py  │
│ └─ Panel Kiri: Signals untuk event buttons                                 │ ui/control_panel.py  │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│ Bug Fixes                                                        │ ✅ Selesai    │
│ └─ High DPI Scaling (Qt.AA_EnableHighDpiScaling sebelum QApplication)       │ main.py  │
│ └─ QColor constructor (hex_to_qcolor helper function)                        │ ui/plot_widget.py  │
│ └─ QDialog import (ditambahkan ke main_window.py)                            │ ui/main_window.py  │
└─────────────────────────────────────────────────────────────────────────────────────────────┘

7. Fitur Tambahan yang Sudah Diimplementasi (Coffee Roasting Operations)
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ FITUR                                                                  │ IMPLEMENTASI │
├─────────────────────────────────────────────────────────────────────────────────────┤
│ Coffee Roasting Buttons                                             │ ✅ Selesai    │
│ └─ Tombol Charge untuk menandakan biji kopi dimasukkan                 │ ui/control_panel.py  │
│ └─ Tombol Drop untuk menandakan biji kopi jatuh ke penampungan        │ ui/control_panel.py  │
│ └─ Tombol FC Start/Finish untuk First Crack start & end                    │ ui/control_panel.py  │
│ └─ Tombol SC Start untuk Second Crack start                                  │ ui/control_panel.py  │
│ └─ Tombol Dry End untuk menandakan Dry End phase                          │ ui/control_panel.py  │
│ └─ Urutan tombol: Charge, FC Start, FC Finish, SC Start, Drop, Dry End   │ ui/control_panel.py  │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│ Signal untuk Tombol Events                                             │ ✅ Selesai    │
│ └─ charge_clicked, drop_clicked, fc_start_clicked, fc_finish_clicked         │ ui/control_panel.py  │
│ └─ sc_start_clicked, dry_end_clicked                                          │ ui/control_panel.py  │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│ Event Type Extensions                                                 │ ✅ Selesai    │
│ └─ EventType enum dengan CHARGE, DROP, FC_START, FC_FINISH                │ core/models.py  │
│ └─ EventType enum dengan SC_START (SC_FINISH dihapus)                         │ core/models.py  │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│ RoastEvent Model Extensions                                            │ ✅ Selesai    │
│ └─ Field end_bt untuk menyimpan suhu akhir FC                                │ core/models.py  │
│ └─ Field end_time untuk durasi FC (seconds)                                  │ core/models.py  │
│ └─ Field bean_color untuk tracking warna biji                                  │ core/models.py  │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│ Data Manager Extensions                                                 │ ✅ Selesai    │
│ └─ add_event() menerima event_type, end_bt, end_time, bean_color            │ core/data_manager.py  │
│ └─ save_csv() menyimpan event_type, end_bt, end_time, bean_color            │ core/data_manager.py  │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│ Main Window Coffee Event Handlers                                       │ ✅ Selesai    │
│ └─ on_charge() - menandai CHARGE event                                      │ ui/main_window.py  │
│ └─ on_drop() - menandai DROP event                                         │ ui/main_window.py  │
│ └─ on_fc_start() / on_fc_finish() - hitung end_time dan end_bt            │ ui/main_window.py  │
│ └─ on_sc_start() - menandai SC_START event (SC_FINISH dihapus)             │ ui/main_window.py  │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│ EVENTS Section Layout                                                │ ✅ Selesai    │
│ └─ Title label "EVENTS" (bukan tombol Mark Event)                          │ ui/control_panel.py  │
│ └─ Semua tombol dalam satu section dengan background #f9f9f9                   │ ui/control_panel.py  │
└─────────────────────────────────────────────────────────────────────────────────────────────┘

8. Fitur yang Masih TODO / Belum Diimplementasi
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ FITUR                                                                  │ STATUS │
├─────────────────────────────────────────────────────────────────────────────────────┤
│ UI Icons                                                          │ ⏸️ TODO  │
│ └─ Tambahkan ikon ke tombol toolbar (ikon folder assets/)                    │ assets/  │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│ Event Icons di Grafik                                              │ ⏸️ TODO  │
│ └─ Tambahkan ikon ke event buttons di control panel                         │ assets/  │
└─────────────────────────────────────────────────────────────────────────────────────────────┘

9. Cara Build & Test
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ AKSI                                                               │ PERINTAH   │
├─────────────────────────────────────────────────────────────────────────────────────┤
│ Install Dependencies                                                │ pip install -r requirements.txt │
│ Jalankan Aplikasi                                                 │ python main.py  │
│ Test UI (tanpa hardware)                                          │ Verifikasi UI muncul │
│ Test Load Profile (buat CSV test)                                      │ Buka test_profile.csv │
│ Klik Settings                                                      │ Verifikasi dialog muncul │
└─────────────────────────────────────────────────────────────────────────────────────┘

Build Windows (.exe):
```bash
pyinstaller RachScope.spec
# Hasil: dist/RachScope.exe
```

Build MacOS (.app/.dmg):
```bash
# Build .app
pyinstaller RachScope.spec
# Hasil: dist/RachScope.app

# Buat DMG (opsional)
create-dmg "dist/RachScope.app" "RachScope-1.0.0.dmg"
```

9. Format CSV untuk Profile
```
timestamp,bt,et,ror
0.0,150.0,160.0,5.0
10.0,155.0,165.0,4.5
20.0,160.0,170.0,4.0
30.0,165.0,175.0,3.5
```

Format CSV Output (saat Save):
```
timestamp,bt,et,ror
0.0,150.0,160.0,5.0
10.0,155.0,165.0,4.5
...
EVENTS
Event Name,Elapsed Time (s),BT,ET,RoR,Description
Dry End,120.0,180.0,185.0,4.5,
First Crack,180.0,200.0,205.0,3.5,
```
