import os
import re
import sys
import random
import asyncio
import logging
from logging.handlers import RotatingFileHandler

def setup_logger(name='OwOFarmBetter'):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    formatter = logging.Formatter('[%(asctime)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    if not logger.handlers:
        logger.addHandler(console_handler)
    
    return logger

def parse_inventory_to_matrix(content):
    """
    Parses the inventory message to create a 3x7 matrix of gem quantities.
    Rows: Gem1, Gem3, Gem4
    Columns: Common, Uncommon, Rare, Epic, Mythic, Legendary, Fabled
    """
    matrix = [[0 for _ in range(7)] for _ in range(3)]
    tier_map = {'1': 0, '3': 1, '4': 2}
    rarity_map = {'c': 0, 'u': 1, 'r': 2, 'e': 3, 'm': 4, 'l': 5, 'f': 6}
    superscript_map = {'⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4', '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9'}
    
    matches = re.findall(r'<a?:(c|u|r|e|m|l|f)gem(1|3|4):\d+>([⁰¹²³⁴⁵⁶⁷⁸⁹]+)', content)
    for rarity, tier, qty_str in matches:
        qty = int(''.join(superscript_map[char] for char in qty_str))
        matrix[tier_map[tier]][rarity_map[rarity]] = qty
        
    return matrix

async def random_typing(text):
    """Simulates human typing with random typos and speed."""
    result = ""
    for char in text:
        if random.random() < 0.02:  # 2% typo chance
            result += random.choice('abcdefghijklmnopqrstuvwxyz')
            await asyncio.sleep(random.uniform(0.1, 0.2))
            result = result[:-1]
        result += char
        await asyncio.sleep(random.uniform(0.05, 0.15))
    return result

async def send_human_like(channel, text, logger):
    """Wraps typing simulator and sends message."""
    typed_text = await random_typing(text)
    await channel.send(typed_text)
    logger.info(f"Sent: '{text}'")
