from playwright.sync_api import sync_playwright

profile_dir = r"D:\dark_factory\tokens\tiktok_profile_cortesdoreddit"
print("[*] Verificando sessão do TikTok para @cortesdoreddit.br...")

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=profile_dir,
        headless=False,
        channel="chrome",
        args=["--disable-blink-features=AutomationControlled"]
    )
    page = context.new_page()
    page.goto("https://www.tiktok.com/tiktokstudio/upload", timeout=60000)
    page.wait_for_timeout(5000)

    if "login" in page.url:
        print("[!] Sessao ainda pendente. Faca login na janela aberta.")
    else:
        print("[+] SUCESSO: Sessao validada no TikTok Studio!")
    context.close()
