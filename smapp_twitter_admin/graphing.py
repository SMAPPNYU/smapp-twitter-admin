import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

import StringIO
import numpy as np
from datetime import datetime, timedelta
ONE_MINUTE = timedelta(minutes=1)

def tpm_plot(tweets):
    minutes = np.ceil((tweets[0]['timestamp'] - tweets[-1]['timestamp']).total_seconds()/60)
    x = [tweets[-1]['timestamp'] + i * ONE_MINUTE for i in range(int(minutes)-1)]
    y = np.zeros(len(x))
    for tweet in tweets:
        for i,time in enumerate(x):
            if tweet['timestamp'] < time+ONE_MINUTE:
                y[i] += 1
                break
    fig = plt.figure()
    ax = fig.add_subplot(111)

    ax.bar(x,y, width=0.0005)

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