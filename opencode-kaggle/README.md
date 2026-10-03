# Chạy OpenCode trên Kaggle Notebook

Hướng dẫn chạy OpenCode trên Kaggle và tạo giao diện chat liên tục ngay trong notebook.

## 1. Bật Internet

Trong Kaggle Notebook, mở **Settings** và bật **Internet**.

Kiểm tra:

```bash
!curl -I https://google.com
```

## 2. Cài OpenCode

```bash
!npm install -g @opencode/cli
```

Kiểm tra:

```bash
!opencode --version
```

Nếu binary cài qua npm gặp lỗi trên Kaggle, có thể dùng bản Linux x64 baseline:

```bash
!curl -L --fail --retry 5 https://opencode.ai/files/bin/2.0.22/opencode-linux-x64-baseline.tar.gz -o /tmp/opencode-baseline.tgz
!tar -xzf /tmp/opencode-baseline.tgz -C /usr/local/bin
!chmod +x /usr/local/bin/opencode
!opencode --version
```

## 3. Chọn model và chạy thử

Xem danh sách model:

```bash
!opencode models
```

Ví dụ:

```bash
!opencode run -m opencode/big-pickle "Xin chào, trả lời bằng tiếng Việt"
```

Trong Kaggle nên dùng `opencode run` thay vì mở TUI trực tiếp, vì output cell không phải terminal tương tác đầy đủ.

## 4. Cài thư viện cho giao diện chat

```bash
!pip install markdown ipyevents -q
```

## 5. Chạy Chat UI V1

Mở file [`chat_v1.py`](./chat_v1.py), copy toàn bộ nội dung vào một cell Python trong Kaggle Notebook rồi chạy.

### Phím tắt

- **Enter**: gửi yêu cầu.
- **Esc**: ngắt tiến trình OpenCode hiện tại.

## Đặc điểm V1

- Chat liên tục ngay trong notebook.
- Hiển thị Markdown.
- Hỗ trợ code block, table, link, quote.
- Loading state theo thời gian xử lý.
- Enter để gửi.
- Esc để interrupt.
- Giao diện tối, gọn, phù hợp notebook.

## Model mặc định

```python
MODEL = "opencode/big-pickle"
```

Bạn có thể đổi biến này sang model khác mà `opencode models` hỗ trợ.
