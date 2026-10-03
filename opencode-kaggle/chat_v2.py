import subprocess
import gradio as gr

MODEL = "opencode/big-pickle"


def run_opencode(message, history):
    message = (message or "").strip()

    if not message:
        return ""

    process = subprocess.run(
        ["opencode", "run", "-m", MODEL, message],
        capture_output=True,
        text=True
    )

    output = process.stdout.strip()

    if not output:
        output = process.stderr.strip() or "Không nhận được phản hồi."

    lines = output.splitlines()

    if lines and lines[0].startswith("> build"):
        output = "\n".join(lines[1:]).strip()

    return output


CSS = """
.gradio-container {
    max-width: 100% !important;
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace !important;
}

footer {
    display: none !important;
}
"""


with gr.Blocks() as app:
    gr.Markdown("### >_ OpenCode · big-pickle")

    gr.ChatInterface(
        fn=run_opencode,
        textbox=gr.Textbox(
            placeholder="Nhập yêu cầu...  Enter để gửi · Shift+Enter xuống dòng",
            lines=1,
            max_lines=8,
            autofocus=True,
            container=False,
        ),
        chatbot=gr.Chatbot(
            height=520,
            show_label=False,
        ),
        submit_btn=False,
        stop_btn=True,
    )


app.launch(
    inline=True,
    share=True,
    quiet=True,
    show_error=True,
    theme=gr.themes.Base(),
    css=CSS,
)
