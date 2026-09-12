#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
publish.py - Automazione pubblicazione contenuti sito Eleventy
(cialdecompatibili-netizen/eleventy-template1)

Uso:
  python publish.py articolo "Titolo" "riassunto" "corpo in markdown" [tag1,tag2]
  python publish.py progetto "Titolo" "emoji" "riassunto" "corpo in markdown" [tag1,tag2]

Cosa fa:
  1. Genera lo slug dal titolo
  2. Crea il file .md in src/posts/ o src/projects/ con front matter corretto
  3. git add + commit + push automatico
  4. Stampa l'URL live (GitHub Actions impiega 1-2 minuti a pubblicare)

Per FIX su file esistenti (css, njk, layout) usa fastfix.py invece.
"""

import sys
import os
import re
import subprocess
import datetime

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS_DIR = os.path.join(REPO_DIR, "src", "posts")
PROJECTS_DIR = os.path.join(REPO_DIR, "src", "projects")


def slugify(title):
    slug = title.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    return slug.strip("-")


def now_iso():
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")


def git_run(*args):
    result = subprocess.run(
        ["git"] + list(args),
        cwd=REPO_DIR,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print("[ERRORE git " + " ".join(args) + "]")
        print(result.stderr)
        sys.exit(1)
    return result.stdout.strip()


def _commit_and_push(message):
    git_run("add", "-A")
    status = git_run("status", "--porcelain")
    if not status:
        print("[INFO] Nessuna modifica da committare")
        return
    git_run("commit", "-m", message)
    git_run("push")
    print("[OK] Push completato")


def publish_articolo(titolo, riassunto, corpo, tags=None):
    slug = slugify(titolo)
    filepath = os.path.join(POSTS_DIR, slug + ".md")
    if os.path.exists(filepath):
        print("[ERRORE] Esiste gia' un articolo con slug '" + slug + "'")
        sys.exit(1)

    tags = tags or ["tech"]
    tags_yaml = "\n".join("  - " + t.strip() for t in tags)

    content = "---\n"
    content += "title: " + titolo + "\n"
    content += "date: " + now_iso() + "\n"
    content += "summary: " + riassunto + "\n"
    content += "tags:\n" + tags_yaml + "\n"
    content += "---\n"
    content += corpo + "\n"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print("[OK] Creato " + filepath)
    _commit_and_push("Nuovo articolo: " + titolo)
    print("[LIVE tra 1-2 min] https://cialdecompatibili-netizen.github.io/eleventy-template1/blog/")


def publish_progetto(titolo, emoji, riassunto, corpo, tags=None):
    slug = slugify(titolo)
    filepath = os.path.join(PROJECTS_DIR, slug + ".md")
    if os.path.exists(filepath):
        print("[ERRORE] Esiste gia' un progetto con slug '" + slug + "'")
        sys.exit(1)

    tags = tags or ["web"]
    tags_yaml = "\n".join("  - " + t.strip() for t in tags)

    content = "---\n"
    content += "title: " + titolo + "\n"
    content += "emoji: " + emoji + "\n"
    content += "date: " + now_iso() + "\n"
    content += "summary: " + riassunto + "\n"
    content += "tags:\n" + tags_yaml + "\n"
    content += "---\n"
    content += corpo + "\n"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print("[OK] Creato " + filepath)
    _commit_and_push("Nuovo progetto: " + titolo)
    print("[LIVE tra 1-2 min] https://cialdecompatibili-netizen.github.io/eleventy-template1/projects/")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    comando = sys.argv[1]

    if comando == "articolo":
        if len(sys.argv) < 5:
            print('Uso: python publish.py articolo "Titolo" "riassunto" "corpo" [tag1,tag2]')
            sys.exit(1)
        titolo, riassunto, corpo = sys.argv[2], sys.argv[3], sys.argv[4]
        tags = sys.argv[5].split(",") if len(sys.argv) > 5 else None
        publish_articolo(titolo, riassunto, corpo, tags)

    elif comando == "progetto":
        if len(sys.argv) < 6:
            print('Uso: python publish.py progetto "Titolo" "emoji" "riassunto" "corpo" [tag1,tag2]')
            sys.exit(1)
        titolo, emoji, riassunto, corpo = sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
        tags = sys.argv[6].split(",") if len(sys.argv) > 6 else None
        publish_progetto(titolo, emoji, riassunto, corpo, tags)

    else:
        print("Comando sconosciuto: " + comando)
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
