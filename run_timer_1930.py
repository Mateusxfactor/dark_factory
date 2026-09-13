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
    except Exception:
        pass

def wait_until_target(target_hour=19, target_minute=30):
    now = datetime.now()
    target = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
    
    # Se já passou das 19:30 hoje, agenda para o dia seguinte
    if target <= now:
        target = target.replace(day=now.day + 1)

    diff_seconds = int((target - now).total_seconds())
    diff_minutes = round(diff_seconds / 60, 1)

    send_tg(
        f"⏳ <b>[DARK FACTORY | AGENDAMENTO ATIVO]</b>\n\n"
        f"🎯 <b>Horário Alvo:</b> 19:30:00\n"
        f"🕒 <b>Hora Atual:</b> {now.strftime('%H:%M:%S')}\n"
        f"⏱️ <b>Tempo de Espera:</b> ~{diff_minutes} minutos ({diff_seconds}s)\n\n"
        f"O processo permanecerá em segundo plano e disparará pontualmente."
    )

    # Contagem regressiva com atualização no console a cada 30 segundos
    while True:
        current = datetime.now()
        remaining = int((target - current).total_seconds())
        if remaining <= 0:
            break
        if remaining % 300 == 0:  # Log no console a cada 5 minutos
            print(f"[*] Faltam {remaining // 60} minutos para 19:30...")
        time.sleep(1)

    send_tg(
        f"🚀 <b>19:30 ATINGIDO!</b>\n\n"
        f"Iniciando esteira de produção e publicação agendada..."
    )

def main():
    wait_until_target(19, 30)

    py_exe = sys.executable
    # Dispara a postagem de Cortes do Reddit (relato em andamento) com auditoria fotográfica
    cmd = [py_exe, "dark_scheduler.py", "--job", "cortes_do_reddit"]
    
    try:
        subprocess.run(cmd, cwd=BASE_DIR, check=True)
    except Exception as e:
        send_tg(f"❌ <b>Falha na execução das 19:30:</b>\n<code>{e}</code>")

if __name__ == "__main__":
    main()
