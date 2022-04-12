import asyncio
import concurrent
import time

from apolloxe import ApolloXeApi
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from apscheduler.events import JobExecutionEvent


class PunchKeeper:
    def __init__(self, loop = None) -> None:
        self.loop = loop if loop else asyncio.get_running_loop()
        self.apollo_api = ApolloXeApi(self.loop)
        self.aio_sch = AsyncIOScheduler(timezone='Asia/Taipei')

    async def check_task(self):
        print('Check task start')
        await self.apollo_api.init_driver()

        await self.apollo_api.get_view('')
        await self.apollo_api.login('', '')
        await self.apollo_api.find_button_2_click('登入')
        await self.apollo_api.find_button_2_click('我要打卡')
        await self.apollo_api.find_button_2_click('上班')
        return await self.apollo_api.wait_check_in_done()

    def job_listener(self, event):
        if isinstance(event, JobExecutionEvent):
            asyncio.run_coroutine_threadsafe(self.apollo_api.destroy_driver(), self.loop)

            print(event.retval)
            print(event.job_id)
            if event.retval:
                print('Success')
            else:
                print('Fails')

    async def run(self):
        print('Prepare scheduler')
        self.aio_sch.add_listener(self.job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

        # aio_sch.add_job(check_task, 'cron', hour=13, minute=49)
        # aio_sch.add_job(check_task, 'interval', seconds=10)
        # aio_sch.add_job(check_task, CronTrigger.from_crontab('30 08 * * 3-5'))
        # self.aio_sch.add_job(self.check_task, 'cron', day_of_week='tue-fri', hour=16, minute=7)
        # aio_sch.add_job(check_task, 'cron', day_of_week='wed-fri', hour=8, minute=33)
        # aio_sch.add_job(check_task, 'cron', day_of_week='thu-fri', hour=8, minute=30)
        self.aio_sch.add_job(self.check_task, 'cron', day_of_week='tue-fri', hour=8, minute=35)
        print(self.aio_sch.state)
        print(self.aio_sch.get_jobs())

        self.aio_sch.start()


def args():
    loop = asyncio.get_event_loop()

    p = PunchKeeper(loop=loop)
    asyncio.ensure_future(p.run())
    loop.run_forever()


if __name__ == '__main__':
    # asyncio.run(main())
    args()
