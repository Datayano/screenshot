# Screenshot Automation

Ce script Python permet de capturer automatiquement des captures d’écran (desktop et mobile) d’une page web, tout en contournant les popups de consentement (cookies, bannières) et en simulant un comportement plus humain grâce à des headers aléatoires.

---

## 📋 Prérequis

- **Python 3.8+** installé dans l’environnement virtuel.  
- **Navigateur Chrome ou Chromium** présent sur la machine (nécessaire pour que ChromeDriver dispose d’un binaire de navigateur). Selenium Manager gère automatiquement le téléchargement et la mise à jour du **ChromeDriver**, mais **n’installe pas** le navigateur lui-même.  
- Accès au terminal / shell.

---

## ⚙️ Installation

1. **Cloner le dépôt** (ou copier `screenshot.py` et `requirements.txt`) :
   ```bash
   git clone https://github.com/Datayano/screenshot.git
   cd screenshot
2. **Créer et activer un environnement virtuel** :
```bash
python3 -m venv venv
source venv/bin/activate     # macOS/Linux
# ou sous Windows PowerShell :
# venv\\Scripts\\Activate.ps1
```
3. **Installer les dépendances via requirements.txt** :
```bash
pip install -r requirements.txt
```

## 📦 Fichier requirements.txt :
```bash
selenium>=4.6.0
```
(Seul le package Selenium est nécessaire ; tout le reste fait partie de la bibliothèque standard Python.)


## 🚀 Utilisation

```bash
# Format général
python screenshot.py <URL> [-o <dossier_de_sortie>]

# Exemples :
python screenshot.py https://www.example.com
python screenshot.py https://www.example.com -o ./shots
```
<URL> : l’adresse de la page à capturer.

-o, --out : dossier de sortie (par défaut .).

Le script génère deux fichiers PNG dans le dossier spécifié :

<nom_de_domaine>_desktop.png (1920×1080)

<nom_de_domaine>_mobile.png (390×844)


## 🔧 Détails du script

Randomisation des headersChaque exécution génère :

un User-Agent aléatoire (Chrome, Firefox, Safari, Edge)…

un Accept-Language aléatoire (FR, EN, DE…)afin de réduire le fingerprinting.

Contournement des popupsRecherche et clic sur tout élément cliquable (bouton, lien, input) dont le texte ou la valeur contient des mots-clés de refus (refuser, decline, continuer sans accepter, skip, etc.).

Masquage de SeleniumExclusion des flags enable-automation, useAutomationExtension, override de navigator.webdriver et autres propriétés JS.

CDP pour headersInjection des headers via le Chrome DevTools Protocol (Network.setExtraHTTPHeaders).

## 🔄 Personnalisation

Ajouter des patternsDans RE_PATTERNS, complétez la liste des regex pour gérer d’autres textes de popups.

Changer les dimensionsModifiez les appels snap(..., width, height, ...) si vous souhaitez d’autres résolutions.

ProxyPour éviter une IP blacklistée, ajoutez un argument Chrome :
``` python
opts.add_argument('--proxy-server=http://MON_PROXY:PORT')
```

❓ Dépannage

Popup non détectée : inspectez le DOM, identifiez le texte exact ou la structure, et ajoutez un pattern ou un sélecteur CSS.

Slider / CAPTCHA : Selenium seul ne le résout pas. Il faut simuler un glisser-déposer ou utiliser un service tiers (2Captcha, Anti-Captcha, etc.).

Erreurs ChromeDriver : assurez-vous d’utiliser Selenium ≥ 4.6 (Selenium Manager gère ChromeDriver automatiquement).

📄 Licence

MIT © WorldModelia