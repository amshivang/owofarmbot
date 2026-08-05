# OwO Auto Bot (Desktop)

![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![Security](https://img.shields.io/badge/Security-100%25%20Offline%20Air--Gapped-brightgreen.svg)
![UI](https://img.shields.io/badge/UI-Windows%2011%20Fluent%20Dark-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

A highly optimized, elegant desktop automation console for OwO on Discord.

## Features
- **Intelligent Farm Loop & Auto Gems:** Automatically runs `owo h` and `owo b` commands. Smartly equips the highest-tier hunting gems from your inventory to maximize yields and automate setup.
- **Auto Captcha Detection & Stopping:** Actively monitors direct messages and channel responses for OwO captchas. Instantly halts all automation immediately to protect your account.
- **Real-time Websocket Logs:** Streams bot events and Discord channel logs directly to your dashboard in real-time, featuring smooth, jump-free auto-scrolling.
- **Integrated Gambling:** Play coinflip (`cf`) and slots (`s`) automatically with custom base amounts integrated alongside your primary farm cycles.
- **Pray or Curse:** Run pray or curse commands targeting yourself or others to maintain active multipliers, with customizable repetition limits.

---

## Step-by-Step Installation & Usage Guide

### 1. Download the App
Go to the [Releases](../../releases) tab on the right side of this repository and download the latest version of `OwO Auto Bot.exe`. No installation is required—just save it to a folder and double-click to run!

### 2. Extract your Discord Token
To allow the bot to automate tasks on your behalf, you need to provide it with your personal Discord authorization token. 

1. Open Discord in your web browser (Chrome, Edge, or Firefox).
2. Press `F12` on your keyboard to open the **Developer Tools**.
3. Go to the **Network** tab at the top of the tools window.
4. Send a message in any Discord channel (like "hi").
5. In the Network tab, look for a request named `messages`. Click on it.
6. Scroll down to the **Request Headers** section and look for the word `Authorization`.
7. Copy the long random text next to it. That is your token!

*(If this feels too technical or confusing, simply head over to YouTube and search for **"How to find Discord User Token"** for an easy video tutorial!)*

### 3. Configure and Farm
1. Open `OwO Auto Bot.exe`.
2. Paste your copied token into the main input box.
3. Once verified, configure your custom gambling and limit settings.
4. Click **START FARMBOT** and watch the magic happen in the live console!

---

## How It Works

### The Automation Cycle
OwO Auto Bot relies on a highly sophisticated, jitter-based asynchronous event loop:
1. **Humanized Delays:** The bot never operates on a perfectly rigid timer. If the base delay is set to 15 seconds, it applies a randomized Gaussian offset to every cycle, ensuring actions happen unpredictably (e.g., 14.8s, 16.2s, 15.4s) to mimic real human interaction and evade bot detection.
2. **Command Dispatch:** During a single farm loop, the bot processes the primary `owo h` (hunt) and `owo b` (battle) commands. It automatically checks your active inventory to equip the highest-tier hunting gems available before dispatching the hunt command.
3. **Sub-Routines:** In parallel to the main farm loop, asynchronous sub-routines evaluate if gambling (`cf`/`s`) or status (`pray`/`curse`) commands are eligible to run based on your custom configuration limits.

### How Messages Are Sent
The bot does **not** rely on injecting scripts into your browser or simulating physical keyboard presses (like a macro). Instead, it communicates entirely via **Discord's API endpoints and WebSockets**:
- When a command is triggered, the bot simulates a "typing" state indicator in the target Discord channel.
- It calculates a dynamic delay based on the character length of the command, mimicking human typing speed.
- It then dispatches the raw JSON payload securely to the Discord API, executing the command instantaneously in the background.

---

## Libraries & Technology Stack
This executable was built using several powerful open-source libraries:
- **`discord.py-self`**: The core engine. It manages the Discord API websocket connections, allows the application to log in using a User Token, reads incoming OwO bot messages, and dispatches your commands.
- **`pywebview`**: The GUI framework. It renders the beautiful, modern HTML/CSS interface directly into a native Windows desktop window without requiring a traditional browser.
- **`aiohttp`**: The local web server. It bridges the gap between the frontend UI and the backend Python engine, allowing your toggle switches and inputs to instantly communicate with the bot in real-time.
- **`colorama`**: The console styling engine. It formats and color-codes the internal terminal logs, making it easy to track loot drops, errors, and cycle delays at a glance.

---

## Disclaimer
> **Warning:** Self-botting is strictly against Discord's Terms of Service. Use this application at your own risk. The developers are not responsible for any account bans or data loss.

---
<div align="center">
  <a href="https://buymeacoffee.com/amshivang">
    <img src="https://raw.githubusercontent.com/amshivang/amshivang/main/qr-code.png" alt="Buy Me A Coffee" width="200">
  </a>
  <br>
  <strong><a href="https://buymeacoffee.com/amshivang">Support my work on Buy Me A Coffee! ☕</a></strong>
</div>

