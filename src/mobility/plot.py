"""Implements plot."""
import os
import datetime

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.colors import Normalize
import matplotlib.ticker as tkr
import numpy as np

import imageio

from utils import timex
from covid19 import lk_data as covid_lk_data

from geo import geodata
from mobility import lk_data
from mobility._utils import log


def _build_animated_gif():
    data_mobility = lk_data.get_data_by_region()['LK']
    data_covid19 = covid_lk_data.get_timeseries()

    ds_to_event = {
        '2020-06-01': 'Navy',
        '2020-07-10': 'Kandakadu',
        '2020-10-12': 'Minuwangoda',
        '2021-04-14': 'New Year',
    }

    data_all = []
    for item_covid19 in data_covid19:
        _ds = item_covid19['date'][:10]
        _dict = {
            'ds': _ds,
            'p_non_mobile': data_mobility.get(_ds, 0),
        }
        if _ds in ds_to_event:
            _dict['event'] = ds_to_event[_ds]
        data_all.append({
            **_dict,
            **item_covid19,
        })

    def _build_frame(max_ds):
        data_all_filtered = list(filter(
            lambda item: item['ds'] <= max_ds,
            data_all,
        ))

        N = 7
        _x = list(map(
            lambda item: datetime.datetime.fromtimestamp(
                timex.parse_time(item['ds'], '%Y-%m-%d'),
            ),
            data_all_filtered,
        ))
        _x = _x[:-(N - 1)]
        _y1 = list(map(
            lambda item: item['new_deaths'],
            data_all_filtered,
        ))
        _y1_N = np.convolve(_y1, np.ones(N) / N, 'valid')
        _y1 = _y1[:-(N - 1)]

        _y2 = list(map(
            lambda item: item['p_non_mobile'],
            data_all_filtered,
        ))
        _y2_N = np.convolve(_y2, np.ones(N) / N, 'valid')
        _y2 = _y2[:-(N - 1)]


        fig, axs = plt.subplots(2)
        width = 12
        height = 9 * width / 16
        fig.set_size_inches(width, height)
        axs[0].bar(_x, _y1, color='pink')
        axs[0].plot(_x, _y1_N, color='red')
        axs[1].plot(_x, _y2, color='lightblue')
        axs[1].plot(_x, _y2_N, color='blue')

        axs[0].set_title('Daily Deaths')
        axs[0].legend(['Point Value', '%d-day Moving Avg.' % N])
        axs[0].get_yaxis().set_major_formatter(
            tkr.FuncFormatter(lambda x, p: format(int(x), ','))
        )

        axs[1].set_title('% of population "staying put"')
        axs[1].legend(['Point Value', '%d-day Moving Avg.' % N])
        axs[1].get_yaxis().set_major_formatter(
            tkr.FuncFormatter(lambda x, p: format(float(x), '.1%'))
        )

        for i, item in enumerate(data_all_filtered):
            if 'event' in item:
                event_x = _x[i - N + 1]
                event_y = _y1[i - N + 1]
                axs[0].annotate(
                    item['event'],
                    xy=(event_x, event_y),
                    xytext=(event_x, event_y + 5),
                    fontsize=8,
                    rotation=45,
                )
                event_y = _y2[i - N + 1]
                axs[1].annotate(
                    item['event'],
                    xy=(event_x, event_y),
                    xytext=(event_x, event_y + 5),
                    fontsize=8,
                    rotation=45,
                )

        fig.suptitle(max_ds)

        fig.autofmt_xdate()

        img_file = '/tmp/mobility.%s.png' % (
            max_ds,
        )
        fig.savefig(img_file)
        log.info('Saved plot to %s', img_file)
        return img_file

    img_files = []
    for item in data_all[7:]:
        _ds = item['ds']
        img_file = _build_frame(_ds)
        img_files.append(img_file)

    images = []
    for img_file in img_files:
        images.append(imageio.imread(img_file))

    animated_gif_file = '/tmp/mobility.gif' % ()
    imageio.mimsave(animated_gif_file, images, duration=60/len(images))
    log.info('Saved animated gif to %s', animated_gif_file)
    os.system('open -a firefox %s' % animated_gif_file)

# def _build_animated_gif_old(
#     ds_start,
#     ds_end,
# ):
#     """Plot mobility data."""
#     data_by_region = lk_data.get_data_by_region()
#     map_region_id = 'LK'
#     child_region_type = 'district'
#     _df = geodata.get_region_geodata(map_region_id, child_region_type)
#     log.info('Got geo data')
#
#     ds_to_active_cases = {}
#     timeseries = covid_lk_data.get_timeseries()
#     for item in timeseries:
#         _ds = item['date'][:10]
#         ds_to_active_cases[_ds] = item['active']
#
#     region_to_data = lk_data.get_data()
#     log.info('Got mobility data')
#
#     ds_list = lk_data.get_ds_list()
#     _y1 = []
#     _y2 = []
#     _y3 = []
#     _y4 = []
#     _x = []
#
#     img_files = []
#     for _ds in ds_list:
#         if _ds > ds_end or _ds < ds_start:
#             continue
#         data = region_to_data[_ds]
#         date = datetime.datetime.fromtimestamp(
#             timex.parse_time(_ds, '%Y-%m-%d'),
#         )
#         _x.append(date)
#         _y1.append(data.get('LK', 0))
#         _y2.append(data.get('LK-1', 0))
#         _y3.append(data.get('LK-11', 0))
#         _y4.append(ds_to_active_cases.get(_ds, 0))
#
#         fig, axs = plt.subplots(2)
#         axs[0].plot(_x, _y1, color='maroon')
#         axs[0].plot(_x, _y2, color='orange')
#         axs[0].plot(_x, _y3, color='green')
#         axs[1].plot(_x, _y4, color='red')
#
#         axs[0].get_yaxis().set_major_formatter(
#             tkr.FuncFormatter(lambda x, p: format(float(x), '.1%'))
#         )
#         axs[1].get_yaxis().set_major_formatter(
#             tkr.FuncFormatter(lambda x, p: format(int(x), ','))
#         )
#         fig.autofmt_xdate()
#
#         # def _map_id_to_data(region_id):
#         #     return data.get(region_id, -1)
#         #
#         # _df['p_no_mobility'] = _df['id'].apply(_map_id_to_data)
#         # log.info('Expanded geo data')
#         #
#         # colors = [
#         #     (0.8, 0.8, 0.8),
#         #     (0, 0.4, 0),
#         #     (0, 0.6, 0),
#         #     (0, 0.8, 0),
#         #     (0, 1, 0),
#         #
#         #     (1, 0.8, 0),
#         #
#         #     (1, 0.4, 0),
#         #     (1, 0, 0),
#         #     (0.8, 0, 0),
#         #     (0.6, 0, 0),
#         #     (0.4, 0, 0),
#         # ]
#         # bins = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
#         # labels = []
#         # for bin in bins:
#         #     if bin == 0:
#         #         labels.append('No Data')
#         #     elif bin == 0.1:
#         #         labels.append('< 10%')
#         #     elif bin == 1:
#         #         labels.append('> 90%')
#         #     else:
#         #         labels.append('%d%% - %d%%' % ((bin -  0.1) * 100, bin * 100))
#         #
#         # _df.plot(
#         #     ax=axs[1],
#         #     column='p_no_mobility',
#         #     scheme='UserDefined',
#         #     classification_kwds={
#         #         'bins': bins,
#         #     },
#         #     legend=True,
#         #     legend_kwds={
#         #         'labels': labels,
#         #     },
#         #     figsize=(8, 9),
#         #     cmap=ListedColormap(colors),
#         #     norm=Normalize(0, len(colors)),
#         # )
#
#         # name = 'The Colombo District'
#         # name = 'Sri Lanka'
#         # fig.title(
#         #     'Mobility in %s by Divisional Secretariat (%s)' % (name, _ds),
#         # )
#         # fig.suptitle(
#         #     'Data: https://data.humdata.org/dataset/movement-range-maps',
#         #     fontsize=8,
#         # )
#         # fig.suptitle(
#         #     'Data: https://data.humdata.org/dataset/movement-range-maps',
#         #     fontsize=8,
#         # )
#
#         img_file = '/tmp/mobility.%s.%s.%s.png' % (
#             map_region_id,
#             child_region_type,
#             _ds,
#         )
#         fig.savefig(img_file)
#         log.info('Saved plot to %s', img_file)
#         # fig.close()
#
#         img_files.append(img_file)
#
#     images = []
#     for img_file in img_files:
#         images.append(imageio.imread(img_file))
#
#     animated_gif_file = '/tmp/mobility.%s.%s.%sto%s.gif' % (
#         map_region_id,
#         child_region_type,
#         ds_start,
#         ds_end,
#     )
#     imageio.mimsave(animated_gif_file, images, duration=10 / len(images))
#     log.info('Saved animated gif to %s', animated_gif_file)
#     os.system('open -a firefox %s' % animated_gif_file)


if __name__ == '__main__':
    _build_animated_gif()
