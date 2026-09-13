from playwright.sync_api import sync_playwright

profile_dir = r"D:\dark_factory\tokens\tiktok_profile_insightdeouro"
print("[*] Abrindo gerenciador do TikTok Studio para verificar status...")

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=profile_dir,
        headless=False,
        channel="chrome",
        args=["--disable-blink-features=AutomationControlled"]
    )
    page = context.new_page()
    page.goto("https://www.tiktok.com/tiktokstudio/content", timeout=60000)
    page.wait_for_timeout(5000)
    
    print(">>> Verifique na tela se o vídeo está em 'Publicado' ou em 'Rascunhos'.")
    input(">>> Pressione ENTER no PowerShell para fechar o navegador... ")
    context.close()
