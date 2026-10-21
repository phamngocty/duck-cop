TỔNG HỢP CÔNG VIỆC ĐÃ HOÀN THÀNH
1. Đã chuyển toàn bộ hệ thống sang PHƯƠNG ÁN 1 thuần túy 100%
File mã nguồn chính: 

src/main.cpp
Đặc tính kỹ thuật:
0% WiFi, 0% WebServer, 0% LwIP: Triệt tiêu hoàn toàn đỉnh dòng 150mA–250mA của sóng RF radio lúc mở nguồn. Nguồn 5V qua mạch hạ áp trên xe máy luôn ổn định phẳng lì.
Tiếng còi đầu tiên phát to rõ cực đại ngay mili-giây đầu tiên (y hệt như bản gốc BACKUP copy/main.cpp).
Tích hợp 5 Slot âm thanh mặc định trong PROGMEM:
Slot 0: Vịt Còi Xe Chuẩn (Duck 2)
Slot 1: Vịt Kêu Đơn (Duck 1 – quạc đanh giòn, dứt khoát)
Slot 2: Vịt Còi Đôi (Double Quack)
Slot 3: Bò Rống (Cow Mooing)
Slot 4: Còi Cảnh Sát (Police Siren)
Đổi tiếng ngay trên tay lái: Nối chân GPIO1 (hoặc nút BOOT GPIO9) ra nút phụ. Nhấn nhả nhanh (< 1.5s) là còi nhảy sang tiếng tiếp theo, phát thử ngay tiếng mới và tự động lưu nhớ vào RTC SRAM + NVS (tắt khóa xe bật lại vẫn nhớ đúng tiếng đã chọn).
Cơ chế nạp Dynamic Sound Bank từ Flash (0x1E0000): Khi boot, vi điều khiển dùng esp_partition_mmap kiểm tra phân vùng Flash 0x1E0000. Nếu khách hàng đã nạp âm thanh mới qua Tool, còi sẽ tự động phát âm thanh tùy biến của khách mà không cần nạp lại firmware chính!
Kết quả biên dịch PlatformIO: SUCCESS (RAM dùng: 4.2%, Flash dùng: 16.0%).
2. Tối ưu và dọn dẹp thư mục tools/ thành bộ công cụ độc lập cho khách hàng (KHÔNG LỘ SOURCE CODE)
Đã xóa toàn bộ hơn 25 file rác debug (check_*.py, disasm_*.py, comp*.py,...). Thư mục 

tools/
 hiện tại là một gói Plug & Play 100% độc lập, bạn có thể nén zip gửi trực tiếp cho khách hàng:

text
tools/
├── Audio_Studio.html       <-- Giao diện đồ họa Studio (mở bằng Chrome/Edge/Cốc Cốc)
├── web_gui.html            <-- Bản sao Studio tương thích mọi trình duyệt
├── nap_tieng_coi.bat       <-- Công cụ 1-Click tự động nạp âm thanh trên Windows
├── build_sound_bank.py     <-- Script đóng gói nhị phân và gọi esptool nạp Flash 0x1E0000
├── convert_audio.py        <-- Máy chủ local hỗ trợ Studio khi chạy Python
├── sound_bank.bin          <-- Gói nhị phân âm thanh mẫu (51.1 KB)
├── sounds_sample/          <-- 5 file âm thanh WAV mẫu sẵn có (slot 0 -> slot 4)
├── sounds_input/           <-- Thư mục để khách hàng thả file MP3/WAV tùy thích vào
└── HUONG_DAN_SU_DUNG.txt   <-- File hướng dẫn chi tiết tiếng Việt cho khách hàng
BẢO MẬT: TẠI SAO KHÁCH HÀNG KHÔNG THỂ THẤY MÃ NGUỒN CHÍNH?
Khách hàng không nhận bất kỳ file C++ nào:
Thư mục tools/ không chứa main.cpp, sound_data.h, sound_bank.h, audio_player.h hay file dự án platformio.ini.
Cơ chế nạp âm thanh độc lập với Firmware:
Firmware chính của bạn nằm ở phân vùng app0 (0x10000).
Gói âm thanh của khách hàng nằm độc lập ở phân vùng Data 0x1E0000.
Tool của khách chỉ ghi đè dữ liệu PCM vào vùng 0x1E0000, không bao giờ đụng đến hoặc đọc ngược được mã nguồn vi điều khiển.
HƯỚNG DẪN BẠN GIAO CHO KHÁCH HÀNG
Khách hàng mua mạch còi của bạn có 2 cách cực kỳ đơn giản để đổi tiếng:

Cách 1 (Dễ nhất - Đồ họa Studio):
Mở file 

Audio_Studio.html
 bằng trình duyệt web.
Chọn Slot muốn đổi (0 đến 4) -> Bấm "Đổi tiếng file MP3/WAV" để tải bài hát của họ lên.
Kéo chuột trên dạng sóng âm để cắt đoạn hay nhất, nghe thử ưng ý.
Bấm "Xuất sound_bank.bin", sau đó cắm cáp USB Type-C và nhấp đúp file nap_tieng_coi.bat để nạp trong 3 giây.
Cách 2 (1-Click cực nhanh):
Thả các file âm thanh muốn đổi tên thành slot0.wav, slot1.wav,... vào thư mục sounds_input/.
Cắm cáp USB Type-C vào máy tính và chạy nap_tieng_coi.bat.