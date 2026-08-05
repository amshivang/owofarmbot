import os
import sys
import json
import logging
import asyncio
import time
import socket
import threading
import webview
import aiohttp
from aiohttp import web
import bot_core  # Added so PyInstaller detects the module during build

def get_base_path():
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_base_path()
WEB_DIR = os.path.join(BASE_DIR, 'desktop_web')

def get_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()
    return port

class WebLogHandler(logging.Handler):
    def __init__(self, app):
        super().__init__()
        self.app = app
        
    def emit(self, record):
        try:
            parts = record.name.split('.')
            uid = parts[1] if len(parts) > 1 else None
            if not uid:
                return  
                
            log_msg = self.format(record)
            log_data = {
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(record.created)),
                'level': record.levelname,
                'message': log_msg
            }
            loop = self.app.get('loop')
            if loop and loop.is_running():
                asyncio.run_coroutine_threadsafe(self.broadcast(log_data, uid), loop)
        except Exception:
            self.handleError(record)
            
    async def broadcast(self, log_data, uid):
        user_ws_map = self.app.get('user_websockets', {})
        websockets = user_ws_map.get(uid, set())
        if not websockets:
            return
        payload = json.dumps(log_data)
        disconnected = set()
        for ws in websockets:
            try:
                await ws.send_str(payload)
            except Exception:
                disconnected.add(ws)
        for ws in disconnected:
            websockets.discard(ws)

def setup_web_logger(app):
    logger = logging.getLogger('OwOFarmBetter')
    handler = WebLogHandler(app)
    formatter = logging.Formatter('%(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

@web.middleware
async def cors_middleware(request, handler):
    if request.method == "OPTIONS":
        response = web.Response(status=200)
    else:
        try:
            response = await handler(request)
        except web.HTTPException as ex:
            ex.headers['Access-Control-Allow-Origin'] = '*'
            ex.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PUT, DELETE'
            ex.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            raise ex
        
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PUT, DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

async def handle_index(request):
    return web.FileResponse(os.path.join(WEB_DIR, 'index.html'))

async def handle_dashboard(request):
    return web.FileResponse(os.path.join(WEB_DIR, 'dashboard.html'))

async def handle_css(request):
    return web.FileResponse(os.path.join(WEB_DIR, 'style.css'))

async def handle_js(request):
    return web.FileResponse(os.path.join(WEB_DIR, 'app.js'))

async def handle_logo(request):
    return web.FileResponse(os.path.join(WEB_DIR, 'logo.png'))

async def handle_matrix(request):
    return web.FileResponse(os.path.join(WEB_DIR, 'matrix.js'))

async def handle_validate_token(request):
    try:
        data = await request.json()
        token = data.get('token')
        if not token:
            return web.json_response({'success': False, 'message': 'Token is required.'}, status=400)
        
        headers = {
            'Authorization': token,
            'Content-Type': 'application/json'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get('https://discord.com/api/v9/users/@me', headers=headers) as resp:
                if resp.status == 200:
                    user_data = await resp.json()
                    username = user_data.get('username', 'Unknown User')
                    disc = user_data.get('discriminator', '0000')
                    display_name = f"{username}#{disc}" if disc != "0" else username
                    return web.json_response({'success': True, 'username': display_name})
                else:
                    return web.json_response({'success': False, 'message': f'Discord API rejected token (Status code: {resp.status})'}, status=401)
    except Exception as e:
        return web.json_response({'success': False, 'message': f'Error contacting Discord API: {str(e)}'}, status=500)

def merge_settings_in_memory(bot, data):
    default_settings = {
        "TOKEN": "YOUR_TOKEN_HERE",
        "BASE_DELAY": 15,
        "FARM_TEXTS": ["owo h", "owo b", "owo"],
        "GAMBLE": {"ENABLED": False, "AMOUNT": 1000},
        "PRAY_CURSE": {"ENABLED": False, "COMMAND": "owo pray", "COUNT": 5}
    }
    if hasattr(bot, 'bot_config') and bot.bot_config:
        existing = bot.bot_config
        for k, v in existing.items():
            if isinstance(v, dict) and k in default_settings and isinstance(default_settings[k], dict):
                default_settings[k].update(v)
            else:
                default_settings[k] = v
    for k, v in data.items():
        if isinstance(v, dict) and k in default_settings and isinstance(default_settings[k], dict):
            default_settings[k].update(v)
        else:
            default_settings[k] = v
    bot.bot_config = default_settings
    bot.pray_count_left = default_settings.get("PRAY_CURSE", {}).get("COUNT", 0)

async def handle_start(request):
    try:
        data = await request.json()
        token = data.get('TOKEN')
        uid = data.get('UID')
        
        bots = request.app['bots']
        bot_tasks = request.app['bot_tasks']
        
        bot = bots.get(uid)
        if bot and not bot.is_closed():
            merge_settings_in_memory(bot, data)
            if bot.is_ready():
                bot.logger.info("Farming configurations updated dynamically via dashboard!")
                return web.json_response({'success': True, 'username': str(bot.user)})
        else:
            if BASE_DIR not in sys.path:
                sys.path.insert(0, BASE_DIR)
            from bot_core import OwOFarmBot
            bot = OwOFarmBot(uid=uid)
            bots[uid] = bot
            merge_settings_in_memory(bot, data)
            
        async def bot_starter():
            try:
                await bot.start(token)
            except Exception as e:
                bot.logger.error(f"Failed to connect bot client: {str(e)}")
            finally:
                bot.logger.info("Discord client loop stopped.")
                bot.is_farming = False
                if bot.farm_task:
                    bot.farm_task.cancel()

        old_task = bot_tasks.get(uid)
        if old_task and not old_task.done():
            old_task.cancel()
            
        bot_tasks[uid] = asyncio.create_task(bot_starter())
        
        for _ in range(8):
            await asyncio.sleep(0.5)
            if bot.is_ready():
                return web.json_response({'success': True, 'username': str(bot.user)})
        
        if not bot_tasks[uid].done():
            return web.json_response({'success': True, 'message': 'Connecting to Discord in background...'})
        else:
            return web.json_response({'success': False, 'message': 'Connection failed immediately. Check logs.'}, status=400)
            
    except Exception as e:
        return web.json_response({'success': False, 'message': f'Error starting Discord client: {str(e)}'}, status=500)

async def handle_stop(request):
    try:
        data = await request.json()
        uid = data.get('UID')
    except Exception:
        uid = request.query.get('uid')
        
    bots = request.app['bots']
    bot_tasks = request.app['bot_tasks']
    
    bot = bots.get(uid)
    bot_task = bot_tasks.get(uid)
    if bot:
        bot.is_farming = False
        if bot.farm_task:
            bot.farm_task.cancel()
            bot.logger.info("Stopped farming task.")
            
        if bot.is_ready():
            await bot.close()
            bot.logger.info("Closed Discord bot connection.")
                
        bots.pop(uid, None)
        
    if bot_task and not bot_task.done():
        bot_task.cancel()
        bot_tasks.pop(uid, None)
        
    return web.json_response({'success': True, 'message': 'Bot stopped successfully.'})

async def handle_status(request):
    uid = request.query.get('uid')
    bot = request.app['bots'].get(uid)
    if not bot:
        return web.json_response({
            'connected': False,
            'is_farming': False,
            'username': None
        })
        
    return web.json_response({
        'connected': bot.is_ready(),
        'is_farming': bot.is_farming,
        'username': str(bot.user) if bot.user else None
    })

async def handle_check_cash(request):
    uid = request.query.get('uid')
    bot = request.app['bots'].get(uid)
    if not bot or not bot.is_ready():
        return web.json_response({'success': False, 'message': 'Bot is not running or not connected.'})
    try:
        cash = await bot.check_cash()
        return web.json_response({'success': True, 'cash': cash})
    except Exception as e:
        return web.json_response({'success': False, 'message': str(e)})

async def handle_ws_logs(request):
    uid = request.query.get('uid')
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    if uid not in request.app['user_websockets']:
        request.app['user_websockets'][uid] = set()
        
    request.app['user_websockets'][uid].add(ws)
    
    bot = request.app['bots'].get(uid)
    logger = bot.logger if bot else logging.getLogger(f"OwOFarmBetter.{uid}")
    logger.info("Web dashboard console connected to logs stream.")
    
    try:
        async for msg in ws:
            pass
    finally:
        if uid in request.app['user_websockets']:
            request.app['user_websockets'][uid].discard(ws)
    return ws

def run_server(port):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    app = web.Application(middlewares=[cors_middleware])
    app['bots'] = {}
    app['bot_tasks'] = {}
    app['user_websockets'] = {}
    app['loop'] = loop
    
    app.router.add_get('/', handle_index)
    app.router.add_get('/dashboard', handle_dashboard)
    app.router.add_get('/style.css', handle_css)
    app.router.add_get('/app.js', handle_js)
    app.router.add_get('/matrix.js', handle_matrix)
    app.router.add_get('/logo.png', handle_logo)
    
    app.router.add_post('/api/validate-token', handle_validate_token)
    app.router.add_post('/api/start', handle_start)
    app.router.add_post('/api/stop', handle_stop)
    app.router.add_get('/api/status', handle_status)
    app.router.add_get('/api/ws/logs', handle_ws_logs)
    app.router.add_get('/api/check_cash', handle_check_cash)
    
    setup_web_logger(app)
    
    runner = web.AppRunner(app)
    loop.run_until_complete(runner.setup())
    site = web.TCPSite(runner, '127.0.0.1', port)
    loop.run_until_complete(site.start())
    
    print(f"Backend running on http://127.0.0.1:{port}")
    loop.run_forever()

if __name__ == "__main__":
    port = get_free_port()
    server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
    server_thread.start()
    
    url = f"http://127.0.0.1:{port}/"
    webview.create_window('FarmBot Desktop', url, width=1200, height=800)
    webview.start(private_mode=False)
