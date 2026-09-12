#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fastfix.py - Push diretto via API GitHub, zero git/rebase/conflitti.
Per modificare file ESISTENTI (css, njk, layout, json) sul repo Eleventy.
Per creare NUOVI articoli/progetti usa publish.py invece.

Uso:
  python fastfix.py get <path_nel_repo>
  python fastfix.py replace <path_nel_repo> "<vecchio_testo>" "<nuovo_testo>"
  python fastfix.py push <path_nel_repo> <path_file_locale> "<messaggio_commit>"
  python fastfix.py delete <path_nel_repo> "<messaggio_commit>"

Esempi:
  python fastfix.py get src/_data/home.json
  python fastfix.py replace src/index.njk "Progetti" "I miei progetti"
"""

import sys
import os
import base64
import json
import urllib.request
import urllib.error

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def load_env():
    env_path = os.path.join(SCRIPT_DIR, ".env")
    env = {}
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def load_config():
    config_path = os.path.join(SCRIPT_DIR, "config.json")
    with open(config_path, encoding="utf-8") as f:
        return json.load(f)


def api_request(method, url, token, data=None):
    headers = {
        "Authorization": "token " + token,
        "Accept": "application/vnd.github+json",
        "User-Agent": "fastfix-script",
    }
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        print("[ERRORE HTTP " + str(e.code) + "] " + err_body)
        sys.exit(1)


def get_file(owner, repo, branch, token, path):
    url = "https://api.github.com/repos/" + owner + "/" + repo + "/contents/" + path + "?ref=" + branch
    data = api_request("GET", url, token)
    content = base64.b64decode(data["content"]).decode("utf-8")
    return content, data["sha"]


def put_file(owner, repo, branch, token, path, new_content, sha, message):
    url = "https://api.github.com/repos/" + owner + "/" + repo + "/contents/" + path
    encoded = base64.b64encode(new_content.encode("utf-8")).decode("utf-8")
    payload = {
        "message": message,
        "content": encoded,
        "branch": branch,
    }
    if sha:
        payload["sha"] = sha
    return api_request("PUT", url, token, payload)


def delete_file(owner, repo, branch, token, path, sha, message):
    url = "https://api.github.com/repos/" + owner + "/" + repo + "/contents/" + path
    payload = {
        "message": message,
        "sha": sha,
        "branch": branch,
    }
    return api_request("DELETE", url, token, payload)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    env = load_env()
    cfg = load_config()
    token = env.get("GITHUB_TOKEN")
    owner, repo, branch = cfg["owner"], cfg["repo"], cfg["branch"]

    comando = sys.argv[1]
    path = sys.argv[2]

    if comando == "get":
        content, sha = get_file(owner, repo, branch, token, path)
        print("--- SHA: " + sha + " ---")
        print(content)

    elif comando == "replace":
        if len(sys.argv) < 5:
            print('Uso: python fastfix.py replace <path> "<vecchio>" "<nuovo>"')
            sys.exit(1)
        old_str, new_str = sys.argv[3], sys.argv[4]
        content, sha = get_file(owner, repo, branch, token, path)
        if old_str not in content:
            print("[ERRORE] Testo da sostituire non trovato in " + path)
            sys.exit(1)
        count = content.count(old_str)
        if count > 1:
            print("[ATTENZIONE] Trovate " + str(count) + " occorrenze, sostituisco tutte")
        new_content = content.replace(old_str, new_str)
        put_file(owner, repo, branch, token, path, new_content, sha, "fastfix: " + path)
        print("[OK] " + path + " aggiornato (" + str(count) + " sostituzioni)")

    elif comando == "push":
        if len(sys.argv) < 5:
            print('Uso: python fastfix.py push <path_repo> <path_locale> "<messaggio>"')
            sys.exit(1)
        local_path, message = sys.argv[3], sys.argv[4]
        with open(local_path, encoding="utf-8") as f:
            new_content = f.read()
        sha = None
        try:
            _, sha = get_file(owner, repo, branch, token, path)
        except SystemExit:
            sha = None
        put_file(owner, repo, branch, token, path, new_content, sha, message)
        print("[OK] " + path + " caricato da " + local_path)

    elif comando == "delete":
        if len(sys.argv) < 4:
            print('Uso: python fastfix.py delete <path> "<messaggio>"')
            sys.exit(1)
        message = sys.argv[3]
        _, sha = get_file(owner, repo, branch, token, path)
        delete_file(owner, repo, branch, token, path, sha, message)
        print("[OK] " + path + " eliminato")

    else:
        print("Comando sconosciuto: " + comando)
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
