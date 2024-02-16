import asyncio
from functions import main
import schedule
import time


def my_func():
    asyncio.run(main())


# Запуск функции каждую минуту
schedule.every(1).minutes.do(my_func)


while True:
    schedule.run_pending()
    time.sleep(1)
