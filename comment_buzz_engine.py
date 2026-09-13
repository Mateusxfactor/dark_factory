import os
import sys
import json
import time
import random
import hashlib
import argparse
import urllib.request
import urllib.parse
from datetime import datetime
from playwright.sync_api import sync_playwright

BASE_DIR = r"D:\dark_factory"
MEMORY_FILE = os.path.join(BASE_DIR, "answered_comments.json")
TOKENS_DIR = os.path.join(BASE_DIR, "tokens")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8534172006:AAE_wYmSAkPRv89Ow61kltqc4NAb-JNG2hE")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "2120995649")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

CHANNEL_CONFIGS = {
    "minuto_bizarro": {
        "name": "Minuto Bizarro",
        "profile": "tokens/tiktok_profile_minutobizarro",
        "system_prompt": (
            "Você é o criador do Minuto Bizarro no TikTok (terror e mistérios). "
            "Responda ao comentário do seguidor em Português com no MÁXIMO 10 a 12 palavras. "
            "Seja intrigante e termine com uma pergunta provocativa. Sem hashtags."
        ),
        "fallbacks": [
            "Você teria coragem de ir lá sozinho à noite?",
            "O mais bizarro é o que a polícia omitiu nesse caso...",
            "Muita gente não reparou no detalhe aos 15 segundos.",
            "Acha que foi armação ou fenômeno inexplicável?"
        ]
    },
    "insight_de_ouro": {
        "name": "Insight de Ouro",
        "profile": "tokens/tiktok_profile_insightdeouro",
        "system_prompt": (
            "Você é o criador do Insight de Ouro no TikTok (desenvolvimento pessoal e foco). "
            "Responda ao comentário com no MÁXIMO 10 a 12 palavras. "
            "Seja direto e faça uma pergunta reflexiva sobre ação ou disciplina."
        ),
        "fallbacks": [
            "A maioria desiste exatamente nesse ponto. O que você vai fazer?",
            "O tempo é implacável com quem hesita. Já começou hoje?",
            "Disciplina dói menos que o arrependimento tardio. Concorda?",
            "Você prefere o conforto temporário ou o resultado consistente?"
        ]
    },
    "cortes_do_reddit": {
        "name": "Cortes do Reddit",
        "profile": "tokens/tiktok_profile_cortesdoreddit",
        "system_prompt": (
            "Você é o narrador do canal Cortes do Reddit no TikTok. "
            "Responda ao comentário com no MÁXIMO 10 a 12 palavras, "
            "perguntando o que a pessoa teria feito na mesma situação moral."
        ),
        "fallbacks": [
            "Se estivesse no lugar dele, você teria perdoado?",
            "A continuação revela um detalhe ainda pior sobre isso...",
            "Acha que a atitude foi exagerada ou justa?",
            "Muita gente defendeu o outro lado. O que você faria?"
        ]
    }
}

def tg_send(msg: str):
    print(msg)
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = urllib.parse.urlencode({"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "HTML"}).encode("utf-8")
    try:
        req = urllib.request.Request(url, data=payload)
        with urllib.request.urlopen(req, timeout=10):
            pass
    except Exception as e:
        print(f"[!] Erro TG: {e}")

def tg_photo(photo_path: str, caption: str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID or not os.path.exists(photo_path):
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
        f"Content-Disposition: form-data; name=\"parse_mode\"\r\n\r\nHTML\r\n"
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"photo\"; filename=\"audit.png\"\r\n"
        f"Content-Type: image/png\r\n\r\n"
    ).encode("utf-8") + file_bytes + f"\r\n--{boundary}--\r\n".encode("utf-8")

    req = urllib.request.Request(url, data=body, headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    try:
        with urllib.request.urlopen(req, timeout=20):
            pass
    except Exception:
        pass

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"answered_hashes": []}

def save_memory(mem):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(mem, f, indent=2, ensure_ascii=False)

def generate_reply(channel_key: str, comment_text: str) -> str:
    cfg = CHANNEL_CONFIGS[channel_key]
    if GEMINI_API_KEY:
        try:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")
            resp = model.generate_content(f"{cfg['system_prompt']}\n\nComentário: \"{comment_text}\"\nResposta:")
            clean = resp.text.strip().replace('"', '').replace('\n', ' ')
            if clean and len(clean) < 120:
                return clean
        except Exception:
            pass
    return random.choice(cfg["fallbacks"])

def process_channel(channel_key: str, max_replies: int = 5, force: bool = False):
    cfg = CHANNEL_CONFIGS.get(channel_key)
    profile_dir = os.path.join(BASE_DIR, cfg["profile"])
    if not os.path.exists(profile_dir):
        tg_send(f"⚠️ Perfil não encontrado para <b>{cfg['name']}</b>.")
        return

    tg_send(f"🔍 <b>[Buzz Engine]</b> Conectando a <b>{cfg['name']}</b> para responder até {max_replies} comentários...")
    mem = load_memory()
    replies_done = []

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            headless=False,
            channel="chrome",
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--window-position=-32000,-32000",
                "--window-size=1366,850"
            ],
            viewport={'width': 1366, 'height': 850}
        )
        page = context.new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        page.goto("https://www.tiktok.com/tiktokstudio/comment", timeout=60000)
        page.wait_for_timeout(7000)

        # Trata popups
        page.keyboard.press("Escape")
        for sel in ["button:has-text('Entendi')", "button:has-text('Got it')", "button:has-text('Aceitar')"]:
            try:
                b = page.locator(sel).first
                if b.is_visible():
                    b.click()
            except Exception:
                pass

        # Seletores amplos de botões "Responder" no TikTok Studio
        reply_btn_selectors = [
            "button:has-text('Responder')",
            "button:has-text('Reply')",
            "div[role='button']:has-text('Responder')",
            "span:has-text('Responder')",
            "[data-e2e='comment-reply']"
        ]

        found_buttons = None
        for sel in reply_btn_selectors:
            loc = page.locator(sel)
            if loc.count() > 0:
                found_buttons = loc
                break

        if not found_buttons or found_buttons.count() == 0:
            body_txt = page.locator("body").inner_text()
            if "Ainda não há comentários" in body_txt or "No comments yet" in body_txt:
                print(f"[*] {cfg['name']}: Nenhum comentário novo registrado na conta.")
            else:
                debug_img = os.path.join(BASE_DIR, f"comments_debug_{channel_key}.png")
                page.screenshot(path=debug_img)
                tg_photo(debug_img, f"⚠️ <b>{cfg['name']}</b>: Layout não mapeado ou comentários indisponíveis.")
            context.close()
            return

        total_visible = found_buttons.count()
        print(f"[*] {cfg['name']}: {total_visible} botões de resposta detectados.")

        for i in range(total_visible):
            if len(replies_done) >= max_replies:
                break

            btn = found_buttons.nth(i)
            if not btn.is_visible():
                continue

            # Extrai o texto do comentário no bloco correspondente
            try:
                card = btn.locator("xpath=./ancestor::div[contains(@class, 'item') or contains(@class, 'comment') or position() <= 4]").first
                comment_text = card.inner_text() if card.is_visible() else f"comentario_{i}"
            except Exception:
                comment_text = f"comentario_{i}"

            comm_hash = hashlib.md5(comment_text.strip().encode()).hexdigest()
            if not force and comm_hash in mem["answered_hashes"]:
                continue

            try:
                btn.scroll_into_view_if_needed()
                btn.click()
                page.wait_for_timeout(1500)

                input_box = page.locator("div[contenteditable='true'], textarea, input[type='text']").last
                if not input_box.is_visible():
                    continue

                reply = generate_reply(channel_key, comment_text)
                input_box.click()

                # Digitação humanizada
                for char in reply:
                    input_box.type(char, delay=random.randint(25, 55))
                page.wait_for_timeout(1000)

                send_btn = page.locator(
                    "button:has-text('Publicar'), button:has-text('Post'), button:has-text('Enviar'), button:has-text('Reply')"
                ).last
                send_btn.click()
                page.wait_for_timeout(3000)

                mem["answered_hashes"].append(comm_hash)
                clean_orig = comment_text.replace("\n", " ")[:50]
                replies_done.append({"orig": clean_orig, "reply": reply})
                print(f"[+] {cfg['name']} respondido: {reply}")

                time.sleep(random.randint(3, 6))
            except Exception as ex:
                print(f"[!] Erro ao responder comentário individual: {ex}")

        save_memory(mem)
        context.close()

    if replies_done:
        lines = "\n".join([f"• <i>\"{r['orig']}...\"</i>\n  ↳ <b>{r['reply']}</b>" for r in replies_done])
        tg_send(
            f"💬 <b>Buzz Engine Concluído | {cfg['name']}</b>\n\n"
            f"✅ <b>{len(replies_done)} comentários respondidos:</b>\n\n"
            f"{lines}"
        )
    else:
        tg_send(f"ℹ️ <b>{cfg['name']}</b>: Todos os comentários visíveis já foram respondidos anteriormente.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--channel", type=str, default="all", choices=["minuto_bizarro", "insight_de_ouro", "cortes_do_reddit", "all"])
    parser.add_argument("--max", type=int, default=5)
    parser.add_argument("--force", action="store_true", help="Ignora memória e responde mesmo os já registrados")
    args = parser.parse_args()

    channels = ["minuto_bizarro", "insight_de_ouro", "cortes_do_reddit"] if args.channel == "all" else [args.channel]
    for c in channels:
        process_channel(c, max_replies=args.max, force=args.force)
        time.sleep(3)
