#!/usr/bin/env python3
"""
Dark Channel Factory - Multi-Channel Autonomous Engine
"""

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
import urllib.request
import urllib.parse
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
CHANNELS_FILE = os.path.join(BASE_DIR, "channels.json")
WORKSPACE_DIR = os.path.join(BASE_DIR, "workspace_dark")
SCENES_DIR = os.path.join(WORKSPACE_DIR, "scenes")
EXPORTS_DIR = os.path.join(BASE_DIR, "exports")
TOKENS_DIR = os.path.join(BASE_DIR, "tokens")
CLIENT_SECRET_FILE = os.path.join(BASE_DIR, "client_secret.json")

os.makedirs(WORKSPACE_DIR, exist_ok=True)
os.makedirs(SCENES_DIR, exist_ok=True)
os.makedirs(EXPORTS_DIR, exist_ok=True)
os.makedirs(TOKENS_DIR, exist_ok=True)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8534172006:AAE_wYmSAkPRv89Ow61kltqc4NAb-JNG2hE")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "2120995649")
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")

def load_channel_config(channel_key: str) -> tuple:
    with open(CHANNELS_FILE, "r", encoding="utf-8-sig") as f:
        channels = json.load(f)
    if channel_key not in channels:
        print(f"[!] Perfil '{channel_key}' nao encontrado. Usando 'quant_paradox'.")
        channel_key = "quant_paradox"
    return channels[channel_key], channel_key

def step_select_topic(channel_cfg: dict, manual_topic: str = None) -> str:
    if manual_topic and manual_topic.strip():
        return manual_topic.strip()
    return random.choice(channel_cfg["topics"])

def step_generate_script(topic: str, channel_cfg: dict, dry_run: bool = False) -> dict:
    print(f"[*] [1/7] Gerando roteiro para '{topic}' [{channel_cfg['name']}]...")
    fallback = {
        "title": f"{topic} #Shorts",
        "description": f"Reflexao e disciplina: {topic}. #shorts #desenvolvimentopessoal",
        "voice_script": "A maior ilusao humana e acreditar que controlamos o mundo exterior. A unica forca que voce realmente governa e a sua propria reacao. Domine sua mente ou ela se tornara sua prisao.",
        "visual_scenes": [
            f"cinematic chiaroscuro antique marble statue {channel_cfg['style_prompt']}",
            f"extreme close up classical sculpture face {channel_cfg['style_prompt']}",
            f"dark dramatic shadows glowing accents {channel_cfg['style_prompt']}",
            f"monumental stone philosophical figure {channel_cfg['style_prompt']}",
            f"impactful atmospheric final revelation {channel_cfg['style_prompt']}"
        ],
        "tags": channel_cfg.get("default_tags", ["shorts"])
    }

    if dry_run or not GEMINI_KEY:
        return fallback

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=GEMINI_KEY)
        prompt = f"""
        Diretriz Editorial: {channel_cfg['system_directive']}
        Tema: '{topic}'
        Estilo visual das imagens: {channel_cfg['style_prompt']}

        Crie um roteiro magnetico de Short em 5 blocos.
        Regras estritas:
        1. Gancho forte nos primeiros 3 segundos sem rodeios.
        2. Sem cliches motivacionais vazios.
        3. Duracao de fala: 38 a 42 segundos (~100 a 115 palavras).
        4. OBRIGATORIO: Finalize com frase marcante e reflexiva.
        5. Forneca 5 prompts visuais descritivos em ingles condizentes com o estilo visual solicitado, sem pessoas vivas/modernas.
        6. Responda ESTRITAMENTE em JSON:
        {{
            "title": "Titulo chamativo com #Shorts",
            "description": "Descricao completa com hashtags",
            "voice_script": "Texto exato da narracao.",
            "visual_scenes": [
                "prompt cena 1",
                "prompt cena 2",
                "prompt cena 3",
                "prompt cena 4",
                "prompt cena 5"
            ],
            "tags": ["tag1", "tag2", "tag3"]
        }}
        """

        for model_name in ["gemini-3.6-flash", "gemini-2.0-flash"]:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(response_mime_type="application/json")
                )
                data = json.loads(response.text)
                if len(data.get("visual_scenes", [])) >= 5:
                    return data
            except Exception:
                time.sleep(2)
    except Exception as e:
        print(f"[!] Erro no Gemini: {e}")

    return fallback

def step_generate_all_scenes(scenes_prompts: list) -> list:
    print("[*] [2/7] Sintetizando 5 cenas visuais...")
    images = []
    for i, prompt_text in enumerate(scenes_prompts[:5]):
        output_img = os.path.join(SCENES_DIR, f"scene_{i}.jpg")
        clean_prompt = urllib.parse.quote(prompt_text)
        success = False

        for attempt in range(1, 4):
            seed_val = int(time.time()) + (i * 149) + attempt
            url = f"https://image.pollinations.ai/prompt/{clean_prompt}?width=1080&height=1920&nologo=true&seed={seed_val}"
            try:
                req = urllib.request.Request(url, headers={'User-Agent': f'Mozilla/5.0 Pipeline/{i}'})
                with urllib.request.urlopen(req, timeout=45) as resp, open(output_img, 'wb') as f:
                    f.write(resp.read())
                images.append(output_img)
                print(f"    [+] Cena {i+1}/5 gerada com sucesso.")
                success = True
                time.sleep(3)
                break
            except Exception:
                time.sleep(3)

        if not success and images:
            shutil.copy(images[-1], output_img)
            images.append(output_img)

    return images

def step_generate_voice(text: str, channel_cfg: dict, output_audio: str, dry_run: bool = False):
    print(f"[*] [3/7] Sintetizando voz ({channel_cfg['voice']})...")
    if not dry_run:
        try:
            import edge_tts
            async def _synthesize():
                comm = edge_tts.Communicate(text, channel_cfg["voice"], rate=channel_cfg.get("voice_rate", "+0%"), pitch="+0Hz")
                await comm.save(output_audio)
            asyncio.run(_synthesize())
            return
        except Exception as e:
            print(f"[!] Falha TTS: {e}")

    cmd = ["ffmpeg", "-y", "-f", "lavfi", "-i", "sine=frequency=440:duration=5", "-c:a", "libmp3lame", output_audio]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

def format_srt_time(seconds: float) -> str:
    millis = int((seconds % 1) * 1000)
    mins, secs = divmod(int(seconds), 60)
    hours, mins = divmod(mins, 60)
    return f"{hours:02}:{mins:02}:{secs:02},{millis:03}"

def step_generate_subtitles(audio_path: str, script_text: str, output_srt: str, dry_run: bool = False) -> float:
    print("[*] [4/7] Transcrevendo e alinhando legendas...")
    exact_audio_dur = 40.0
    try:
        cmd_dur = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", audio_path]
        res = subprocess.run(cmd_dur, capture_output=True, text=True, check=True)
        exact_audio_dur = float(res.stdout.strip())
    except Exception:
        pass

    words_timed = []
    if not dry_run:
        try:
            import whisper
            model = whisper.load_model("tiny")
            result = model.transcribe(audio_path, language="pt", word_timestamps=True)
            for seg in result["segments"]:
                seg_words = seg.get("words", [])
                if seg_words:
                    for w in seg_words:
                        words_timed.append({
                            "word": w["word"].strip().upper(),
                            "start": float(w["start"]),
                            "end": float(w["end"])
                        })
                else:
                    raw = seg["text"].strip().split()
                    step = (seg["end"] - seg["start"]) / max(1, len(raw))
                    for idx, rw in enumerate(raw):
                        words_timed.append({
                            "word": rw.strip().upper(),
                            "start": seg["start"] + idx * step,
                            "end": seg["start"] + (idx + 1) * step
                        })
        except Exception:
            pass

    if not words_timed:
        raw = script_text.replace("\n", " ").split()
        step = (exact_audio_dur - 0.5) / max(1, len(raw))
        for idx, rw in enumerate(raw):
            words_timed.append({
                "word": rw.strip().upper(),
                "start": 0.2 + idx * step,
                "end": 0.2 + (idx + 1) * step
            })

    with open(output_srt, "w", encoding="utf-8", newline="\n") as f:
        for i, item in enumerate(words_timed, start=1):
            s = item["start"]
            if i < len(words_timed):
                next_start = words_timed[i]["start"]
                e = next_start if (next_start - item["end"] < 0.8) else (item["end"] + 0.3)
            else:
                e = item["end"] + 0.4
            f.write(f"{i}\n{format_srt_time(s)} --> {format_srt_time(e)}\n{item['word']}\n\n")

    return exact_audio_dur

def step_render_video(audio_path: str, srt_path: str, images_paths: list, exact_audio_dur: float, channel_cfg: dict, output_video: str):
    print("[*] [5/7] Renderizando vídeo final com enquadramento dinâmico...")
    srt_escaped = srt_path.replace("\\", "/").replace(":", "\\:")
    sub_filter = (
        f"subtitles='{srt_escaped}':force_style="
        f"'Fontname=Impact,Fontsize=24,"
        f"PrimaryColour={channel_cfg['sub_color']},OutlineColour=&H00000000,"
        "BorderStyle=1,Outline=2.5,Shadow=1,Alignment=10'"
    )

    total_video_dur = exact_audio_dur + 2.5
    scene_dur = math.ceil(((total_video_dur + 2.0) / max(1, len(images_paths))) * 10) / 10

    clips_list = []
    concat_file = os.path.join(WORKSPACE_DIR, "concat.txt")

    for i, img_path in enumerate(images_paths):
        clip_out = os.path.join(SCENES_DIR, f"clip_{i}.mp4")
        if i % 2 == 0:
            pan_filter = "scale=1080:1920,zoompan=z='min(zoom+0.0014,1.30)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30"
        else:
            pan_filter = "scale=1080:1920,zoompan=z='if(lte(zoom,1.08),1.30,max(1.08,zoom-0.0014))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30"

        cmd_clip = [
            "ffmpeg", "-y", "-loop", "1", "-t", str(scene_dur),
            "-i", img_path, "-vf", pan_filter, "-c:v", "libx264",
            "-preset", "ultrafast", "-pix_fmt", "yuv420p", clip_out
        ]
        subprocess.run(cmd_clip, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        clips_list.append(clip_out)

    with open(concat_file, "w", encoding="utf-8", newline="\n") as f:
        for c in clips_list:
            f.write(f"file '{c.replace(chr(92), '/')}'\n")

    bg_merged = os.path.join(WORKSPACE_DIR, "bg_merged.mp4")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_file, "-c", "copy", bg_merged],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    cmd_final = [
        "ffmpeg", "-y", "-stream_loop", "-1", "-i", bg_merged, "-i", audio_path,
        "-t", str(total_video_dur), "-vf", sub_filter, "-af", "apad=pad_dur=3.0",
        "-map", "0:v:0", "-map", "1:a:0", "-c:v", "libx264", "-preset", "ultrafast",
        "-crf", "23", "-c:a", "aac", "-b:a", "192k", output_video
    ]
    subprocess.run(cmd_final, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print(f"[+] Renderizacao concluida com sucesso.")

def step_upload_to_youtube(video_path: str, metadata: dict, channel_cfg: dict) -> str:
    if not channel_cfg.get("upload_youtube", True):
        print("[*] [6/7] Upload YouTube desativado para este canal. Pulando...")
        return None

    token_path = os.path.join(BASE_DIR, channel_cfg["token_file"])
    print(f"[*] [6/7] Verificando credenciais do YouTube ({token_path})...")

    if not os.path.exists(CLIENT_SECRET_FILE):
        return None

    try:
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials

        SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
        creds = None

        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(token_path, "w", encoding="utf-8") as t:
                t.write(creds.to_json())

        youtube = build("youtube", "v3", credentials=creds)
        body = {
            "snippet": {
                "title": metadata.get("title", "Insight #Shorts")[:100],
                "description": metadata.get("description", ""),
                "tags": metadata.get("tags", []),
                "categoryId": "27"
            },
            "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False}
        }

        media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")
        request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"    [+] Upload YT: {int(status.progress() * 100)}%")

        vid_id = response.get("id")
        url = f"https://youtube.com/shorts/{vid_id}"
        print(f"[+] Postado com sucesso no YouTube: {url}")
        return url
    except Exception as e:
        print(f"[!] Upload YouTube ignorado: {e}")
        return None

def step_upload_to_tiktok(video_path: str, caption_text: str, channel_cfg: dict, channel_key: str) -> bool:
    print(f"[*] [7/7] Verificando integração TikTok...")
    rel_profile = channel_cfg.get("tiktok_profile", f"tokens/tiktok_profile_{channel_key}")
    profile_dir = os.path.join(BASE_DIR, rel_profile)

    if not os.path.exists(profile_dir):
        print(f"[!] Perfil Chrome TikTok ({profile_dir}) nao encontrado. Upload TikTok pulado.")
        return False

    try:
        from playwright.sync_api import sync_playwright
        print(f"[*] Publicando no TikTok via perfil '{rel_profile}'...")
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

            page.goto("https://www.tiktok.com/tiktokstudio/upload", timeout=60000)
            page.wait_for_timeout(5000)

            file_input = page.locator("input[type='file']").first
            if not file_input.is_visible():
                for frame in page.frames:
                    if frame.locator("input[type='file']").count() > 0:
                        file_input = frame.locator("input[type='file']").first
                        break

            file_input.set_input_files(video_path)
            page.wait_for_timeout(10000)

            # Limpa modais e overlays
            page.keyboard.press("Escape")
            for sel in ["button:has-text('Entendi')", "button:has-text('Aceitar')", "button:has-text('Got it')", "button:has-text('OK')"]:
                try:
                    b = page.locator(sel).first
                    if b.is_visible():
                        b.click(force=True)
                        page.wait_for_timeout(1000)
                except Exception:
                    pass
            page.keyboard.press("Escape")
            page.wait_for_timeout(1500)

            # Preenche a legenda
            caption_box = page.locator("div[contenteditable='true']").first
            caption_box.wait_for(state="visible", timeout=15000)
            caption_box.click(force=True)
            page.wait_for_timeout(500)
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            caption_box.type(caption_text, delay=20)
            page.wait_for_timeout(3000)

            # Publica
            post_btn = page.locator("button:has-text('Publicar'), button:has-text('Post')").first
            post_btn.scroll_into_view_if_needed()
            page.wait_for_timeout(1000)
            post_btn.click(force=True)
            page.wait_for_timeout(15000)

            print("[+] Publicado com sucesso no TikTok!")
            context.close()
            return True
    except Exception as e:
        print(f"[!] Upload TikTok falhou ou pendente: {e}")
        return False

def step_export_distribution(raw_video: str, metadata: dict, channel_key: str) -> dict:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_dir = os.path.join(EXPORTS_DIR, channel_key, timestamp)
    os.makedirs(export_dir, exist_ok=True)

    dest_video = os.path.join(export_dir, "video.mp4")
    shutil.copy(raw_video, dest_video)

    tiktok_txt = os.path.join(export_dir, "tiktok_copy.txt")
    tags_formatted = " ".join([f"#{t}" for t in metadata.get("tags", [])])
    caption_full = f"{metadata.get('title')}\n\n{tags_formatted}"
    with open(tiktok_txt, "w", encoding="utf-8") as f:
        f.write(caption_full)

    return {"export_dir": export_dir, "video_path": dest_video, "caption": caption_full}

def step_send_telegram(metadata: dict, channel_name: str, dist_info: dict, yt_url: str = None, tiktok_ok: bool = False):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return

    yt_part = f"🔗 <b>YouTube:</b> {yt_url}\n" if yt_url else "⚠️ <b>YouTube:</b> Desativado ou pendente.\n"
    tt_part = "✅ <b>TikTok:</b> Publicado automaticamente!\n" if tiktok_ok else "⚠️ <b>TikTok:</b> Salvo localmente.\n"

    msg = (
        f"🎬 <b>Dark Factory - Publicação Realizada</b>\n\n"
        f"📺 <b>Canal:</b> {channel_name}\n"
        f"📌 <b>Título:</b> {metadata.get('title')}\n"
        f"{yt_part}"
        f"{tt_part}"
        f"📁 <b>Pasta Local:</b>\n<code>{dist_info['export_dir']}</code>"
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = urllib.parse.urlencode({"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "HTML"}).encode()
    try:
        req = urllib.request.Request(url, data=payload)
        with urllib.request.urlopen(req, timeout=15):
            pass
    except Exception:
        pass

def run(channel: str = "insight_de_ouro", topic: str = "", dry_run: bool = False):
    channel_cfg, channel_key = load_channel_config(channel)
    active_topic = step_select_topic(channel_cfg, topic)

    print("====================================================================")
    print(f"DARK FACTORY | CANAL: {channel_cfg['name']} | TEMA: {active_topic}")
    print("====================================================================")

    audio_file = os.path.join(WORKSPACE_DIR, "narration.mp3")
    srt_file = os.path.join(WORKSPACE_DIR, "subtitles.srt")
    output_video = os.path.join(WORKSPACE_DIR, "final_render.mp4")

    meta = step_generate_script(active_topic, channel_cfg, dry_run=dry_run)
    images = step_generate_all_scenes(meta.get("visual_scenes", []))
    step_generate_voice(meta["voice_script"], channel_cfg, audio_file, dry_run=dry_run)
    audio_dur = step_generate_subtitles(audio_file, meta["voice_script"], srt_file, dry_run=dry_run)
    step_render_video(audio_file, srt_file, images, audio_dur, channel_cfg, output_video)

    dist_info = step_export_distribution(output_video, meta, channel_key)

    yt_url = None
    tiktok_ok = False
    if not dry_run:
        yt_url = step_upload_to_youtube(output_video, meta, channel_cfg)
        tiktok_ok = step_upload_to_tiktok(dist_info["video_path"], dist_info["caption"], channel_cfg, channel_key)

    step_send_telegram(meta, channel_cfg["name"], dist_info, yt_url, tiktok_ok)
    print(f"[SUCCESS] Ciclo autônomo concluído com sucesso!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--channel", type=str, default="insight_de_ouro", help="quant_paradox | web3_tech | minuto_bizarro | insight_de_ouro")
    parser.add_argument("--topic", type=str, default="", help="Tema opcional")
    parser.add_argument("--dry-run", action="store_true", help="Execucao de teste")
    args = parser.parse_args()

    run(channel=args.channel, topic=args.topic, dry_run=args.dry_run)
