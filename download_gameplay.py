import os
import sys
import yt_dlp

OUTPUT_DIR = r"D:\dark_factory\assets\minecraft"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "parkour.mp4")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Gameplay de Minecraft Parkour livre de copyright (Creative Commons / Free to use)
VIDEO_URL = "https://www.youtube.com/watch?v=intRX7BRA90"

ydl_opts = {
    'format': 'bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'outtmpl': OUTPUT_FILE,
    'overwrites': True,
    'quiet': False,
    'no_warnings': True,
}

print("=" * 65)
print("[*] BAIXANDO GAMEPLAY DE MINECRAFT PARKOUR")
print("=" * 65)
print(f"[*] Destino: {OUTPUT_FILE}")
print("[*] Baixando video base em alta definicao...")

try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([VIDEO_URL])
    
    if os.path.exists(OUTPUT_FILE):
        file_size_mb = os.path.getsize(OUTPUT_FILE) / (1024 * 1024)
        print(f"\n[+] Gameplay salvo com sucesso! Tamanho: {file_size_mb:.2f} MB")
    else:
        print("[!] O arquivo nao foi localizado apos o download.")
except Exception as e:
    print(f"[!] Erro no download automatico: {e}")
