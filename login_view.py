import asyncio

from apolloxe import ApolloXeApi
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger


async def check_task():
    print('Check task start')
    a = ApolloXeApi()
    await a.get_view("")
    await a.login('', '')
    await a.find_button_2_click('登入')
    await a.find_button_2_click('我要打卡')
    await a.find_button_2_click('上班')
    await a.wait_check_in_done()


async def main():
    print('Prepare scheduler')
    aio_sch = AsyncIOScheduler(timezone='Asia/Taipei')

    # aio_sch.add_job(check_task, 'cron', hour=13, minute=49)
    # aio_sch.add_job(check_task, 'interval', seconds=10)
    aio_sch.add_job(check_task, CronTrigger.from_crontab('30 08 * * *'))
    print(aio_sch.state)
    print(aio_sch.get_jobs())

    aio_sch.start()


def args():
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(main())
    loop.run_forever()


if __name__ == '__main__':
    # asyncio.run(main())
    args()
