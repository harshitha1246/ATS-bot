import asyncio

from app.telegram_bot import build_application


if __name__ == "__main__":
    asyncio.set_event_loop(asyncio.new_event_loop())
    build_application().run_polling()