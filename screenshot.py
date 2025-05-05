#!/usr/bin/env python3
"""
Capture desktop + mobile d’une page,
et ferme tout popup de consentement en cherchant
un bouton/liens au texte "refuser"/"decline"/etc.
Saisie en full-page (hauteur totale) pour screenshot.
"""
import argparse, os, time, random, re, urllib.parse

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# 1) Patterns génériques de "refus"
RE_PATTERNS = [
    re.compile(r"continuer\s+sans\s+accepter"),
    re.compile(r"\brefuser\b"),
    re.compile(r"\bdecline\b"),
    re.compile(r"\breject\b"),
    re.compile(r"\bskip\b"),
    re.compile(r"\bpasser\b"),
    re.compile(r"no\s+thanks"),
]

# Exemple d'User-Agents et langues
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:114.0) Gecko/20100101 Firefox/114.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.0.0",
]
LANGUAGES = [
    "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
    "en-US,en;q=0.9,fr-FR;q=0.8",
    "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
]

def random_headers() -> dict:
    """Retourne un petit jeu de headers aléatoires."""
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": random.choice(LANGUAGES),
        "Accept": ("text/html,application/xhtml+xml,"  
                   "application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"),
    }

def safe_name(url: str) -> str:
    return urllib.parse.urlparse(url).netloc.replace(":", "_") or "site"


def make_driver(w: int, h: int, headers: dict):
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument(f"--window-size={w},{h}")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    opts.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(options=opts)
    # inject headers via CDP
    driver.execute_cdp_cmd("Network.enable", {})
    driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": headers})
    # override JS fingerprints
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
          Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
          Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3]});
          Object.defineProperty(navigator, 'languages', {get: () => %s});
        """ % repr(headers["Accept-Language"].split(","))
    })
    return driver


def close_consent_popup(driver) -> bool:
    elems = driver.find_elements(By.XPATH,
        "//button | //a | //input[@type='button'] | //input[@type='submit']"
    )
    for el in elems:
        try:
            text = el.text.strip() or el.get_attribute("value") or ""
            low = text.lower()
            for pat in RE_PATTERNS:
                if pat.search(low):
                    driver.execute_script("arguments[0].scrollIntoView(true);", el)
                    el.click()
                    time.sleep(1)
                    return True
        except Exception:
            continue
    return False


def snap(url: str, w: int, h: int, tag: str, out_dir: str):
    headers = random_headers()
    print(f"[DEBUG] Headers : {headers}")
    driver = make_driver(w, h, headers)
    driver.get(url)
    # fermer popup si présent
    if close_consent_popup(driver):
        print("→ Consent popup fermé.")
    else:
        print("→ Aucun popup détecté.")

    # Calcul de la hauteur totale du document
    total_height = driver.execute_script(
        "return Math.max(document.body.scrollHeight,"
        "document.documentElement.scrollHeight,"
        "document.body.offsetHeight,"
        "document.documentElement.offsetHeight,"
        "document.documentElement.clientHeight);"
    )
    # Ajuster la fenêtre pour capturer full page
    driver.set_window_size(w, total_height)
    time.sleep(1)

    fn = f"{safe_name(url)}_{tag}.png"
    out = os.path.join(out_dir, fn)
    driver.save_screenshot(out)
    driver.quit()
    return out


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("url")
    p.add_argument("-o","--out",default=".")
    a = p.parse_args()
    os.makedirs(a.out, exist_ok=True)
    print("Desktop :", snap(a.url, 1920,1080,"desktop", a.out))
    print("Mobile  :", snap(a.url,  390, 844,"mobile",  a.out))
