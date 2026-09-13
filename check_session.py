import sys
from playwright.sync_api import sync_playwright

profile_dir = r"D:\dark_factory\tokens\tiktok_chrome_profile"

print("[*] Testando acesso persistente ao TikTok Studio...")
with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=profile_dir,
        headless=False,
        channel="chrome",
        args=["--disable-blink-features=AutomationControlled"]
    )
    page = context.new_page()
    page.goto("https://www.tiktok.com/tiktokstudio/upload", timeout=60000)
    page.wait_for_timeout(6000)

    print(f"[*] URL acessada: {page.url}")
    if "login" in page.url:
        print("[!] Falha: Ainda redirecionou para o login.")
    else:
        print("[+] SUCESSO: Acesso direto liberado ao painel de envio!")

    context.close()
