# LearnPath

Personal IT learning platform — Networks, Systems, Security, Programming, Cloud & Certifications.

## Parcours disponibles

- 🌐 **Réseaux** — OSI, TCP/IP, DNS, DHCP, Routage, VPN...
- 🖥️ **Systèmes** — Linux, Windows Server, Active Directory, Virtualisation...
- 🔒 **Cybersécurité** — Cryptographie, Pentest, OWASP, Forensics, EDR...
- 💻 **Langages** — Python, Bash, PowerShell, SQL, Git...
- ☁️ **Cloud** — Azure, AWS, IaaS/PaaS/SaaS...
- 🏆 **Certifications** — CCNA, CompTIA Security+/Network+, AZ-900, CEH...

## Fonctionnalités

- 📖 Cours structurés par niveaux progressifs
- ✅ Quiz interactifs avec feedback immédiat
- 🃏 Flashcards recto/verso
- 🔬 Labs pratiques avec terminal simulé
- ⏱️ Examens blancs chronométrés type certif
- 📊 Suivi de progression + XP + niveaux

## Stack

Flask 3.x · SQLAlchemy · SQLite · Jinja2 · TailwindCSS · highlight.js

## Setup

```bash
git clone https://github.com/Kiwi6212/learnpath
cd learnpath
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

## Deploy

Served via Gunicorn on port 8083, managed by systemd. Independent from other services.

## License

MIT
