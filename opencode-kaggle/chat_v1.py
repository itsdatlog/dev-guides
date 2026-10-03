import subprocess
import threading
import time
import html
import json
import markdown
import ipywidgets as widgets
from IPython.display import display, HTML, Javascript

MODEL = "opencode/big-pickle"

lich_su_html = ""
dang_xu_ly = False
process_hien_tai = None
ngat_event = threading.Event()

noi_dung = widgets.HTML(value="")
trang_thai = widgets.HTML(value="")

# Nút ẩn dùng làm cầu nối từ JavaScript -> Python.
nut_gui_an = widgets.Button(
    description="send",
    layout=widgets.Layout(display="none")
)

nut_ngat_an = widgets.Button(
    description="interrupt",
    layout=widgets.Layout(display="none")
)

nut_gui_an.add_class("oc-hidden-send")
nut_ngat_an.add_class("oc-hidden-interrupt")

# ===== INPUT =====

# Cầu nối dữ liệu từ HTML/JavaScript -> Python.
bridge_input = widgets.Text(
    value="",
    layout=widgets.Layout(display="none")
)
bridge_input.add_class("oc-hidden-input")

composer_html = widgets.HTML(
    value=r"""
    <div class="oc-composer-shell">
        <div class="oc-composer-prompt">›</div>
        <div
            class="oc-composer-editor"
            contenteditable="true"
            role="textbox"
            aria-multiline="true"
            data-placeholder="Nhập yêu cầu...  Ctrl+. để gửi"
            spellcheck="false"
        ></div>
    </div>
    """
)


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
    display: grid;
    grid-template-columns: 20px minmax(0, 1fr);
    column-gap: 4px;
    align-items: start;
    min-height: 56px;
    margin: 10px 0;
    padding: 17px 16px;
}

.oc-composer-prompt {
    color: #999;
    line-height: 22px;
    user-select: none;
}

.oc-composer-editor {
    display: block;
    width: 100%;
    min-width: 0;
    min-height: 22px;
    max-height: 154px;
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    overflow-y: auto;
    background: transparent;
    color: #eeeeee;
    border: 0;
    outline: 0;
    box-shadow: none;
    font: inherit;
    line-height: 22px;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
    word-break: break-word;
    caret-color: #eeeeee;
}

.oc-composer-editor:empty::before {
    content: attr(data-placeholder);
    color: #8d8d8d;
    pointer-events: none;
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

    yeu_cau = bridge_input.value.strip()

    if not yeu_cau:
        return

    bridge_input.value = ""

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


nut_gui_an.on_click(lambda _: gui())
nut_ngat_an.on_click(lambda _: ngat_agent())


display(Javascript(r"""
(() => {
    const install = () => {
        const editor = document.querySelector('.oc-composer-editor');
        const hiddenInput = document.querySelector('.oc-hidden-input input');
        const sendBtn = document.querySelector('.oc-hidden-send button');
        const stopBtn = document.querySelector('.oc-hidden-interrupt button');

        if (!editor || !hiddenInput || !sendBtn || !stopBtn) {
            setTimeout(install, 100);
            return;
        }

        const syncToPython = () => {
            const setter = Object.getOwnPropertyDescriptor(
                HTMLInputElement.prototype,
                'value'
            ).set;

            setter.call(hiddenInput, editor.innerText.replace(/\r/g, ''));
            hiddenInput.dispatchEvent(
                new Event('input', { bubbles: true })
            );
            hiddenInput.dispatchEvent(
                new Event('change', { bubbles: true })
            );
        };

        editor.addEventListener('input', () => {
            syncToPython();
        });

        editor.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                e.preventDefault();
                e.stopPropagation();
                e.stopImmediatePropagation();
                stopBtn.click();
                return;
            }

            // Enter luôn dùng để xuống dòng tự nhiên.
            // Không chặn Enter/Shift+Enter nữa để tránh xung đột với Kaggle.

            // Ctrl + .  -> gửi
            if (e.ctrlKey && e.key === '.') {
                e.preventDefault();
                e.stopPropagation();
                e.stopImmediatePropagation();

                syncToPython();

                setTimeout(() => {
                    sendBtn.click();

                    setTimeout(() => {
                        editor.innerHTML = '';
                        syncToPython();
                        editor.focus();
                    }, 80);
                }, 40);
            }
        });

        editor.focus();
    };

    install();
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

display(nut_gui_an)
display(nut_ngat_an)
display(bridge_input)
display(noi_dung)
display(trang_thai)
display(composer_html)
