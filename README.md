# YT Downloader Local

Petit projet Flask pour télécharger des vidéos YouTube en 1080p ou en MP3 depuis une interface locale.

## Installation

1. Ouvrez un terminal dans le dossier du projet.
2. Créez un environnement virtuel Python :

```powershell
python -m venv .venv
```

3. Activez-le :

```powershell
.\.venv\Scripts\Activate.ps1
```
```
4. Installez les dépendances :

```powershell
pip install -r requirements.txt
```
```

## Exécution

```powershell
python app.py
```

Ouvrez ensuite `http://127.0.0.1:5000` dans votre navigateur.

## Usage

- Collez un lien YouTube.
- Choisissez `Vidéo 1080p` ou `MP3`.
- Cliquez sur `Télécharger`.

## Remarques

- La vidéo est téléchargée localement et renvoyée immédiatement au navigateur.
- La conversion MP3 nécessite `ffmpeg` sur votre machine.
