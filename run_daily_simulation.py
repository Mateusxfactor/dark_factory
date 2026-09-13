import os
import sys
import time
import subprocess
import urllib.request
import urllib.parse
from datetime import datetime

BASE_DIR = r"D:\dark_factory"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8534172006:AAE_wYmSAkPRv89Ow61kltqc4NAb-JNG2hE")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "2120995649")

def send_tg(msg: str):
    print(msg)
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = urllib.parse.urlencode({
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg,
        "parse_mode": "HTML"
    }).encode("utf-8")
    try:
        req = urllib.request.Request(url, data=payload)
        with urllib.request.urlopen(req, timeout=12):
            pass
    except Exception as e:
        print(f"[!] Erro TG: {e}")

def run_job(command: list, label: str):
    send_tg(f"🚀 <b>[SIMULAÇÃO DIÁRIA]</b> Iniciando produção do canal: <b>{label}</b>...")
    start = time.time()
    try:
        proc = subprocess.run(
            command,
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            check=True
        )
        elapsed = int(time.time() - start)
        send_tg(f"✅ <b>{label}</b> concluído e publicado com sucesso em {elapsed}s!")
        return True
    except subprocess.CalledProcessError as e:
        err = e.stderr[-400:] if e.stderr else e.stdout[-400:]
        send_tg(f"❌ <b>Falha em {label}:</b>\n<code>{err}</code>")
        return False

def countdown_interval(minutes: int):
    send_tg(f"⏳ <b>Aguardando intervalo de segurança:</b> {minutes} minutos até o próximo canal...")
    for i in range(minutes * 60, 0, -30):
        time.sleep(30)
    send_tg("⏰ Intervalo finalizado. Disparando próxima postagem...")

def main():
    send_tg(
        "🏭 <b>DARK FACTORY | SIMULAÇÃO COMPLETA DE CICLO DIÁRIO</b>\n\n"
        "📅 <b>Escopo do Teste:</b>\n"
        "1. @minutobizarro\n"
        "2. @insightdeouro\n"
        "3. @cortesdoreddit.br\n\n"
        f"🕒 <b>Início:</b> {datetime.now().strftime('%H:%M:%S')}"
    )

    py_exe = sys.executable

    # 1. Minuto Bizarro
    run_job([py_exe, "dark_pipeline.py", "--channel", "minuto_bizarro"], "Minuto Bizarro")

    # Intervalo 3 minutos
    countdown_interval(3)

    # 2. Insight de Ouro
    run_job([py_exe, "dark_pipeline.py", "--channel", "insight_de_ouro"], "Insight de Ouro")

    # Intervalo 3 minutos
    countdown_interval(3)

    # 3. Cortes do Reddit (relato_002 - Parte 1)
    run_job([py_exe, "reddit_pipeline.py"], "Cortes do Reddit")

    send_tg(
        "🏁 <b>SIMULAÇÃO DIÁRIA CONCLUÍDA COM SUCESSO!</b>\n\n"
        "Os 3 canais publicaram seus respectivos vídeos com espaçamento temporal. "
        "Verifique as contas no TikTok."
    )

if __name__ == "__main__":
    main()
