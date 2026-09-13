import os
import sys
import json
import time
import math
import random
import asyncio
import argparse
import subprocess
import shutil
import traceback
import urllib.request
import urllib.parse
from datetime import datetime
from playwright.sync_api import sync_playwright

BASE_DIR = r"D:\dark_factory"
STATE_FILE = os.path.join(BASE_DIR, "reddit_state.json")
PARKOUR_VIDEO = os.path.join(BASE_DIR, "assets", "minecraft", "parkour.mp4")
WORKSPACE_DIR = os.path.join(BASE_DIR, "workspace_reddit")
EXPORTS_DIR = os.path.join(BASE_DIR, "exports", "cortes_do_reddit")
PROFILE_DIR = os.path.join(BASE_DIR, "tokens", "tiktok_profile_cortesdoreddit")

os.makedirs(WORKSPACE_DIR, exist_ok=True)
os.makedirs(EXPORTS_DIR, exist_ok=True)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8534172006:AAE_wYmSAkPRv89Ow61kltqc4NAb-JNG2hE")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "2120995649")

def tg_log(msg: str):
    """Envia log imediato para o Telegram e exibe no console."""
    print(msg)
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = urllib.parse.urlencode({
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg,
        "parse_mode": "HTML"
    }).encode("utf-8")
    try:
        req = urllib.request.Request(url, data=payload)
        with urllib.request.urlopen(req, timeout=10):
            pass
    except Exception as e:
        print(f"[!] Falha no envio ao Telegram: {e}")

def get_video_duration(file_path):
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", file_path]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())

def format_ass_time(seconds: float) -> str:
    cs = int((seconds % 1) * 100)
    mins, secs = divmod(int(seconds), 60)
    hours, mins = divmod(mins, 60)
    return f"{hours}:{mins:02d}:{secs:02d}.{cs:02d}"

def generate_reddit_card(title_pt: str, part_num: str, total_parts: int, output_png: str):
    tg_log("🎨 <b>[1/6]</b> Renderizando Card visual nativo do Reddit...")
    html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
        background: transparent;
        display: flex;
        justify-content: center;
        align-items: center;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }}
    .reddit-card {{
        width: 960px;
        background: #1A1A1B;
        border: 2px solid #343536;
        border-radius: 28px;
        padding: 32px 36px;
        box-shadow: 0 16px 40px rgba(0, 0, 0, 0.65);
        color: #D7DADC;
    }}
    .header {{
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 20px;
    }}
    .avatar {{
        width: 60px;
        height: 60px;
        background: #FF4500;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
    }}
    .avatar svg {{
        width: 38px;
        height: 38px;
        fill: #FFFFFF;
    }}
    .meta-info {{
        display: flex;
        flex-direction: column;
        gap: 4px;
    }}
    .sub-row {{
        display: flex;
        align-items: center;
        gap: 12px;
    }}
    .subreddit {{
        font-size: 26px;
        font-weight: 800;
        color: #FFFFFF;
    }}
    .badge {{
        background: #FF4500;
        color: #FFFFFF;
        font-size: 19px;
        font-weight: 800;
        padding: 4px 14px;
        border-radius: 20px;
        text-transform: uppercase;
    }}
    .user-info {{
        font-size: 21px;
        color: #818384;
    }}
    .title {{
        font-size: 34px;
        font-weight: 700;
        line-height: 1.35;
        color: #F2F4F5;
        margin-bottom: 24px;
        word-wrap: break-word;
    }}
    .footer {{
        display: flex;
        align-items: center;
        gap: 16px;
    }}
    .pill {{
        background: #272729;
        border-radius: 24px;
        padding: 8px 18px;
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 21px;
        font-weight: 600;
        color: #D7DADC;
    }}
    .upvote {{ color: #FF4500; font-weight: 800; }}
</style>
</head>
<body>
<div class="reddit-card" id="card">
    <div class="header">
        <div class="avatar">
            <svg viewBox="0 0 20 20">
                <circle cx="10" cy="10" r="10" fill="#FF4500"/>
                <path d="M16.67 10a1.46 1.46 0 0 0-2.47-1 6.54 6.54 0 0 0-3.85-1.23l.65-3.08 2.14.45a1 1 0 1 0 .91-.77l-2.48-.52a.3.3 0 0 0-.35.23l-.76 3.6a6.6 6.6 0 0 0-4 .19 1.46 1.46 0 1 0-1.84 2.21 3.58 3.58 0 0 0-.08.77c0 2.45 2.82 4.44 6.3 4.44s6.3-2 6.3-4.44a3.53 3.53 0 0 0-.08-.75 1.46 1.46 0 0 0 .61-1.1z" fill="#FFF"/>
            </svg>
        </div>
        <div class="meta-info">
            <div class="sub-row">
                <span class="subreddit">r/relatos</span>
                <span class="badge">PARTE {part_num} DE {total_parts}</span>
            </div>
            <span class="user-info">Enviado por u/anonimo_br • há 4 horas</span>
        </div>
    </div>
    <div class="title">{title_pt}</div>
    <div class="footer">
        <div class="pill"><span class="upvote">▲</span> 14.8k <span style="color:#818384">▼</span></div>
        <div class="pill">💬 892 comentários</div>
        <div class="pill">↗ Compartilhar</div>
    </div>
</div>
</body>
</html>"""

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1080, "height": 800})
        page.set_content(html_content)
        card_el = page.locator("#card")
        card_el.screenshot(path=output_png, omit_background=True)
        browser.close()

def generate_voice(text: str, output_audio: str):
    tg_log("🎙️ <b>[2/6]</b> Sintetizando voz neural pt-BR-AntonioNeural...")
    import edge_tts
    async def _synth():
        comm = edge_tts.Communicate(text, "pt-BR-AntonioNeural", rate="+6%", pitch="+0Hz")
        await comm.save(output_audio)
    asyncio.run(_synth())

def generate_ass_subtitles(audio_path: str, script_text: str, output_ass: str) -> float:
    tg_log("📝 <b>[3/6]</b> Transcrevendo áudio e alinhando legendas dinâmicas...")
    exact_dur = get_video_duration(audio_path)
    words_timed = []

    try:
        import whisper
        model = whisper.load_model("tiny")
        result = model.transcribe(audio_path, language="pt", word_timestamps=True)
        for seg in result.get("segments", []):
            seg_words = seg.get("words")
            if seg_words:
                for w in seg_words:
                    words_timed.append({
                        "word": w["word"].strip().upper(),
                        "start": float(w["start"]),
                        "end": float(w["end"])
                    })
            else:
                raw = seg.get("text", "").strip().split()
                if raw:
                    step = (seg["end"] - seg["start"]) / len(raw)
                    for idx, rw in enumerate(raw):
                        words_timed.append({
                            "word": rw.strip().upper(),
                            "start": seg["start"] + idx * step,
                            "end": seg["start"] + (idx + 1) * step
                        })
    except Exception:
        pass

    if not words_timed:
        raw_words = script_text.replace("\n", " ").split()
        step = (exact_dur - 0.4) / max(1, len(raw_words))
        for idx, rw in enumerate(raw_words):
            words_timed.append({
                "word": rw.strip().upper(),
                "start": 0.2 + idx * step,
                "end": 0.2 + (idx + 1) * step
            })

    chunks = []
    current_chunk = []
    for w in words_timed:
        current_chunk.append(w)
        if len(current_chunk) >= 3 or (w["word"].endswith((".", ",", "!", "?")) and len(current_chunk) >= 2):
            chunks.append({
                "text": " ".join([x["word"] for x in current_chunk]),
                "start": current_chunk[0]["start"],
                "end": current_chunk[-1]["end"]
            })
            current_chunk = []
    if current_chunk:
        chunks.append({
            "text": " ".join([x["word"] for x in current_chunk]),
            "start": current_chunk[0]["start"],
            "end": current_chunk[-1]["end"]
        })

    ass_content = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Impact,64,&H0000FFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,5.0,2.0,2,60,60,520,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    with open(output_ass, "w", encoding="utf-8") as f:
        f.write(ass_content)
        for c in chunks:
            s_str = format_ass_time(c["start"])
            e_str = format_ass_time(c["end"] + 0.15)
            f.write(f"Dialogue: 0,{s_str},{e_str},Default,,0,0,0,,{c['text']}\n")

    return exact_dur

def render_reddit_cut(audio_path, ass_path, card_png, duration, output_video):
    tg_log("🎬 <b>[4/6]</b> Recortando Minecraft Parkour e renderizando vídeo vertical...")
    parkour_dur = get_video_duration(PARKOUR_VIDEO)
    total_dur = duration + 2.0
    
    max_start = max(10, int(parkour_dur - total_dur - 30))
    start_time = random.randint(15, max_start)

    ass_rel = os.path.relpath(ass_path, BASE_DIR).replace("\\", "/")

    filter_complex = (
        "[0:v]scale=3413:1920,crop=1080:1920:(in_w-1080)/2:0[bg];"
        f"[bg][1:v]overlay=(W-w)/2:220[vcard];"
        f"[vcard]subtitles={ass_rel}[outv]"
    )

    cmd = [
        "ffmpeg", "-y", "-ss", str(start_time), "-t", str(total_dur),
        "-i", PARKOUR_VIDEO, "-i", card_png, "-i", audio_path,
        "-filter_complex", filter_complex, "-af", "apad=pad_dur=2.0",
        "-map", "[outv]", "-map", "2:a:0",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22",
        "-c:a", "aac", "-b:a", "192k", output_video
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

def upload_tiktok(video_path, caption_text):
    tg_log("🌐 <b>[5/6]</b> Abrindo TikTok Studio com perfil persistente...")
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
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

        page.goto("https://www.tiktok.com/tiktokstudio/upload", timeout=60000)
        page.wait_for_timeout(5000)

        file_input = page.locator("input[type='file']").first
        if not file_input.is_visible():
            for frame in page.frames:
                if frame.locator("input[type='file']").count() > 0:
                    file_input = frame.locator("input[type='file']").first
                    break

        tg_log("📤 Enviando arquivo MP4 para a plataforma...")
        file_input.set_input_files(video_path)
        page.wait_for_timeout(3000)
        page.keyboard.press("Escape")

        for sel in ["button:has-text('Entendi')", "button:has-text('Got it')", "button:has-text('Aceitar')"]:
            try:
                b = page.locator(sel).first
                if b.is_visible():
                    b.click()
            except Exception:
                pass

        try:
            caption_box = page.locator("div[contenteditable='true']").first
            caption_box.wait_for(state="visible", timeout=25000)
            caption_box.click()
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            caption_box.type(caption_text, delay=20)
            page.wait_for_timeout(2000)
        except Exception:
            pass

        tg_log("⏳ Aguardando processamento dos servidores do TikTok...")
        post_btn = page.locator("button[data-e2e='post_video_button'], button:has-text('Publicar'), button:has-text('Post')").first

        for _ in range(60):
            try:
                aria_dis = post_btn.get_attribute("aria-disabled")
                data_dis = post_btn.get_attribute("data-disabled")
                dis = post_btn.get_attribute("disabled")

                if (aria_dis in [None, "false", ""]) and (data_dis in [None, "false", ""]) and (dis is None):
                    break
            except Exception:
                pass
            time.sleep(2)

        tg_log("🔘 Clicando no botão Publicar...")
        post_btn.scroll_into_view_if_needed()
        page.wait_for_timeout(1000)
        post_btn.click(force=True)

        tg_log("⚠️ Monitorando modal de confirmação ('Publicar agora')...")
        modal_selectors = [
            "button:has-text('Publicar agora')",
            "button:has-text('Publicar mesmo assim')",
            "button:has-text('Post anyway')",
            "button:has-text('Confirmar')"
        ]
        
        for _ in range(15):
            clicked = False
            for sel in modal_selectors:
                btn = page.locator(sel).first
                if btn.is_visible():
                    tg_log(f"✅ Modal detectado! Clicando em: <i>{sel}</i>")
                    btn.click(force=True)
                    clicked = True
                    break
            if clicked:
                break
            time.sleep(1)

        tg_log("⏳ Aguardando tela de confirmação de envio...")
        try:
            page.wait_for_selector(
                "text='Gerenciar vídeos', text='Manage your videos', text='Seu vídeo foi publicado', text='Your video has been uploaded'",
                timeout=30000
            )
            tg_log("🎉 <b>[6/6]</b> Sucesso confirmado: Vídeo publicado oficialmente no TikTok!")
        except Exception:
            tg_log("⚠️ Redirecionamento não explícito, tolerância concluída com segurança.")
            page.wait_for_timeout(8000)

        context.close()
        return True

def run(force_part: int = None, no_upload: bool = False):
    try:
        with open(STATE_FILE, "r", encoding="utf-8-sig") as f:
            state = json.load(f)

        active_series = state.get("active_series", [])
        current_serie = None

        for s in active_series:
            if s["status"] == "in_progress":
                current_serie = s
                break

        if not current_serie:
            tg_log("ℹ️ <b>[Cortes do Reddit]</b> Nenhuma série ativa pendente no momento.")
            return

        part_num = str(force_part if force_part else current_serie["next_part"])
        total_parts = current_serie["total_parts"]
        part_text = current_serie["parts_content"].get(part_num)

        if not part_text:
            tg_log(f"⚠️ <b>[Cortes do Reddit]</b> Texto para a Parte {part_num} não localizado no estado.")
            return

        tg_log(
            f"🚀 <b>Iniciando Cortes do Reddit</b>\n\n"
            f"📖 <b>História:</b> {current_serie['title_pt']}\n"
            f"🔢 <b>Episódio:</b> Parte {part_num} de {total_parts}"
        )

        audio_file = os.path.join(WORKSPACE_DIR, f"audio_p{part_num}.mp3")
        ass_file = os.path.join(WORKSPACE_DIR, f"subs_p{part_num}.ass")
        card_png = os.path.join(WORKSPACE_DIR, f"reddit_card_p{part_num}.png")
        render_file = os.path.join(WORKSPACE_DIR, f"final_p{part_num}.mp4")

        generate_reddit_card(current_serie["title_pt"], part_num, total_parts, card_png)
        generate_voice(part_text, audio_file)
        dur = generate_ass_subtitles(audio_file, part_text, ass_file)
        render_reddit_cut(audio_file, ass_file, card_png, dur, render_file)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest_dir = os.path.join(EXPORTS_DIR, f"{current_serie['id']}_parte_{part_num}_{timestamp}")
        os.makedirs(dest_dir, exist_ok=True)

        dest_video = os.path.join(dest_dir, "video.mp4")
        shutil.copy(render_file, dest_video)

        caption = (
            f"[PARTE {part_num}/{total_parts}] {current_serie['title_pt']}\n\n"
            f"#relatos #historiasdoreddit #redditbrasil #cortesdoreddit #historias #parte{part_num} #{current_serie['id']}"
        )
        with open(os.path.join(dest_dir, "tiktok_copy.txt"), "w", encoding="utf-8") as f:
            f.write(caption)

        if not no_upload:
            upload_tiktok(dest_video, caption)
            if int(part_num) not in current_serie["posted_parts"]:
                current_serie["posted_parts"].append(int(part_num))
            next_p = int(part_num) + 1
            if next_p > total_parts:
                current_serie["status"] = "completed"
                current_serie["next_part"] = None
                tg_log(f"🏆 <b>Série Concluída!</b> Todas as {total_parts} partes foram publicadas.")
            else:
                current_serie["next_part"] = next_p
                tg_log(f"📌 Próximo agendado na fila: <b>Parte {next_p}/{total_parts}</b>")

            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2, ensure_ascii=False)

            tg_log(f"📁 <b>Backup Local:</b>\n<code>{dest_dir}</code>")
        else:
            tg_log(f"✅ <b>Render Local Concluído:</b>\n<code>{dest_video}</code>")

    except Exception as e:
        err_details = traceback.format_exc()
        tg_log(f"❌ <b>ERRO NO PIPELINE REDDIT:</b>\n<code>{err_details[-500:]}</code>")
        raise e

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--part", type=int, default=None)
    parser.add_argument("--no-upload", action="store_true")
    args = parser.parse_args()

    run(force_part=args.part, no_upload=args.no_upload)
