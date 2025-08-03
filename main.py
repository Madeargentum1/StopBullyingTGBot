import asyncio
import tg_bot


# Main
async def main():
    await tg_bot.dp.start_polling(tg_bot.bot)


if __name__ == "__main__":
    asyncio.run(main())
