import os
import sys
from playwright.sync_api import sync_playwright

profile_dir = r"D:\dark_factory\tokens\tiktok_profile_cortesdoreddit"

print("[*] Inspecionando a aba de comentários do TikTok Studio...")

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=profile_dir,
        headless=False,
        channel="chrome",
        args=["--disable-blink-features=AutomationControlled", "--window-position=-32000,-32000"]
    )
    page = context.new_page()
    page.goto("https://www.tiktok.com/tiktokstudio/comment", timeout=60000)
    page.wait_for_timeout(6000)

    # Coleta todo o texto visível da página
    body_text = page.locator("body").inner_text()
    
    print("\n" + "="*50)
    print("RESUMO DO CONTEÚDO DA PÁGINA:")
    print("="*50)
    for line in body_text.split("\n"):
        clean = line.strip()
        if clean and len(clean) > 2 and not clean.startswith("http"):
            print(f"- {clean}")
            
    context.close()
