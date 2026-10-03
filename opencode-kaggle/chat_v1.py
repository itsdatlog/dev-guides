import subprocess
import os
import codecs
import selectors
import threading
import time
import html
import markdown
import ipywidgets as widgets
from IPython.display import display, HTML

MODEL = "opencode/big-pickle"

lich_su_html = ""
dang_xu_ly = False
process_hien_tai = None
ngat_event = threading.Event()

noi_dung = widgets.HTML(value="")
trang_thai = widgets.HTML(value="")

# ===== INPUT =====

o_nhap = widgets.Text(
    value="",
    placeholder="Nhập yêu cầu...  Enter để gửi",
    continuous_update=False,
    layout=widgets.Layout(
        width="100%",
        height="56px"
    )
)
o_nhap.add_class("oc-native-input")

khung_nhap = widgets.Box(
    [o_nhap],
    layout=widgets.Layout(
        width="100%",
        height="56px"
    )
)
khung_nhap.add_class("oc-composer-shell")


# ===== CSS =====

display(HTML("""
<style>

.jp-OutputArea-output,
.output_area,
.widget-html-content {
    overflow-x: hidden !important;
}

.oc-log {
    width: 100%;
    max-width: 100%;
    overflow-x: hidden;
    box-sizing: border-box;
}

.oc-composer-shell,
.oc-message {
    width: 100%;
    box-sizing: border-box;
    background: #3a3939;
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    font-size: 14px;
    line-height: 22px;
}

.oc-composer-shell {
    position: relative;
    height: 56px !important;
    min-height: 56px !important;
    margin: 10px 0 !important;
    padding: 0 !important;
    overflow: hidden !important;
}

.oc-composer-shell::before {
    content: "›";
    position: absolute;
    left: 16px;
    top: 17px;
    width: 20px;
    color: #999;
    font-size: 14px;
    line-height: 22px;
    pointer-events: none;
    z-index: 2;
}

.oc-native-input {
    width: 100% !important;
    height: 56px !important;
    margin: 0 !important;
    padding: 0 !important;
}

.oc-native-input .widget-label {
    display: none !important;
}

.oc-native-input input {
    width: 100% !important;
    height: 56px !important;
    box-sizing: border-box !important;
    margin: 0 !important;
    padding: 17px 16px 17px 40px !important;
    background: transparent !important;
    color: #eeeeee !important;
    border: 0 !important;
    border-radius: 0 !important;
    outline: 0 !important;
    box-shadow: none !important;
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace !important;
    font-size: 14px !important;
    line-height: 22px !important;
}

.oc-native-input input::placeholder {
    color: #8d8d8d !important;
    opacity: 1 !important;
}

.oc-message {
    position: relative;
    min-height: 56px;
    margin: 10px 0;
    padding: 17px 16px 17px 40px;
    color: #eeeeee;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
}

.oc-message::before {
    content: "›";
    position: absolute;
    left: 16px;
    top: 17px;
    width: 20px;
    color: #999;
    line-height: 22px;
}


.oc-stream {
    margin: 18px 14px 8px 14px;
    color: #d7d7d7;
    font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    font-size: 14px;
    line-height: 1.7;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
    word-break: normal;
}

.oc-answer {
    margin: 18px 14px 8px 14px;
    color: #d7d7d7;
    font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    font-size: 14px;
    line-height: 1.7;
    overflow-wrap: anywhere;
    word-break: normal;
}

.oc-answer > p {
    position: relative;
    margin: 7px 0 12px 0;
    padding-left: 16px;
}

.oc-answer > p::before {
    content: "·";
    position: absolute;
    left: 0;
    color: #6f8fa8;
}

.oc-answer h1,
.oc-answer h2,
.oc-answer h3,
.oc-answer h4 {
    color: #9fc5e8;
    font-weight: 500;
    line-height: 1.4;
    margin: 22px 0 9px 0;
    padding: 0;
}

.oc-answer h1 { font-size: 18px; }
.oc-answer h2 { font-size: 16px; }
.oc-answer h3 { font-size: 15px; }
.oc-answer h4 {
    font-size: 14px;
    color: #a9bdd0;
}

.oc-answer ul,
.oc-answer ol {
    margin: 7px 0 14px 0;
    padding-left: 24px;
}

.oc-answer li {
    margin: 5px 0;
    padding-left: 2px;
}

.oc-answer li::marker {
    color: #6f8fa8;
}

.oc-answer code {
    background: #2a2725;
    color: #e0aa79;
    padding: 2px 5px;
    border-radius: 4px;
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    font-size: 13px;
}

.oc-answer pre {
    margin: 14px 0;
    padding: 13px 15px;
    background: #161616;
    border: 1px solid #343434;
    border-left: 3px solid #6b8daa;
    border-radius: 6px;
    overflow-x: auto;
    line-height: 1.55;
}

.oc-answer pre code {
    background: transparent;
    color: #dcdcdc;
    padding: 0;
}

.oc-answer a {
    color: #76a9dc;
    text-decoration: none;
}

.oc-answer a:hover {
    color: #9fc5e8;
    text-decoration: underline;
}

.oc-answer blockquote {
    margin: 12px 0;
    padding: 6px 0 6px 12px;
    border-left: 3px solid #8a7fa8;
    color: #b7afc8;
}

.oc-answer table {
    width: 100%;
    margin: 14px 0;
    border-collapse: collapse;
    font-size: 13px;
}

.oc-answer th {
    padding: 8px 10px;
    background: #242b31;
    color: #a9c4da;
    border-bottom: 1px solid #46525c;
    font-weight: 500;
}

.oc-answer td {
    padding: 8px 10px;
    color: #d2d2d2;
    border-bottom: 1px solid #333;
}

.oc-answer strong,
.oc-answer b {
    color: #dfc48f;
    font-weight: 500;
}

.oc-answer em,
.oc-answer i {
    color: #b9a9d0;
}

.oc-done {
    margin: 4px 14px 22px 14px;
    color: #6e7d86;
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    font-size: 12px;
}

.oc-working {
    height: 32px;
    display: flex;
    align-items: center;
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    font-size: 13px;
}

.oc-spinner {
    width: 19px;
    display: inline-block;
    color: #d5b77a;
}

.oc-state {
    color: #c7b37e;
}

.oc-time {
    margin-left: 8px;
    color: #69757c;
}

</style>
"""))


# ===== RENDER =====

def hien_thi():
    noi_dung.value = f"""
    <div class="oc-log">
        {lich_su_html}
    </div>
    """


def markdown_sang_html(text):
    return markdown.markdown(
        text,
        extensions=[
            "fenced_code",
            "tables",
            "sane_lists"
        ]
    )


# ===== TRẠNG THÁI =====

def ten_trang_thai(giay):
    if giay < 2:
        return "Đang suy nghĩ"
    if giay < 5:
        return "Đang xem ngữ cảnh"
    if giay < 10:
        return "Đang thực hiện yêu cầu"
    if giay < 20:
        return "Đang tiếp tục xử lý"
    if giay < 40:
        return "Tác vụ đang mất thêm thời gian"
    return "Vẫn đang xử lý"


def hieu_ung_xu_ly(bat_dau):
    frames = [
        "⠋", "⠙", "⠹", "⠸",
        "⠼", "⠴", "⠦", "⠧",
        "⠇", "⠏"
    ]

    i = 0

    while dang_xu_ly:
        giay = max(1, int(time.time() - bat_dau))
        state = ten_trang_thai(giay)

        trang_thai.value = f"""
        <div class="oc-working">
            <span class="oc-spinner">{frames[i % len(frames)]}</span>
            <span class="oc-state">{state}</span>
            <span class="oc-time">{giay}s</span>
        </div>
        """

        i += 1
        time.sleep(0.08)


# ===== CHẠY OPENCODE =====

def chay_agent(yeu_cau):
    global lich_su_html
    global dang_xu_ly
    global process_hien_tai

    bat_dau = time.time()
    tra_loi = ""
    lan_render_cuoi = 0.0

    threading.Thread(
        target=hieu_ung_xu_ly,
        args=(bat_dau,),
        daemon=True
    ).start()

    try:
        # Giữ nguyên hành vi mặc định của OpenCode:
        # không custom agent, không thêm system prompt.
        process_hien_tai = subprocess.Popen(
            [
                "opencode",
                "run",
                "-m",
                MODEL,
                yeu_cau
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=0
        )

        decoder = codecs.getincrementaldecoder("utf-8")("replace")
        selector = selectors.DefaultSelector()
        selector.register(process_hien_tai.stdout, selectors.EVENT_READ)

        while True:
            if ngat_event.is_set():
                return

            events = selector.select(timeout=0.05)

            for key, _ in events:
                chunk = os.read(key.fileobj.fileno(), 512)

                if chunk:
                    tra_loi += decoder.decode(chunk)

            hien_tai = time.time()

            # Stream dưới dạng plain text để tránh Markdown reflow/jitter.
            if tra_loi and hien_tai - lan_render_cuoi >= 0.05:
                tam = tra_loi.strip()

                lines = tam.splitlines()

                if lines and lines[0].startswith("> build"):
                    tam = "\n".join(lines[1:]).strip()

                if tam:
                    noi_dung.value = f"""
                    <div class="oc-log">
                        {lich_su_html}
                        <div class="oc-stream">{html.escape(tam)}</div>
                    </div>
                    """

                lan_render_cuoi = hien_tai

            if process_hien_tai.poll() is not None:
                # Đọc nốt phần còn lại trong pipe.
                while True:
                    chunk = os.read(process_hien_tai.stdout.fileno(), 512)

                    if not chunk:
                        break

                    tra_loi += decoder.decode(chunk)

                tra_loi += decoder.decode(b"", final=True)
                break

        selector.close()

        if ngat_event.is_set():
            return

        tra_loi = tra_loi.strip()

        if not tra_loi:
            tra_loi = "Không nhận được phản hồi."

        lines = tra_loi.splitlines()

        if lines and lines[0].startswith("> build"):
            tra_loi = "\n".join(lines[1:]).strip()

        # Chỉ render Markdown hoàn chỉnh một lần khi stream kết thúc.
        tra_loi_html = markdown_sang_html(tra_loi)
        thoi_gian = time.time() - bat_dau

        lich_su_html += f"""
        <div class="oc-answer">
            {tra_loi_html}
        </div>

        <div class="oc-done">
            Hoàn thành sau {thoi_gian:.1f} giây
        </div>
        """

        hien_thi()

    finally:
        process_hien_tai = None
        dang_xu_ly = False

        if not ngat_event.is_set():
            trang_thai.value = ""


# ===== GỬI =====

def gui():
    global lich_su_html
    global dang_xu_ly

    if dang_xu_ly:
        return

    yeu_cau = o_nhap.value.strip()

    if not yeu_cau:
        return

    o_nhap.value = ""

    safe = html.escape(yeu_cau)

    lich_su_html += f"""
    <div class="oc-message">{safe}</div>
    """

    hien_thi()

    ngat_event.clear()
    dang_xu_ly = True

    threading.Thread(
        target=chay_agent,
        args=(yeu_cau,),
        daemon=True
    ).start()


# ===== ENTER =====

def khi_commit_input(change):
    # Với widgets.Text + continuous_update=False,
    # value chỉ được commit khi Enter hoặc khi input mất focus.
    # Nếu có nội dung mới thì gửi ngay.
    if change.get("name") != "value":
        return

    gia_tri = (change.get("new") or "").strip()

    if not gia_tri:
        return

    gui()


o_nhap.observe(
    khi_commit_input,
    names="value"
)


# ===== HEADER =====

display(HTML("""
<div style="
    font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
    margin-bottom:12px;
">
    <span style="color:#777;">&gt;_</span>
    <span style="margin-left:6px;color:#ddd;">OpenCode</span>
    <span style="color:#707070;">· big-pickle</span>
</div>
"""))


# ===== HIỂN THỊ =====

display(noi_dung)
display(trang_thai)
display(khung_nhap)
