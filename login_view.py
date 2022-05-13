import asyncio
import concurrent
from datetime import datetime
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
        self.dump_check_out_time_job = None
        self.check_out_job = None

    async def check_task(self):
        print('Check task start')
        await self.apollo_api.init_driver()

        await self.apollo_api.get_view('')
        await self.apollo_api.login('', '')
        await self.apollo_api.find_button_2_click('登入')
        await self.apollo_api.find_button_2_click('我要打卡')

        # await self.apollo_api.find_button_2_click('上班')
        await self.apollo_api.check_out_click()
        return await self.apollo_api.wait_check_out_done()

    async def dump_check_out_time_task(self):
        print('Check task start')
        await self.apollo_api.init_driver()

        await self.apollo_api.get_view('')
        await self.apollo_api.login('', '')
        await self.apollo_api.find_button_2_click('登入')
        await self.apollo_api.find_button_2_click('我要打卡')
        return await self.apollo_api.get_check_out_time()

    def job_listener(self, event):
        if isinstance(event, JobExecutionEvent):
            asyncio.run_coroutine_threadsafe(self.apollo_api.destroy_driver(), self.loop)

            print(event.job_id)
            if event.job_id == self.dump_check_out_time_job.id:
                print(f'The check in time is {event.retval}')
                check_out_time: datetime = event.retval

                hour, minute = check_out_time.hour + 9, check_out_time.minute
                print(f'so the punch out time is {hour} : {minute}')

                self.check_out_job.reschedule('cron', day_of_week='mon-fri', hour=hour, minute=minute)
                self.check_out_job.resume()

            if event.job_id == self.check_out_job.id:
                self.check_out_job.pause()
                punch_out_resutl: bool = event.retval

                if punch_out_resutl:
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
        # self.aio_sch.add_job(self.check_task, 'cron', day_of_week='tue-fri', hour=8, minute=30)

        self.dump_check_out_time_job = self.aio_sch.add_job(self.dump_check_out_time_task, 'cron', day_of_week='mon-fri', hour=17, minute=27)
        print(self.aio_sch.state)

        # self.check_out_job = self.aio_sch.add_job(self.check_task, 'cron', day_of_week='mon-fri', hour=16, minute=45)
        self.check_out_job = self.aio_sch.add_job(self.check_task)
        self.check_out_job.pause()

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
