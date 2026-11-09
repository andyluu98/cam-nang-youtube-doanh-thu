# Cẩm nang xây dựng kênh YouTube tạo ra doanh thu cho doanh nghiệp

Giáo trình 8 buổi, mỗi buổi một trang HTML: từ xác định khách hàng, chiến lược nội dung, đóng gói video, kịch bản, dựng video, đội ngũ, đo doanh thu tới tối ưu và mở rộng quy mô.

**Xem trực tuyến:** https://andyluu98.github.io/cam-nang-youtube-doanh-thu/

## Lộ trình

| Buổi | Chủ đề | Trang |
|---|---|---|
| 1 | Xác định đúng đối tượng khách hàng | [buoi-01.html](buoi-01.html) |
| 2 | Chiến lược nội dung: nên đăng những gì | [buoi-02.html](buoi-02.html) |
| 3 | Đóng gói video: tiêu đề và thumbnail | [buoi-03.html](buoi-03.html) |
| 4 | Kịch bản và hook: giữ chân người xem | [buoi-04.html](buoi-04.html) |
| 5 | Dựng video và tối ưu trải nghiệm | [buoi-05.html](buoi-05.html) |
| 6 | Xây dựng và quản lý đội ngũ content | [buoi-06.html](buoi-06.html) |
| 7 | Biến lượt xem thành doanh thu | [buoi-07.html](buoi-07.html) |
| 8 | Tối ưu hệ thống và mở rộng quy mô | [buoi-08.html](buoi-08.html) |
| | Kết luận | [ket-luan.html](ket-luan.html) |

Mỗi buổi gồm: mục tiêu, tóm tắt 30 giây, nội dung chính, checklist áp dụng (lưu tiến độ trên trình duyệt), bài tập thực hành và câu hỏi tự kiểm tra.

## Cấu trúc

```
content/        Nội dung gốc từng buổi (Markdown)
assets/         Giao diện (style.css) và script nhỏ (app.js)
build.py        Sinh các trang HTML từ content/
*.html          Trang đã sinh, mở trực tiếp bằng trình duyệt
```

## Sửa nội dung

1. Sửa file trong `content/`.
2. Chạy `pip install markdown` (một lần) rồi `python build.py`.
3. Mở `index.html` để xem lại.
