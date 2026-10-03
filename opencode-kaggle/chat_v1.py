import subprocess
import threading
import time
import html
import markdown
import ipywidgets as widgets
from IPython.display import display, HTML, Javascript
from ipyevents import Event

MODEL = "opencode/big-pickle"

lich_su_html = ""
dang_xu_ly = False
process_hien_tai = None
ngat_event = threading.Event()

noi_dung = widgets.HTML(value="")
trang_thai = widgets.HTML(value="")

# ===== INPUT =====

o_nhap = widgets.Textarea(
    placeholder="Nhập yêu cầu...  (Shift + Enter để xuống dòng)",
    continuous_update=True,
    layout=widgets.Layout(
        width="auto",
        height="96px",
        flex="1 1 0",
        min_width="0"
    )
)

o_nhap.add_class("oc-input")


dau_nhap = widgets.HTML(
    value='<span class="oc-arrow">›</span>',
    layout=widgets.Layout(
        width="24px",
        height="96px"
    )
)

khung_nhap = widgets.HBox(
    [dau_nhap, o_nhap],
    layout=widgets.Layout(
        width="100%",
        height="96px",
        align_items="flex-start",
        overflow="hidden"
    )
)

khung_nhap.add_class("oc-user-block")


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

.oc-user-block {
    width: 100% !important;
    min-height: 96px !important;
    background: #3a3939 !important;
    margin: 10px 0 !important;
    padding: 0 14px !important;
    box-sizing: border-box !important;
    display: flex !important;
    align-items: flex-start !important;
    overflow: visible;
}

.oc-arrow {
    height: 96px;
    display: flex;
    align-items: flex-start;
    padding-top: 15px;
    color: #999;
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    font-size: 14px;
    line-height: 1;
}

.oc-input {
    flex: 1 1 0 !important;
    width: auto !important;
    min-width: 0 !important;
    height: 96px !important;
    margin: 0 !important;
    padding: 0 !important;
}

.oc-input .widget-label {
    display: none !important;
}

.oc-input textarea {
    width: 100% !important;
    height: 96px !important;
    min-height: 96px !important;
    resize: none !important;
    margin: 0 !important;
    padding: 14px 0 !important;
    background: transparent !important;
    color: #eeeeee !important;
    border: none !important;
    border-radius: 0 !important;
    box-shadow: none !important;
    outline: none !important;
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace !important;
    font-size: 14px !important;
    line-height: 1.55 !important;
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
    color: #7fa6c9;
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
    color: #9cc7ee;
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

    threading.Thread(
        target=hieu_ung_xu_ly,
        args=(bat_dau,),
        daemon=True
    ).start()

    try:
        process_hien_tai = subprocess.Popen(
            [
                "opencode",
                "run",
                "-m",
                MODEL,
                yeu_cau
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        stdout, stderr = process_hien_tai.communicate()

        if ngat_event.is_set():
            return

        tra_loi = stdout.strip()

        if not tra_loi:
            tra_loi = stderr.strip() or "Không nhận được phản hồi."

        lines = tra_loi.splitlines()

        if lines and lines[0].startswith("> build"):
            tra_loi = "\n".join(lines[1:]).strip()

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
    <div style="
        width:100%;
        min-height:52px;
        background:#3a3939;
        margin:10px 0;
        padding:0 14px;
        box-sizing:border-box;
        display:flex;
        align-items:center;
        overflow:hidden;
    ">
        <span style="
            width:24px;
            flex:0 0 24px;
            color:#999;
            font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
            font-size:14px;
            line-height:1;
        ">›</span>

        <span style="
            color:#eee;
            font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
            font-size:14px;
            overflow-wrap:anywhere;
            white-space:pre-wrap;
        ">{safe}</span>
    </div>
    """

    hien_thi()

    ngat_event.clear()
    dang_xu_ly = True

    threading.Thread(
        target=chay_agent,
        args=(yeu_cau,),
        daemon=True
    ).start()


# ===== PHÍM TẮT =====

def ngat_agent():
    global process_hien_tai
    global dang_xu_ly

    if not dang_xu_ly:
        return

    ngat_event.set()

    if process_hien_tai is not None:
        process_hien_tai.terminate()

        try:
            process_hien_tai.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process_hien_tai.kill()

    dang_xu_ly = False

    trang_thai.value = """
    <div class="oc-done">
        Đã ngắt bằng Esc
    </div>
    """


# Textarea:
# - Enter: gửi
# - Shift + Enter: xuống dòng
# - Esc: ngắt tiến trình
def xu_ly_phim(event):
    key = event.get("key", "")
    shift = bool(event.get("shiftKey", False))

    if key == "Escape":
        ngat_agent()
        return

    if key == "Enter" and not shift:
        # Đợi một nhịp rất ngắn để Textarea đồng bộ ký tự cuối về Python.
        threading.Timer(0.05, gui).start()


su_kien_phim = Event(
    source=o_nhap,
    watched_events=["keydown"],
    prevent_default_action=False
)

su_kien_phim.on_dom_event(
    xu_ly_phim
)


# ===== CHẶN PHÍM TẮT CỦA NOTEBOOK =====
# Kaggle/Jupyter có thể bắt Shift+Enter để chạy cell.
# Chặn Enter bubble ra notebook, nhưng vẫn giữ Shift+Enter để xuống dòng.
display(Javascript(r"""
(() => {
    const attach = () => {
        const areas = document.querySelectorAll('.oc-input textarea');

        if (!areas.length) {
            setTimeout(attach, 150);
            return;
        }

        areas.forEach((el) => {
            if (el.dataset.ocKeysReady === '1') return;
            el.dataset.ocKeysReady = '1';

            el.addEventListener(
                'keydown',
                (e) => {
                    if (e.key === 'Enter') {
                        // Không để Kaggle/Jupyter nhận Enter hoặc Shift+Enter.
                        e.stopPropagation();

                        // Enter thường dùng để gửi, không chèn newline.
                        // Shift+Enter vẫn giữ default để Textarea xuống dòng.
                        if (!e.shiftKey) {
                            e.preventDefault();
                        }
                    }

                    if (e.key === 'Escape') {
                        e.stopPropagation();
                    }
                },
                true
            );
        });
    };

    attach();
})();
"""))


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
