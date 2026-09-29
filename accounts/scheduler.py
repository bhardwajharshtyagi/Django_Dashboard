from apscheduler.schedulers.background import BackgroundScheduler

from .tasks import check_birthdays


scheduler = BackgroundScheduler()


def start_scheduler():

    if not scheduler.running:

        scheduler.add_job(
            check_birthdays,
            trigger="cron",
            hour=9,
            minute=0,
            id="birthday_email_job",
            replace_existing=True,
        )

        scheduler.start()

        print(
            "Birthday Scheduler Started Successfully"
        )