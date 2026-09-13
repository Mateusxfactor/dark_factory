import os
import sys
import time
from playwright.sync_api import sync_playwright

profile_dir = r"D:\dark_factory\tokens\tiktok_chrome_profile"
video_path = r"D:\dark_factory\exports\minuto_bizarro\20260913_144340\video.mp4"
copy_file = r"D:\dark_factory\exports\minuto_bizarro\20260913_144340\tiktok_copy.txt"

with open(copy_file, "r", encoding="utf-8") as f:
    caption_text = f.read().strip()

print("[*] Iniciando upload teste no TikTok...")

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=profile_dir,
        headless=False,
        channel="chrome",
        args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
        viewport={'width': 1366, 'height': 768}
    )
    page = context.new_page()
    page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    print("[*] Acessando TikTok Studio...")
    page.goto("https://www.tiktok.com/tiktokstudio/upload", timeout=60000)
    page.wait_for_timeout(5000)

    print("[*] Injetando arquivo de vídeo...")
    file_input = page.locator("input[type='file']").first
    if not file_input.is_visible():
        for frame in page.frames:
            if frame.locator("input[type='file']").count() > 0:
                file_input = frame.locator("input[type='file']").first
                break

    file_input.set_input_files(video_path)
    print("[*] Aguardando upload e renderização inicial da interface...")
    page.wait_for_timeout(10000)

    # 1. Limpeza de modais e overlays que bloqueiam a tela
    print("[*] Verificando e fechando popups/overlays...")
    page.keyboard.press("Escape")
    page.wait_for_timeout(1000)

    modal_dismiss_selectors = [
        "button:has-text('Entendi')",
        "button:has-text('Aceitar')",
        "button:has-text('Got it')",
        "button:has-text('OK')",
        "button:has-text('Concordar')",
        "button[aria-label='Close']",
        "button[aria-label='Fechar']",
        ".TUXModal-overlay button"
    ]
    for sel in modal_dismiss_selectors:
        try:
            btns = page.locator(sel)
            for i in range(btns.count()):
                b = btns.nth(i)
                if b.is_visible():
                    b.click(force=True)
                    page.wait_for_timeout(1000)
        except Exception:
            pass

    page.keyboard.press("Escape")
    page.wait_for_timeout(2000)

    # 2. Preenchimento de legenda com clique forçado
    print("[*] Preenchendo texto e hashtags...")
    caption_box = page.locator("div[contenteditable='true']").first
    caption_box.wait_for(state="visible", timeout=20000)
    caption_box.click(force=True)
    page.wait_for_timeout(500)
    
    page.keyboard.press("Control+A")
    page.keyboard.press("Backspace")
    caption_box.type(caption_text, delay=20)
    page.wait_for_timeout(3000)

    # 3. Publicação
    print("[*] Localizando botão de publicação...")
    post_btn = page.locator("button:has-text('Publicar'), button:has-text('Post')").first
    post_btn.scroll_into_view_if_needed()
    page.wait_for_timeout(1000)
    post_btn.click(force=True)

    print("[*] Aguardando confirmação de envio...")
    page.wait_for_timeout(15000)

    print("[+] Postagem concluída com sucesso no TikTok!")
    context.close()
