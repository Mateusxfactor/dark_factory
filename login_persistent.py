import os
import sys
import argparse
from playwright.sync_api import sync_playwright

profile_dir = r"D:\dark_factory\tokens\tiktok_profile_minuto_bizarro"
os.makedirs(profile_dir, exist_ok=True)

print("=" * 65)
print("[*] AUTENTICAÇÃO PERSISTENTE - TIKTOK (MINUTO BIZARRO)")
print("=" * 65)
print("[*] Abrindo navegador com perfil dedicado...")

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=profile_dir,
        headless=False,
        channel="chrome",
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox"
        ],
        viewport={'width': 1366, 'height': 768}
    )
    page = context.new_page()
    page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    page.goto("https://www.tiktok.com/login", timeout=60000)

    print("\n" + "#" * 65)
    print(">>> 1. Realize o login no TikTok (QR Code ou E-mail/Senha).")
    print(">>> 2. Espere a página carregar e você estar dentro do TikTok.")
    print(">>> 3. Somente após ver a tela logada, volte aqui e aperte ENTER.")
    print("#" * 65 + "\n")

    input(">>> Pressione ENTER no PowerShell APÓS estar logado com sucesso... ")
    
    # Navega ate a tela de upload para garantir que os cookies do Studio assentaram
    page.goto("https://www.tiktok.com/tiktokstudio/upload", timeout=60000)
    page.wait_for_timeout(5000)
    
    context.close()
    print("\n[+] Perfil persistente autenticado e salvo com sucesso!")
