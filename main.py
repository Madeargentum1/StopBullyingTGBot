import asyncio
import threading

import server
import tg_bot


# Main
async def main():
    await tg_bot.dp.start_polling(tg_bot.bot)


if __name__ == "__main__":
    threading.Thread(target=server.run_web_server, daemon=True).start()
    asyncio.run(main())
