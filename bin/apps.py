from datetime import datetime
import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from configparser import ConfigParser
from pathlib import Path
import dirobot
import time


scheduler = BackgroundScheduler(daemon=True)
dir_path = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(Path(dir_path).parent, "config")
config_file_path = os.path.join(config_path, "config.properties")

# reading config.properities and store it on the config_dict variable as dictionary object
try:
    config_dic = ConfigParser()
    config_dic.read(config_file_path)
    if len(config_dic.sections()) == 0:
        raise Exception("File Not found or File is empty")
except Exception as msg:
    # print(msg)
    raise Exception("Unable to read the config.properties file")


def job1():
    dirobot.main(config_dic=config_dic)
    print('monitor function started at time is: %s' % datetime.now())
    # monitor_func(config_dic=config_dic)


if __name__ == '__main__':

    # cron_job1 = '*/1 * * * *'
    # scheduler.add_job(job1, CronTrigger.from_crontab(expr=cron_job1,timezone='UTC'),id='1')
    # scheduler.start()
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        # while True:
        #     time.sleep(2)
        while True:
            print('*'*100)
            print('Getting mail from outlook')
            print('*'*100)
            job1()
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        #scheduler.shutdown()
        print('completed')
