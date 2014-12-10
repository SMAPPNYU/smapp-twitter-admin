import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns

import StringIO
import numpy as np
from datetime import datetime, timedelta
from dateutil import parser
ONE_MINUTE = timedelta(minutes=1)

def tpm_plot(collection, start_datetime, end_datetime):
    start = parser.parse(start_datetime)
    end = parser.parse(end_datetime)
    num_steps = int((end-start).total_seconds()/60)

    fig = plt.figure()
    collection.using_latest_collection_only().histogram_figure(
        start,
        step_size=timedelta(minutes=1),
        num_steps=num_steps,
        show=False)
    plt.title('Tweets per minute')
    plt.xlabel('Time (UTC)')
    plt.ylabel('tweet volume')

    imgdata = StringIO.StringIO()
    fig.savefig(imgdata, format='svg')
    imgdata.seek(0)
    plt.close()

    return imgdata

def limits_plot(limit_messages):
    x, y = zip( *[(lm['timestamp'], lm['number_missed']) for lm in limit_messages] )

    fig = plt.figure()
    ax = fig.add_subplot(111)

    x = matplotlib.dates.date2num(x)
    ax.plot_date(x,y, 'ro', alpha=0.8, xdate=True)

    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    plt.xticks(rotation=90)
    plt.tight_layout()

    imgdata = StringIO.StringIO()
    fig.savefig(imgdata, format='svg')
    imgdata.seek(0)
    plt.close()

    return imgdata

def throwaway_plot(throwaway_messages):
    x,y = zip(*[(m['timestamp'], m['count']) for m in reversed(throwaway_messages)])

    fig = plt.figure()
    ax = fig.add_subplot(111)

    ax.bar(x,y, width=0.005)
    plt.title('tweets per hour')

    imgdata = StringIO.StringIO()
    fig.savefig(imgdata, format='svg')
    imgdata.seek(0)
    plt.close()

    return imgdata