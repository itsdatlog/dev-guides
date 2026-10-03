import subprocess
import os
import threading
import time
import html
import markdown
from pathlib import Path
import ipywidgets as widgets
from IPython.display import display, HTML, Javascript

MODEL_MAC_DINH = "opencode/big-pickle"


def lay_danh_sach_model():
    try:
        ket_qua = subprocess.run(
            ["opencode", "models"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=20
        )

        models = [
            dong.strip()
            for dong in ket_qua.stdout.splitlines()
            if "/" in dong and " " not in dong.strip()
        ]

        # Giữ thứ tự OpenCode trả về nhưng loại trùng.
        models = list(dict.fromkeys(models))

        if MODEL_MAC_DINH not in models:
            models.insert(0, MODEL_MAC_DINH)

        return models

    except Exception:
        return [MODEL_MAC_DINH]


lich_su_html = ""
dang_xu_ly = False
process_hien_tai = None
ngat_event = threading.Event()

noi_dung = widgets.HTML(value="")
trang_thai = widgets.HTML(value="")

# Cầu nối ẩn chỉ dành cho phím Esc.
nut_ngat_an = widgets.Button(
    description="interrupt",
    layout=widgets.Layout(display="none")
)
nut_ngat_an.add_class("oc-hidden-interrupt")

# ===== MODEL =====

danh_sach_model = lay_danh_sach_model()

chon_model = widgets.Dropdown(
    options=danh_sach_model,
    value=MODEL_MAC_DINH,
    description="",
    layout=widgets.Layout(
        width="220px",
        height="28px"
    )
)
chon_model.add_class("oc-model-select")



# ===== KAGGLE API =====

kaggle_token = widgets.Password(
    placeholder="Kaggle token",
    layout=widgets.Layout(width="180px", height="26px")
)
kaggle_token.add_class("oc-kaggle-token")

nut_ket_noi_kaggle = widgets.Button(
    description="↵",
    tooltip="Kết nối Kaggle",
    layout=widgets.Layout(width="26px", height="26px")
)
nut_ket_noi_kaggle.add_class("oc-kaggle-connect")

nut_mo_kaggle = widgets.Button(
    description="Kaggle",
    tooltip="Kết nối Kaggle API",
    layout=widgets.Layout(width="auto", height="26px")
)
nut_mo_kaggle.add_class("oc-kaggle-inline")

kaggle_form = widgets.HBox(
    [kaggle_token, nut_ket_noi_kaggle],
    layout=widgets.Layout(
        width="auto",
        height="26px",
        align_items="center",
        gap="4px",
        display="none"
    )
)


def dat_form_kaggle(mo):
    kaggle_form.layout.display = "flex" if mo else "none"


def toggle_kaggle(_):
    dat_form_kaggle(kaggle_form.layout.display == "none")


def dat_trang_thai_kaggle(ok):
    nut_mo_kaggle.description = "Kaggle ✓" if ok else "Kaggle"


def ket_noi_kaggle(_):
    token = kaggle_token.value.strip()

    if not token:
        return

    try:
        os.environ["KAGGLE_API_TOKEN"] = token

        kaggle_dir = Path.home() / ".kaggle"
        kaggle_dir.mkdir(parents=True, exist_ok=True)
        kaggle_dir.chmod(0o700)

        token_file = kaggle_dir / "access_token"
        token_file.write_text(token, encoding="utf-8")
        token_file.chmod(0o600)

        test = subprocess.run(
            ["kaggle", "competitions", "list", "--group", "entered", "--format", "json"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=25
        )

        if test.returncode == 0:
            kaggle_token.value = ""
            dat_trang_thai_kaggle(True)
            dat_form_kaggle(False)

    except Exception:
        pass


nut_mo_kaggle.on_click(toggle_kaggle)
nut_ket_noi_kaggle.on_click(ket_noi_kaggle)

dat_trang_thai_kaggle(
    bool(
        os.environ.get("KAGGLE_API_TOKEN")
        or (Path.home() / ".kaggle" / "access_token").exists()
    )
)


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

.oc-model-select {
    margin: 0 !important;
    padding: 0 !important;
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace !important;
    font-size: 13px !important;
}

.oc-model-select select {
    height: 28px !important;
    padding: 0 22px 0 6px !important;
    background: transparent !important;
    color: #707070 !important;
    border: 0 !important;
    border-radius: 0 !important;
    outline: 0 !important;
    box-shadow: none !important;
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace !important;
    font-size: 13px !important;
    cursor: pointer;
}

.oc-model-select select:hover {
    color: #bdbdbd !important;
}

.oc-kaggle-inline button,
.oc-kaggle-connect button {
    height: 26px !important;
    padding: 0 4px !important;
    background: transparent !important;
    color: #707070 !important;
    border: 0 !important;
    box-shadow: none !important;
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace !important;
    font-size: 12px !important;
}

.oc-kaggle-inline button:hover,
.oc-kaggle-connect button:hover {
    color: #d7d7d7 !important;
}

.oc-kaggle-token input {
    height: 26px !important;
    padding: 0 6px !important;
    background: transparent !important;
    color: #d7d7d7 !important;
    border: 0 !important;
    border-bottom: 1px solid #3a3a3a !important;
    border-radius: 0 !important;
    box-shadow: none !important;
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace !important;
    font-size: 12px !important;
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
                chon_model.value,
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


# ===== ESC =====

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


nut_ngat_an.on_click(lambda _: ngat_agent())


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

header_label = widgets.HTML(
    value="""
    <div style="
        height:26px;
        display:flex;
        align-items:center;
        font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
        white-space:nowrap;
    ">
        <span style="color:#777;">&gt;_</span>
        <span style="margin-left:6px;color:#ddd;">OpenCode</span>
        <span style="margin-left:5px;color:#707070;">·</span>
    </div>
    """,
    layout=widgets.Layout(width="auto", height="26px")
)

header = widgets.HBox(
    [
        header_label,
        chon_model,
        widgets.HTML(
            value='<span style="color:#707070;line-height:26px;">·</span>',
            layout=widgets.Layout(width="8px", height="26px")
        ),
        nut_mo_kaggle,
        kaggle_form
    ],
    layout=widgets.Layout(
        width="100%",
        height="26px",
        align_items="center",
        gap="2px",
        margin="0 0 8px 0"
    )
)


# ===== HIỂN THỊ =====

display(nut_ngat_an)
display(header)
display(noi_dung)
display(trang_thai)
display(khung_nhap)

# Chỉ bắt Esc trên input. Enter vẫn hoàn toàn do widgets.Text xử lý native.
display(Javascript(r"""
(() => {
    const install = () => {
        const input = document.querySelector('.oc-native-input input');
        const stopBtn = document.querySelector('.oc-hidden-interrupt button');

        if (!input || !stopBtn) {
            setTimeout(install, 100);
            return;
        }

        if (input.dataset.ocEscInstalled === '1') return;
        input.dataset.ocEscInstalled = '1';

        input.addEventListener('keydown', (e) => {
            if (e.key !== 'Escape') return;

            e.preventDefault();
            e.stopPropagation();
            e.stopImmediatePropagation();
            stopBtn.click();
        }, true);
    };

    install();
})();
"""))
