import asyncio
from functions import main
import schedule
import time


def my_func():
    asyncio.run(main())


# Запуск функции каждые 5 минут
schedule.every(5).minutes.do(my_func)


while True:
    schedule.run_pending()
    time.sleep(1)
