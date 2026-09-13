import os
import sys
import time
from playwright.sync_api import sync_playwright

profile_dir = r"D:\dark_factory\tokens\tiktok_profile_insightdeouro"

# Localiza o ultimo video gerado do insight_de_ouro
exports_base = r"D:\dark_factory\exports\insight_de_ouro"
subdirs = [os.path.join(exports_base, d) for d in os.listdir(exports_base) if os.path.isdir(os.path.join(exports_base, d))]
subdirs.sort(key=os.path.getmtime, reverse=True)

if not subdirs:
    print("[!] Nenhuma pasta de exportacao encontrada para insight_de_ouro.")
    sys.exit(1)

latest_dir = subdirs[0]
video_path = os.path.join(latest_dir, "video.mp4")
copy_file = os.path.join(latest_dir, "tiktok_copy.txt")

with open(copy_file, "r", encoding="utf-8") as f:
    caption_text = f.read().strip()

print(f"[*] Usando video: {video_path}")
print("[*] Iniciando TikTok Studio em modo interativo...")

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=profile_dir,
        headless=False,
        channel="chrome",
        args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
        viewport={'width': 1366, 'height': 850}
    )
    page = context.new_page()
    page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    page.goto("https://www.tiktok.com/tiktokstudio/upload", timeout=60000)
    page.wait_for_timeout(5000)

    # Localiza campo de arquivo
    file_input = page.locator("input[type='file']").first
    if not file_input.is_visible():
        for frame in page.frames:
            if frame.locator("input[type='file']").count() > 0:
                file_input = frame.locator("input[type='file']").first
                break

    print("[*] Injetando video no TikTok Studio...")
    file_input.set_input_files(video_path)

    # Trata eventuais modais ou avisos de boas-vindas
    page.wait_for_timeout(3000)
    page.keyboard.press("Escape")
    for sel in ["button:has-text('Entendi')", "button:has-text('Got it')", "button:has-text('Aceitar')"]:
        try:
            btn = page.locator(sel).first
            if btn.is_visible():
                btn.click()
        except Exception:
            pass

    # Aguarda a conclusao do carregamento na interface
    print("[*] Aguardando processamento do video (esperando botao Publicar ficar ativo)...")
    post_button_selector = "button:has-text('Publicar'):not([disabled]), button:has-text('Post'):not([disabled])"
    
    # Aguarda ate 90 segundos para o botao ficar ativo
    try:
        page.wait_for_selector(post_button_selector, timeout=90000)
        print("[+] Video carregado e validado pelo TikTok!")
    except Exception:
        print("[!] Timeout aguardando o botao Publicar ficar ativo. Verifique a janela do navegador.")

    # Preenche legenda
    print("[*] Atualizando texto da legenda...")
    caption_box = page.locator("div[contenteditable='true']").first
    if caption_box.is_visible():
        caption_box.click()
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        caption_box.type(caption_text, delay=20)
        page.wait_for_timeout(2000)

    # Clica no botao ativo de publicar
    print("[*] Acionando Publicar...")
    publish_btn = page.locator(post_button_selector).first
    publish_btn.click()

    # Confirma eventuais caixas de dialogo ("Publicar agora" ou confirmacao de audio)
    page.wait_for_timeout(3000)
    confirm_btn = page.locator("button:has-text('Publicar mesmo assim'), button:has-text('Post anyway'), button:has-text('Confirmar')").first
    if confirm_btn.is_visible():
        print("[*] Confirmando modal de direitos/som...")
        confirm_btn.click()

    # Aguarda redirecionamento ou aviso de sucesso
    print("[*] Aguardando confirmacao de envio...")
    try:
        # Espera tela de sucesso ou redirecionamento para o feed de posts
        page.wait_for_selector("text='Gerenciar vídeos', text='Manage your videos', text='Seu vídeo foi publicado', text='Your video has been uploaded'", timeout=30000)
        print("\n" + "=" * 60)
        print("[SUCCESS] Confirmado: O video foi postado oficialmente!")
        print("=" * 60 + "\n")
        page.wait_for_timeout(5000)
    except Exception:
        print("[!] Nao foi possivel detectar a mensagem final automaticamente. Verifique se o post concluiu na janela aberta.")
        page.wait_for_timeout(10000)

    context.close()
