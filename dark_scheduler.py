import os
import sys
import json
import time
import argparse
import subprocess
import urllib.request
import urllib.parse
from datetime import datetime

BASE_DIR = r"D:\dark_factory"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8534172006:AAE_wYmSAkPRv89Ow61kltqc4NAb-JNG2hE")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "2120995649")

def send_telegram(title: str, message: str, status: str = "SUCCESS"):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return
    icon = "✅" if status == "SUCCESS" else "⚠️"
    msg = (
        f"{icon} <b>Dark Factory | Agendador Autônomo</b>\n\n"
        f"<b>Canal:</b> {title}\n"
        f"<b>Status:</b> {status}\n"
        f"<b>Detalhes:</b> {message}\n"
        f"🕒 <b>Horário:</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
    )
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = urllib.parse.urlencode({"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "HTML"}).encode()
    try:
        req = urllib.request.Request(url, data=payload)
        with urllib.request.urlopen(req, timeout=15):
            pass
    except Exception:
        pass

def run_pipeline(command: list, channel_name: str):
    print(f"[*] Disparando rotina para: {channel_name}...")
    try:
        result = subprocess.run(
            command,
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            check=True
        )
        send_telegram(channel_name, "Vídeo renderizado e postado com sucesso!", "SUCCESS")
        print(f"[+] Sucesso: {channel_name}")
    except subprocess.CalledProcessError as e:
        err_msg = e.stderr[-350:] if e.stderr else e.stdout[-350:]
        send_telegram(channel_name, f"Falha na execução:\n<code>{err_msg}</code>", "ERROR")
        print(f"[!] Erro em {channel_name}: {err_msg}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--job", type=str, required=True, choices=["minuto_bizarro", "insight_de_ouro", "cortes_do_reddit", "buzz_comments", "all"])
    args = parser.parse_args()

    py_exe = sys.executable

    if args.job in ["minuto_bizarro", "all"]:
        run_pipeline([py_exe, "dark_pipeline.py", "--channel", "minuto_bizarro"], "Minuto Bizarro")

    if args.job in ["insight_de_ouro", "all"]:
        run_pipeline([py_exe, "dark_pipeline.py", "--channel", "insight_de_ouro"], "Insight de Ouro")

    if args.job in ["cortes_do_reddit", "all"]:
        run_pipeline([py_exe, "reddit_pipeline.py"], "Cortes do Reddit")

    if args.job in ["buzz_comments", "all"]:
        run_job([py_exe, "comment_buzz_engine.py", "--channel", "all"], "buzz_comments", "Buzz Engine (Comentários)")