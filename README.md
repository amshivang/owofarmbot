<div align="center">

  <p>
    <a href="https://github.com/amshivang"><strong>Shivang Shukla (@amshivang)</strong></a> • 
    <a href="https://github.com/amshivang?tab=repositories">Portfolio Repositories</a> • 
    <a href="mailto:linkwithshivang@gmail.com">Contact</a>
  </p>

  # 🤖 OwO Auto Bot (Desktop)
  ### High-Performance Desktop Automation Console for Discord OwO

  <p>
    <em>A desktop automation dashboard for Discord OwO bot interactions, featuring humanized Gaussian jitter timing, real-time WebSocket event streaming, and automated captcha emergency halting.</em>
  </p>

  <p>
    <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.11"/></a>
    <a href="https://github.com/dolfies/discord.py-self"><img src="https://img.shields.io/badge/Engine-discord.py--self-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord Engine"/></a>
    <a href="#"><img src="https://img.shields.io/badge/GUI-pywebview%20%2B%20Fluent-0284C7?style=for-the-badge&logo=windows11&logoColor=white" alt="Fluent GUI"/></a>
    <a href="https://github.com/amshivang/owofarmbot/releases"><img src="https://img.shields.io/badge/Distribution-Standalone%20EXE-059669?style=for-the-badge" alt="Distribution"/></a>
    <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-EAB308?style=for-the-badge" alt="License: MIT"/></a>
  </p>

  <p>
    <a href="#-overview">Overview</a> •
    <a href="#-key-features">Key Features</a> •
    <a href="#-how-it-works">How It Works</a> •
    <a href="#-architecture--tech-stack">Tech Stack</a> •
    <a href="#-installation--setup">Setup Guide</a> •
    <a href="#-safety--disclaimer">Disclaimer</a> •
    <a href="#-author--connect">Author</a>
  </p>

</div>

---

## 📌 Overview

**OwO Auto Bot** is a high-performance, standalone Windows desktop application engineered to streamline and automate repetitive interactions with the popular Discord OwO economy bot.

Rather than relying on clunky keyboard macros or fragile browser screen-scraping extensions, OwO Auto Bot operates at the protocol level. It establishes asynchronous WebSocket connections using `discord.py-self`, analyzes Discord Gateway events in real-time, injects dynamic typing simulations with humanized Gaussian delay curves, and displays a live, responsive dashboard inside a native Fluent Dark GUI.

---

## ✨ Key Features

- **⚡ Intelligent Farm & Hunt Loop**: Dispatches automated `owo h` (hunt) and `owo b` (battle) routines with smart gem auto-equipping to maximize loot yield.
- **🚨 Automated Captcha Detection & Emergency Stop**: Actively intercepts incoming Direct Messages and server channel mentions from the OwO bot. The moment a captcha challenge is detected, all automation halts instantly with sound alerts to protect the account from bans.
- **📊 Real-Time WebSocket Event Console**: Streams Discord channel responses, loot drops, currency gains, and balance updates live into the desktop dashboard with smooth, jump-free autoscrolling.
- **🎲 Integrated Gambling & Multiplier Subroutines**: Automated coinflip (`cf`) and slots (`s`) routines with strict stop-loss limits and customizable cycle intervals.
- **🙏 Automated Multiplier Maintenance**: Automates `owo pray` / `owo curse` targeting self or designated user IDs with configurable repetition counters.
- **🪟 Standalone Executable Distribution**: Distributed as a single, portable Windows binary (`OwO_Auto_Bot.exe`) requiring zero Python installation.

---

## ⚡ How It Works

```
  ┌─────────────────────────────────┐
  │   OwO Auto Bot Desktop GUI      │
  │   (pywebview + aiohttp backend) │
  └────────────────┬────────────────┘
                   │ User Config & Live Logs
                   ▼
  ┌─────────────────────────────────┐
  │   Asynchronous Dispatch Loop    │
  │   - Gaussian Jitter Timing      │
  │   - Humanized Typing Latency    │
  └────────────────┬────────────────┘
                   │
                   ▼
  ┌─────────────────────────────────┐
  │   Discord Gateway (WebSocket)   │
  │   via discord.py-self           │
  └────────────────┬────────────────┘
                   │
       ┌───────────┴───────────┐
       ▼                       ▼
  [ Send Commands ]     [ Intercept Gateway Events ]
  - owo hunt                   │
  - owo battle                 ▼
  - owo pray           [ Captcha Check ]
                         │
                         ├──► Captcha Detected? ──► [ EMERGENCY HALT & ALARM ]
                         └──► Normal Loot/Drops ──► [ Stream to Dashboard ]
```

1. **Gaussian Delay Distribution**: Commands never fire on rigid mathematical intervals. A dynamic Gaussian offset is applied to every cycle (e.g. 15.0s target ± 1.8s variance) to emulate human irregularity.
2. **Dynamic Typing Emulation**: Before payload transmission, the bot signals Discord's typing API endpoint with duration proportional to command string length.
3. **Gateway Event Filtering**: Incoming messages are parsed concurrently. If the OwO bot mentions the user with verification prompts, the state machine switches immediately to `EMERGENCY_STOP`.

---

## 🛠️ Architecture & Tech Stack

| Component / Layer | Technology | Architectural Role & Rationale |
| :--- | :--- | :--- |
| **Core Protocol Engine** | `discord.py-self` | Manages Discord Gateway WebSockets, user token authentication & event listeners |
| **GUI Framework** | `pywebview` | Embeds modern HTML/CSS interface directly into a native Windows desktop frame |
| **Local Inter-Process Bridge**| `aiohttp` | Lightweight asynchronous local webserver bridging Python core with frontend UI |
| **Terminal Formatting** | `colorama` | Formats and color-codes internal log levels, alerts, and debug information |
| **Binary Packaging** | PyInstaller | Compiles entire runtime, dependencies, and web assets into a single `.exe` |

---

## 🚀 Installation & Setup

### 1. Download Standalone Executable
Download the latest pre-compiled build (`OwO_Auto_Bot.exe`) from the [Releases](https://github.com/amshivang/owofarmbot/releases) section. No Python installation is needed.

### 2. Extract Discord User Authorization Token
1. Open Discord in your desktop browser (Chrome, Edge, or Brave).
2. Press <kbd>F12</kbd> (or <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>I</kbd>) to open Developer Tools.
3. Select the **Network** tab.
4. Send any test message in a channel (e.g. "test").
5. Click on the `messages` network entry, navigate to **Request Headers**, and locate the `Authorization` header.
6. Copy the alphanumeric token value.

### 3. Launch and Automate
1. Run `OwO_Auto_Bot.exe`.
2. Paste your authorization token into the secure credential field.
3. Configure your desired hunting cycles, gambling limits, and channels.
4. Click **Start Farmbot** to initiate the live automation console.

---

## ⚠️ Safety & Disclaimer

> **Important Notice:** Self-botting violates Discord's Terms of Service. Automating user account actions carries inherent risks of account suspension or termination by Discord. This project is published strictly for educational research into asynchronous WebSocket protocols and client automation. Use responsibly and at your own risk.

---

## 📜 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.

---

## 👤 Author & Connect

<div align="center">
  <p><strong>Shivang Shukla</strong></p>
  <p><em>Cybersecurity & Digital Forensics Scholar</em></p>

  <p>
    <a href="https://github.com/amshivang"><img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub"/></a>
    <a href="https://www.linkedin.com/in/amshivang/"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn"/></a>
    <a href="mailto:linkwithshivang@gmail.com"><img src="https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white" alt="Email"/></a>
  </p>

  <a href="https://buymeacoffee.com/amshivang">
    <img src="https://raw.githubusercontent.com/amshivang/amshivang/main/qr-code.png" alt="Buy Me A Coffee" width="180">
  </a>
  <br>
  <strong><a href="https://buymeacoffee.com/amshivang">☕ Support my open-source work on Buy Me A Coffee!</a></strong>
</div>
