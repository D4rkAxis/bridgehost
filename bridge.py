import asyncio
import logging
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError
from aiohttp import web  # NEW: For dummy health check

# ========================== CONFIG ==========================
API_ID = 28328622
API_HASH = 'b259ae2fcffdb3e11133d94b56915110'
BOT_TOKEN = '8553271238:AAFInIJGF0d8jQv25hYP0dgEeV-wyjtyir0'

SOURCE_BOT_ID = 8553271238
DESTINATION_CHANNEL = -1003889415595

# ========================== LOGGING ==========================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)

# ========================== CLIENTS ==========================
bot_client = TelegramClient('bot_session', API_ID, API_HASH)
user_client = TelegramClient('user_session', API_ID, API_HASH)

bot_client.flood_sleep_threshold = 60 * 60

# NEW: Dummy health check for Back4app
async def health_check(request):
    return web.Response(text="OK")  # Simple response to pass health check

async def start_http_server():
    app = web.Application()
    app.add_routes([web.get('/', health_check)])  # Or /health
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 80)  # Listen on port 80
    await site.start()
    logging.info("✅ Dummy HTTP server started for health check")

# ======================= /START =======================
@bot_client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    await event.reply("🚀 **Bridge Connected!** Signals forwarding instantly.")
    logging.info(f"New user: {event.sender_id}")

# ======================= RELIABLE FORWARD =======================
async def send_with_retry(client, entity, message, max_retries=10):
    for attempt in range(max_retries):
        try:
            await client.send_message(entity, message)
            logging.info("✅ Forwarded successfully")
            return
        except FloodWaitError as e:
            wait = e.seconds + 10
            logging.warning(f"FloodWait {wait}s (attempt {attempt+1})")
            await asyncio.sleep(wait)
        except Exception as e:
            logging.error(f"Error attempt {attempt+1}: {e}")
            await asyncio.sleep(2 ** attempt)
    logging.error("💥 Failed after max retries")

@user_client.on(events.NewMessage(from_users=SOURCE_BOT_ID))
async def bridge_handler(event):
    logging.info("📦 Signal received → forwarding...")
    await send_with_retry(bot_client, DESTINATION_CHANNEL, event.message)

# ========================== MAIN ==========================
async def main():
    await bot_client.start(bot_token=BOT_TOKEN)
    await user_client.start()

    # NEW: Start dummy server in background
    asyncio.create_task(start_http_server())

    print("\n" + "="*60)
    print("🔥 BACK4APP BRIDGE IS LIVE (FREE TIER)")
    print(f"Listening to bot: {SOURCE_BOT_ID}")
    print(f"Forwarding to: {DESTINATION_CHANNEL}")
    print("="*60 + "\n")

    await asyncio.gather(
        bot_client.run_until_disconnected(),
        user_client.run_until_disconnected()
    )

if __name__ == '__main__':
    asyncio.run(main())
