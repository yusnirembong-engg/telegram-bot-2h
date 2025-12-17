# Telegram User API (Telethon) - Auto Kirim Pesan Aman (Tanpa Media)
import os
import random
import asyncio
from telethon import TelegramClient, errors
from datetime import datetime

# ====== KONFIGURASI VIA ENV ======
api_id = int(os.environ.get("API_ID"))
api_hash = os.environ.get("API_HASH")
session_name = "session_tele_user"
ADMIN_ID = int(os.environ.get("ADMIN_ID", 0))  # Telegram pribadi untuk notif error

# ====== LIST GRUP ======
GROUP_IDS = [
    -1002658447462, -1002255700000, -1001428379167, -1001706294440,
    -1002072882843, -1001352580530, -1001662248944, -1002038560278,
    -1001662248944, -1001764400714, -1001684579817
]

# ====== ROTASI PESAN ======
MESSAGES = [
    "🔥 GRATISAN LAGI DIBUKA 🔥\nYang nanya free? 👉 Sudah tersedia di BIO\nTanpa deposit\nLangsung klaim\nGas cek bio sekarang 💥",
    "🎁 INFO FREEBET HARI INI 🎁\nGratis tanpa deposit, langsung klaim di BIO!\nKesempatan terbatas ⚡",
    "⚡ PROMO GRATIS ⚡\nSudah ada di BIO, jangan sampai kelewatan\nLangsung klaim sekarang!"
]

# ====== LOG ======
LOG_FILE = "log_telegram.txt"

# ====== DELAY ======
MIN_DELAY = 3
MAX_DELAY = 10

# ====== Gagal Counter ======
failed_counter = {}  # key: group_id, value: jumlah gagal berturut-turut
MAX_FAIL = 5        # skip permanen setelah 5 gagal

async def send_message(client, group_id, message):
    global failed_counter

    if failed_counter.get(group_id, 0) >= MAX_FAIL:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Skip permanen grup {group_id} karena gagal {MAX_FAIL} kali berturut-turut")
        return

    try:
        await client.send_message(group_id, message)
        log_text = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Berhasil kirim ke {group_id}"
        print(log_text)
        with open(LOG_FILE, "a") as f:
            f.write(log_text + "\n")
        failed_counter[group_id] = 0  # reset counter jika sukses
        await asyncio.sleep(random.randint(MIN_DELAY, MAX_DELAY))
    except errors.FloodWaitError as fe:
        log_text = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Skip sementara grup {group_id} karena FloodWait {fe.seconds}s"
        print(log_text)
        with open(LOG_FILE, "a") as f:
            f.write(log_text + "\n")
        if ADMIN_ID != 0:
            try:
                await client.send_message(ADMIN_ID, log_text)
            except:
                pass
        await asyncio.sleep(fe.seconds + 5)
    except Exception as e:
        failed_counter[group_id] = failed_counter.get(group_id, 0) + 1
        log_text = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Gagal kirim ke {group_id}: {e} (Fail {failed_counter[group_id]}/{MAX_FAIL})"
        print(log_text)
        with open(LOG_FILE, "a") as f:
            f.write(log_text + "\n")
        if ADMIN_ID != 0:
            try:
                await client.send_message(ADMIN_ID, log_text)
            except:
                pass
        await asyncio.sleep(random.randint(MIN_DELAY, MAX_DELAY))

async def main():
    async with TelegramClient(session_name, api_id, api_hash) as client:
        for group_id in GROUP_IDS:
            message = random.choice(MESSAGES)
            await send_message(client, group_id, message)

if __name__ == "__main__":
    asyncio.run(main())
