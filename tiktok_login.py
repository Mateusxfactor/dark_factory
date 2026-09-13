#!/usr/bin/env python3
"""
TikTok Stealth Session Capture
Utiliza o Google Chrome nativo com argumentos anti-deteccao para login limpo.
"""

import os
import sys
import argparse
from playwright.sync_api import sync_playwright

TOKENS_DIR = r"D:\dark_factory\tokens"
os.makedirs(TOKENS_DIR, exist_ok=True)

def capture_session(channel_key: str):
    session_file = os.path.join(TOKENS_DIR, f"tiktok_{channel_key}.json")
    print("=" * 65)
    print(f"[*] AUTENTICACAO TIKTOK (MODO STEALTH) - CANAL: '{channel_key}'")
    print("=" * 65)
    print("[*] Iniciando Google Chrome em modo seguro anti-bloqueio...")

    with sync_playwright() as p:
        # Tenta abrir o Chrome do sistema; caso falhe, usa o Chromium padrao
        try:
            browser = p.chromium.launch(
                headless=False,
                channel="chrome",
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-infobars"
                ]
            )
        except Exception:
            browser = p.chromium.launch(
                headless=False,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-infobars"
                ]
            )

        context = browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        )
        
        page = context.new_page()
        # Oculta qualquer rastro de automacao do motor do navegador
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        page.goto("https://www.tiktok.com/login", timeout=60000)

        print("\n" + "#" * 65)
        print(">>> 1. Realize o login no TikTok na janela aberta.")
        print(">>> 2. Apos o login carregar a tela inicial do seu perfil, volte aqui.")
        print("#" * 65 + "\n")

        input(">>> Pressione ENTER no PowerShell APOS o login estar concluido... ")

        context.storage_state(path=session_file)
        print(f"\n[+] Sessao autenticada salva com sucesso em: {session_file}")
        browser.close()
        sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--channel", type=str, default="minuto_bizarro")
    args = parser.parse_args()
    capture_session(args.channel)
