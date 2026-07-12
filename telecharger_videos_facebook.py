#!/usr/bin/env python3
"""Télécharge deux vidéos Facebook avec yt-dlp et FFmpeg.

Utilisez ce script uniquement si vous possédez les droits nécessaires sur les
vidéos ou l'autorisation de leur propriétaire.
"""

from __future__ import annotations

import argparse
from collections import deque
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys


URLS = (
    "https://www.facebook.com/100011158635699/videos/pcb.2775007999547794/1382969080366058",
    "https://www.facebook.com/100011158635699/videos/pcb.2775007999547794/1525461309612448",
)

BASE_DIR = Path(__file__).resolve().parent
VIDEO_DIR = BASE_DIR / "videos"
DEFAULT_COOKIES_FILE = BASE_DIR / "cookies.txt"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Télécharge les deux vidéos Facebook autorisées dans le dossier videos."
    )
    parser.add_argument(
        "--cookies",
        type=Path,
        help=(
            "Chemin d'un fichier cookies.txt au format Netscape. "
            "Sans cette option, le script utilise cookies.txt placé à côté du script, s'il existe."
        ),
    )
    return parser.parse_args()


def find_cookies_file(requested_file: Path | None) -> Path | None:
    if requested_file is not None:
        cookies_file = requested_file.expanduser().resolve()
        if not cookies_file.is_file():
            raise FileNotFoundError(f"Fichier de cookies introuvable : {cookies_file}")
        return cookies_file

    if DEFAULT_COOKIES_FILE.is_file():
        return DEFAULT_COOKIES_FILE

    return None


def explain_failure(output_lines: deque[str]) -> None:
    details = "\n".join(output_lines)
    lowered = details.lower()

    if any(
        marker in lowered
        for marker in (
            "login required",
            "log in",
            "not logged in",
            "private video",
            "cookies",
            "checkpoint",
            "not authorized",
        )
    ):
        print(
            "Cause probable : la vidéo exige une connexion Facebook, est privée, "
            "ou votre compte n'est pas autorisé. Exportez vos cookies dans cookies.txt "
            "et vérifiez que votre compte peut ouvrir la vidéo dans le navigateur."
        )
    elif any(
        marker in lowered
        for marker in (
            "video unavailable",
            "content isn't available",
            "content is not available",
            "removed",
            "deleted",
            "does not exist",
            "not found",
        )
    ):
        print(
            "Cause probable : la vidéo a été supprimée, n'existe plus, ou n'est pas "
            "accessible à votre compte ou dans votre région."
        )
    elif "unsupported url" in lowered:
        print(
            "Cause probable : cette URL Facebook n'est pas reconnue par la version "
            "installée de yt-dlp. Mettez yt-dlp à jour puis réessayez."
        )
    elif "ffmpeg" in lowered and any(
        marker in lowered for marker in ("not found", "not installed", "error")
    ):
        print(
            "Cause probable : FFmpeg est absent, mal installé ou inaccessible dans le PATH."
        )
    elif any(marker in lowered for marker in ("http error 403", "forbidden")):
        print(
            "Cause probable : Facebook refuse l'accès. Des cookies valides et un compte "
            "autorisé peuvent être nécessaires."
        )
    else:
        print(
            "Cause indéterminée : vérifiez l'URL, votre connexion, les droits d'accès "
            "et mettez yt-dlp à jour."
        )

    error_lines = [line for line in output_lines if "error" in line.lower()]
    if error_lines:
        print("Dernier message d'erreur de yt-dlp :")
        for line in error_lines[-3:]:
            print(f"  {line}")


def download_video(url: str, number: int, cookies_file: Path | None) -> bool:
    command = [
        sys.executable,
        "-m",
        "yt_dlp",
        "--no-playlist",
        "--format",
        "bestvideo*+bestaudio/best",
        "--merge-output-format",
        "mp4",
        "--remux-video",
        "mp4",
        "--paths",
        str(VIDEO_DIR),
        "--output",
        "%(title).160B [%(id)s].%(ext)s",
        "--windows-filenames",
        "--trim-filenames",
        "190",
        "--no-overwrites",
        "--continue",
        "--progress",
        "--newline",
        "--progress-delta",
        "1",
        "--print",
        "after_move:Fichier final : %(filepath)s",
    ]

    if cookies_file is not None:
        command.extend(("--cookies", str(cookies_file)))

    command.append(url)

    print("\n" + "=" * 78)
    print(f"Vidéo {number}/{len(URLS)}")
    print(f"URL : {url}")
    print("Démarrage du téléchargement...")

    recent_output: deque[str] = deque(maxlen=50)
    environment = os.environ.copy()
    environment.setdefault("PYTHONUTF8", "1")

    try:
        process = subprocess.Popen(
            command,
            cwd=BASE_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            env=environment,
        )

        assert process.stdout is not None
        for raw_line in process.stdout:
            line = raw_line.rstrip()
            if line:
                recent_output.append(line)
                print(line, flush=True)

        return_code = process.wait()
    except OSError as error:
        print(f"ERREUR : impossible de lancer yt-dlp : {error}")
        return False

    if return_code == 0:
        print(f"RÉUSSITE : la vidéo {number} a été traitée sans écraser de fichier existant.")
        return True

    print(f"ERREUR : échec de la vidéo {number} (code de sortie {return_code}).")
    explain_failure(recent_output)
    print("Le script continue avec la vidéo suivante.")
    return False


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")

    print("Téléchargeur Facebook avec yt-dlp")
    print(
        "À utiliser uniquement avec les droits nécessaires ou l'autorisation du propriétaire."
    )

    if importlib.util.find_spec("yt_dlp") is None:
        print(
            "ERREUR : le module yt-dlp n'est pas installé.\n"
            "Installez-le avec : py -m pip install --upgrade yt-dlp"
        )
        return 2

    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path is None:
        print(
            "ERREUR : FFmpeg est introuvable dans le PATH.\n"
            "Installez FFmpeg, ajoutez son dossier bin au PATH, fermez puis rouvrez "
            "PowerShell, et vérifiez avec : ffmpeg -version"
        )
        return 2

    try:
        cookies_file = find_cookies_file(parse_args().cookies)
    except FileNotFoundError as error:
        print(f"ERREUR : {error}")
        return 2

    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Dossier de destination : {VIDEO_DIR}")
    print(f"FFmpeg détecté : {ffmpeg_path}")
    if cookies_file is None:
        print(
            "Cookies : aucun fichier utilisé (les vidéos nécessitant une connexion peuvent échouer)."
        )
    else:
        print(f"Cookies : utilisation de {cookies_file} (contenu jamais affiché).")

    successes = 0
    for number, url in enumerate(URLS, start=1):
        if download_video(url, number, cookies_file):
            successes += 1

    failures = len(URLS) - successes
    print("\n" + "=" * 78)
    print(f"Bilan : {successes} réussite(s), {failures} échec(s).")
    print(f"Vidéos disponibles dans : {VIDEO_DIR}")

    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
