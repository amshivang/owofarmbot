import json
import time
import random
import asyncio
import re
from colorama import Fore, Style
import discord
from discord.ext import commands
from utils import setup_logger, parse_inventory_to_matrix, send_human_like

logger = setup_logger()

OWO_BOT_ID = 408785106942164992
TARGET_BOT_IDS = [OWO_BOT_ID]

OWO_COMMANDS = [
    "owo inv", "owo cash", "owo hb", "owo profile", "owo zoo", 
    "owo teams 1", "owo teams 2", "!rt", "!rr", "owo my", 
    "owo sc all", "owo buy 1", "owo buy 2", "owo buy 3"
]
GAMBLE_COMMANDS = ["owo cf", "owo cf t", "owo s"]

class OwOFarmBot(commands.Bot):
    def __init__(self, uid=None):
        self.uid = uid
        logger_name = f"OwOFarmBetter.{uid}" if uid else "OwOFarmBetter"
        self.logger = setup_logger(logger_name)
        
        super().__init__(command_prefix='.', case_insensitive=True, self_bot=True)
        self.remove_command("help")
        
        self.load_settings()
        
        # State tracking
        self.is_farming = False
        self.farm_task = None
        self.target_channels = []
        self.current_channel_index = 0
        
        # Timers
        self.start_time = 0
        self.session_end_time = 0
        self.on_break = False
        self.break_end_time = 0
        self.on_rest = False
        self.rest_end_time = 0
        self.last_rest_time = 0
        self.rest_interval = 0
        self.last_switch_time = 0
        self.switch_interval = 0
        self.next_owo_time = 0
        self.next_pray_curse_time = 0
        self.pray_count_left = self.bot_config.get("PRAY_CURSE", {}).get("COUNT", 0)
        
        # Inventory tracking
        self.gem_matrix = [[0 for _ in range(7)] for _ in range(3)]
        self.inventory_received = asyncio.Event()
        self.pending_equip_cmd = None

    def load_settings(self):
        default_settings = {
            "TOKEN": "YOUR_TOKEN_HERE",
            "BASE_DELAY": 15,
            "FARM_TEXTS": ["owo h", "owo b"],
            "GAMBLE": {"ENABLED": False, "AMOUNT": 1000},
            "PRAY_CURSE": {"ENABLED": False, "COMMAND": "owo pray", "COUNT": 5}
        }
        # In-memory settings only. If bot_config is not set, initialize it.
        if not hasattr(self, 'bot_config') or not self.bot_config:
            self.bot_config = default_settings
            self.logger.info("Initialized default settings in-memory")
        
        # Sync dynamic variables
        self.pray_count_left = self.bot_config.get("PRAY_CURSE", {}).get("COUNT", 0)

    async def setup_hook(self):
        from cogs.farm_commands import FarmCommands
        await self.add_cog(FarmCommands(self))

    async def on_ready(self):
        self.logger.info(f"OwO Farm Connected To: {self.user}")
        self.logger.info("Ready to farm! Type .start or .owo <channel_id> in Discord to begin.")

    def start_session(self):
        self.start_time = time.time()
        farm_duration = random.randint(6600, 8400) # 1h50m to 2h20m
        self.session_end_time = self.start_time + farm_duration
        self.last_rest_time = time.time()
        self.rest_interval = random.randint(1500, 1800)
        self.last_switch_time = time.time()
        self.switch_interval = random.randint(1500, 1800)
        self.next_owo_time = time.time() + random.randint(10, 60)
        self.next_pray_curse_time = time.time() + random.randint(10, 60)

    async def _farm_runner(self):
        try:
            if self.is_farming and self.target_channels:
                channel = self.target_channels[self.current_channel_index]
                self.inventory_received.clear()
                await send_human_like(channel, "owo inv", self.logger)
                try:
                    await asyncio.wait_for(self.inventory_received.wait(), timeout=10.0)
                except asyncio.TimeoutError:
                    self.logger.warning("Timed out waiting for inventory. Proceeding anyway.")
                await asyncio.sleep(random.uniform(1.5, 3.0))

            while self.is_farming:
                channel = self.target_channels[self.current_channel_index]
                
                if time.time() >= self.session_end_time:
                    self.on_break = True
                    break_duration = random.randint(900, 1200)
                    self.break_end_time = time.time() + break_duration
                    msg = f"Taking a long break for {break_duration // 60} minutes..."
                    print(Fore.YELLOW + msg + Style.RESET_ALL)
                    self.logger.info(msg)
                    await channel.send(msg)
                    await asyncio.sleep(break_duration)
                    self.on_break = False
                    self.start_session()
                    continue
                
                if time.time() - self.last_rest_time >= self.rest_interval:
                    self.on_rest = True
                    rest_duration = random.randint(120, 180)
                    self.rest_end_time = time.time() + rest_duration
                    msg = f"Taking a short rest for {rest_duration // 60} minutes {rest_duration % 60} seconds..."
                    print(Fore.YELLOW + msg + Style.RESET_ALL)
                    self.logger.info(msg)
                    await channel.send(msg)
                    await asyncio.sleep(rest_duration)
                    self.on_rest = False
                    self.last_rest_time = time.time()
                    self.rest_interval = random.randint(1500, 1800)
                    continue
                
                if len(self.target_channels) > 1 and time.time() - self.last_switch_time >= self.switch_interval:
                    self.current_channel_index = (self.current_channel_index + 1) % len(self.target_channels)
                    channel = self.target_channels[self.current_channel_index]
                    msg = f"Switching to channel: {channel.name}"
                    print(Fore.CYAN + msg + Style.RESET_ALL)
                    self.logger.info(msg)
                    await channel.send(msg)
                    self.last_switch_time = time.time()
                    self.switch_interval = random.randint(1500, 1800)
                
                if self.pending_equip_cmd:
                    await send_human_like(channel, self.pending_equip_cmd, self.logger)
                    self.pending_equip_cmd = None
                    await asyncio.sleep(random.uniform(1.5, 3.0))

                texts = list(self.bot_config["FARM_TEXTS"])
                random.shuffle(texts)
                for text in texts:
                    if not self.is_farming: return
                    if random.random() < 0.1:
                        await asyncio.sleep(random.uniform(2, 3))
                    await send_human_like(channel, text, self.logger)
                    await asyncio.sleep(random.uniform(1.5, 3.0))
                
                if self.bot_config["PRAY_CURSE"]["ENABLED"] and self.pray_count_left > 0 and time.time() >= self.next_pray_curse_time:
                    if not self.is_farming: return
                    await send_human_like(channel, self.bot_config["PRAY_CURSE"]["COMMAND"], self.logger)
                    self.pray_count_left -= 1
                    self.next_pray_curse_time = time.time() + random.randint(300, 400)
                    await asyncio.sleep(random.uniform(1.5, 3.0))

                if time.time() >= self.next_owo_time:
                    if not self.is_farming: return
                    await send_human_like(channel, random.choice(OWO_COMMANDS), self.logger)
                    self.next_owo_time = time.time() + random.randint(100, 200)
                    await asyncio.sleep(random.uniform(1.5, 3.0))

                # ── Last command: randomly pick s / cf / cf t ─────────────────
                gamble_cfg = self.bot_config.get("GAMBLE", {})
                if gamble_cfg.get("ENABLED", False):
                    if not self.is_farming: return
                    base   = gamble_cfg.get("AMOUNT", 1000)
                    amount = max(1, int(base * random.uniform(0.8, 1.2)))
                    choice = random.choice([
                        f"owo s {amount}",
                        f"owo cf {amount}",
                        f"owo cf t {amount}",
                    ])
                    await send_human_like(channel, choice, self.logger)
                    await asyncio.sleep(random.uniform(1.5, 3.0))

                delay = self.bot_config["BASE_DELAY"] + random.uniform(-3, 3)
                self.logger.info(f"Cycle complete. Waiting {delay:.2f}s")
                await asyncio.sleep(delay)
                
        except asyncio.CancelledError:
            self.logger.info("Farming task cancelled.")
        except Exception as e:
            self.logger.error(f"Error in farm loop: {e}", exc_info=True)
            self.is_farming = False

    async def check_cash(self):
        self.cash_event = asyncio.Event()
        self.cash_amount = "Unknown"
        channel = self.target_channels[self.current_channel_index] if self.target_channels else None
        if not channel:
            raise Exception("No active channel")
        await send_human_like(channel, "owo cash", self.logger)
        try:
            await asyncio.wait_for(self.cash_event.wait(), timeout=10.0)
        except asyncio.TimeoutError:
            raise Exception("Timed out waiting for cash response from OwO bot")
        return self.cash_amount

    async def on_message(self, message):
        await self.process_commands(message)

        if message.author.id == self.user.id or not self.is_farming:
            return

        if message.author.id not in TARGET_BOT_IDS:
            return

        if message.channel not in self.target_channels:
            return

        content = message.content.lower()
        for embed in message.embeds:
            if embed.author and embed.author.name: content += "\n" + embed.author.name.lower()
            if embed.title: content += "\n" + embed.title.lower()
            if embed.description: content += "\n" + embed.description.lower()
            for field in embed.fields:
                content += "\n" + str(field.name).lower() + "\n" + str(field.value).lower()

        channel = message.channel

        # ── CAPTCHA / WARNING check ────────────────────────
        CAPTCHA_TRIGGERS = [
            "are you a real human",
            "please complete your captcha",
            "verify that you are human",
            "please complete this within 10 minutes",
            "captcha",
        ]
        
        # Check if the message contains any trigger AND mentions the user's ID
        if any(trigger in content for trigger in CAPTCHA_TRIGGERS) and str(self.user.id) in message.content:
            self.logger.warning("\n" + "="*60)
            self.logger.warning("CAPTCHA DETECTED — STOPPING BOT IMMEDIATELY")
            self.logger.warning("="*60)
            self.is_farming = False
            if self.farm_task:
                self.farm_task.cancel()
            
            if hasattr(self, 'uid') and self.uid:
                self.logger.info("Bot is_farming set to False in memory after captcha detection.")
            
            try:
                await channel.send("🚨 CAPTCHA detected! Stopped. Solve it then type .resume")
            except:
                pass
            return

        user_name = self.user.name.lower() if self.user else ""
        display_name = self.user.display_name.lower() if self.user else ""

        if hasattr(self, 'cash_event') and not self.cash_event.is_set():
            if (user_name in content or display_name in content) and "cowoncy" in content:
                match = re.search(r'currently has \*\*<:cowoncy:\d+>\s*([\d,]+)\*\*', message.content)
                if match:
                    self.cash_amount = match.group(1)
                    self.cash_event.set()

        if f"{user_name}'s inventory" in content or f"{display_name}'s inventory" in content:
            self.gem_matrix = parse_inventory_to_matrix(content)
            self.logger.info("Updated Gem Matrix:")
            tiers = ["Gem 1", "Gem 3", "Gem 4"]
            rarities = ["Common", "Uncommon", "Rare", "Epic", "Mythic", "Legendary", "Fabled"]
            header = f"{'Tier':>7} | " + " | ".join(f"{r:>9}" for r in rarities)
            self.logger.info(header)
            self.logger.info("-" * len(header))
            for row_idx, row in enumerate(self.gem_matrix):
                row_str = f"{tiers[row_idx]:>7} | " + " | ".join(f"{val:>9}" for val in row)
                self.logger.info(row_str)
            self.inventory_received.set()

        if (user_name in content or display_name in content) and "you found:" in content:
            active_gems_with_uses = re.findall(r'<a?:(c|u|r|e|m|l|f)gem(1|3|4):\d+>\s*`?\[(\d+)/\d+\]`?', content)
            expected_tiers = {'1', '3', '4'}
            found_tiers = set()
            needs_equip = []

            if active_gems_with_uses:
                gem_info = []
                for rarity, tier, uses_left in active_gems_with_uses:
                    found_tiers.add(tier)
                    gem_info.append(f"{rarity}gem{tier} ({uses_left} left)")
                    if int(uses_left) <= 0:
                        self.logger.warning(f"⚠️ Gem Tier {tier} ({rarity}gem{tier}) has reached 0 uses!")
                        needs_equip.append(tier)
                self.logger.info(f"💎 Active hunt gems: {', '.join(gem_info)}")
            else:
                active_gems = re.findall(r'<a?:(c|u|r|e|m|l|f)gem(1|3|4):\d+>', content)
                if active_gems:
                    for rarity, tier in active_gems:
                        found_tiers.add(tier)
                    self.logger.info(f"💎 Active hunt gems: {', '.join([f'{r}gem{t}' for r, t in active_gems])}")
                else:
                    self.logger.info("💎 No active hunt gems found.")

            missing_tiers = expected_tiers - found_tiers
            for missing in missing_tiers:
                self.logger.warning(f"⚠️ MISSING GEMS IN HUNT: Tier {missing} is completely missing!")
                needs_equip.append(missing)

            needs_equip = list(set(needs_equip))

            if needs_equip:
                equip_ids = []
                tier_to_idx = {'1': 0, '3': 1, '4': 2}
                base_ids = [51, 65, 72]
                for t in sorted(needs_equip):
                    t_idx = tier_to_idx[t]
                    found_id = None
                    for r in range(6, -1, -1):
                        if self.gem_matrix[t_idx][r] > 0:
                            self.gem_matrix[t_idx][r] -= 1
                            found_id = base_ids[t_idx] + r
                            break
                    if found_id:
                        equip_ids.append(str(found_id))
                    else:
                        self.logger.warning(f"❌ Cannot equip Tier {t} gem: None left in inventory matrix!")

                if equip_ids:
                    use_cmd = f"owo use {' '.join(equip_ids)}"
                    self.logger.info(f"🔄 Queuing auto-equip for next cycle: {use_cmd}")
                    self.pending_equip_cmd = use_cmd
