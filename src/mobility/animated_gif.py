"""Animated GIF."""
import os
import datetime

import matplotlib.pyplot as plt
import matplotlib.ticker as tkr
import numpy as np

import imageio

from utils import timex
from covid19 import lk_data as covid_lk_data
from covid19.covid_data import JHU_URL

from mobility import lk_data
from mobility._utils import log

from mobility._constants import URL_HDX_MOBILITY, LK_COVID_EVENTS

WINDOW_DAYS = 7


def _build_frame(data_all, max_ds):
    data_all_filtered = list(filter(
        lambda item: item['ds'] <= max_ds,
        data_all,
    ))

    _x = list(map(
        lambda item: datetime.datetime.fromtimestamp(
            timex.parse_time(item['ds'], '%Y-%m-%d'),
        ),
        data_all_filtered,
    ))
    _x = _x[:-(WINDOW_DAYS - 1)]
    _y1 = list(map(
        lambda item: item['new_deaths'],
        data_all_filtered,
    ))
    _y1_window = np.convolve(
        _y1, np.ones(WINDOW_DAYS) / WINDOW_DAYS,
        'valid',
    )
    _y1 = _y1[:-(WINDOW_DAYS - 1)]

    _y2 = list(map(
        lambda item: item['p_non_mobile_lk'],
        data_all_filtered,
    ))
    _y2_window = np.convolve(
        _y2, np.ones(WINDOW_DAYS) / WINDOW_DAYS,
        'valid',
    )
    _y2 = _y2[:-(WINDOW_DAYS - 1)]

    fig, axs = plt.subplots(2)
    width = 12
    height = 9 * width / 16
    fig.set_size_inches(width, height)
    axs[0].bar(_x, _y1, color='pink')
    axs[0].plot(_x, _y1_window, color='red')
    axs[1].plot(_x, _y2_window, color='blue')
    axs[1].plot(_x, _y2, color='lightblue')

    axs[0].set_title('Daily COVID19 Deaths in Sri Lanka')
    axs[0].legend([
        '%d-day Moving Avg.' % WINDOW_DAYS,
        'Point Value',
    ])
    axs[0].get_yaxis().set_major_formatter(
        tkr.FuncFormatter(lambda x, p: format(int(x), ','))
    )

    axs[1].set_title('% of the Sri Lankan population "staying put"')
    axs[1].legend([
        '%d-day Moving Avg.' % WINDOW_DAYS,
        'Point Value',
    ])
    axs[1].get_yaxis().set_major_formatter(
        tkr.FuncFormatter(lambda x, p: format(float(x), '.1%'))
    )

    for i, item in enumerate(data_all_filtered):
        if 'event' in item:
            event_x = _x[i - WINDOW_DAYS + 1]
            event_y = _y1[i - WINDOW_DAYS + 1]
            axs[0].annotate(
                item['event'],
                xy=(event_x, event_y),
                xytext=(event_x, event_y),
                fontsize=8,
                rotation=45,
            )
            event_y = _y2[i - WINDOW_DAYS + 1]
            axs[1].annotate(
                item['event'],
                xy=(event_x, event_y),
                xytext=(event_x, event_y),
                fontsize=8,
                rotation=45,
            )

    fig.suptitle(max_ds)
    fig.text(
        0.5, 0.05,
        'Data Sources: %s & %s' % (
            URL_HDX_MOBILITY,
            JHU_URL,
        ),
        horizontalalignment='center',
    )

    fig.autofmt_xdate()

    img_file = '/tmp/mobility.%s.png' % (
        max_ds,
    )
    fig.savefig(img_file, dpi=120)
    log.info('Saved plot to %s', img_file)
    return img_file


def _build_animated_gif():
    data_mobility_lk = lk_data.get_data_by_region()['LK']
    data_mobility_lk11 = lk_data.get_data_by_region()['LK-11']
    data_covid19 = covid_lk_data.get_timeseries()

    data_all = []
    for item_covid19 in data_covid19:
        _ds = item_covid19['date'][:10]
        _dict = {
            'ds': _ds,
            'p_non_mobile_lk': data_mobility_lk.get(_ds, 0),
            'p_non_mobile_lk11': data_mobility_lk11.get(_ds, 0),
        }
        if _ds in LK_COVID_EVENTS:
            _dict['event'] = LK_COVID_EVENTS[_ds]
        data_all.append({
            **_dict,
            **item_covid19,
        })

    img_files = []
    n_items = len(data_all[WINDOW_DAYS:])
    for i, item in enumerate(data_all[WINDOW_DAYS:]):
        if (i % 7 != 0) and (i != n_items - 1):
            continue
        _ds = item['ds']
        img_file = '/tmp/tmp.mobility.%s.png' % (_ds)
        if not os.path.exists(img_file):
            img_file = _build_frame(data_all, _ds)
        img_files.append(img_file)

    images = []
    for img_file in img_files:
        images.append(imageio.imread(img_file))

    for i in range(0, 10):
        images.append(images[-1])

    animated_gif_file = '/tmp/mobility.gif'
    imageio.mimsave(animated_gif_file, images, duration=60/len(images))
    log.info('Saved animated gif to %s', animated_gif_file)
    os.system('open -a firefox %s' % animated_gif_file)


if __name__ == '__main__':
    _build_animated_gif()
