import os
import sys
import time
import urllib.request
from playwright.sync_api import sync_playwright

BASE_DIR = r"D:\dark_factory"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8534172006:AAE_wYmSAkPRv89Ow61kltqc4NAb-JNG2hE")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "2120995649")

def send_telegram_photo(photo_path: str, caption: str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    
    with open(photo_path, "rb") as f:
        file_bytes = f.read()

    body = (
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"chat_id\"\r\n\r\n{TELEGRAM_CHAT_ID}\r\n"
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"caption\"\r\n\r\n{caption}\r\n"
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"photo\"; filename=\"proof.png\"\r\n"
        f"Content-Type: image/png\r\n\r\n"
    ).encode("utf-8") + file_bytes + f"\r\n--{boundary}--\r\n".encode("utf-8")

    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
    )
    try:
        with urllib.request.urlopen(req, timeout=20):
            print("[+] Comprovante visual enviado ao Telegram!")
    except Exception as e:
        print(f"[!] Erro ao enviar foto no Telegram: {e}")

def verify_channel_posts(profile_name: str, label: str):
    profile_dir = os.path.join(BASE_DIR, "tokens", profile_name)
    screenshot_path = os.path.join(BASE_DIR, f"audit_{profile_name}.png")
    
    print(f"[*] Auditando publicações de {label}...")
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            headless=False,
            channel="chrome",
            args=["--disable-blink-features=AutomationControlled", "--window-position=-32000,-32000"]
        )
        page = context.new_page()
        page.goto("https://www.tiktok.com/tiktokstudio/content", timeout=60000)
        page.wait_for_timeout(6000)

        # Captura a área da lista de conteúdo
        page.screenshot(path=screenshot_path)
        
        # Extrai o primeiro título/legenda exibido no topo da lista
        first_post_title = "Conteúdo recente carregado"
        try:
            first_post_el = page.locator("div[data-e2e='manage-post-item'], tr, div[class*='content-item']").first
            if first_post_el.is_visible():
                first_post_title = first_post_el.inner_text()[:180].replace("\n", " | ")
        except Exception:
            pass

        context.close()

    caption = (
        f"📸 <b>Auditoria de Postagem | {label}</b>\n\n"
        f"<b>Status:</b> Verificação da aba de conteúdo concluída.\n"
        f"<b>Registro topo:</b> <code>{first_post_title}</code>\n"
        f"🕒 {time.strftime('%d/%m/%Y %H:%M:%S')}"
    )
    send_telegram_photo(screenshot_path, caption)

if __name__ == "__main__":
    accounts = [
        ("tiktok_profile_minutobizarro", "Minuto Bizarro"),
        ("tiktok_profile_insightdeouro", "Insight de Ouro"),
        ("tiktok_profile_cortesdoreddit", "Cortes do Reddit")
    ]
    for prof, lbl in accounts:
        verify_channel_posts(prof, lbl)
        time.sleep(2)
