"""Implements plot."""
import os

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.colors import Normalize

# from utils.cache import cache

from geo import geodata
from mobility import lk_data
from mobility._utils import log


def plot():
    """Plot mobility data."""
    map_ent_id = 'LK-1'
    _df = geodata.get_region_geodata(map_ent_id, 'dsd')
    log.info('Got geo data')

    dsd_to_data = lk_data.get_data()
    log.info('Got mobility data')

    for _ds in [
        '2020-03-20',
        '2020-03-30',
        '2020-04-10',
        '2020-04-20',
        '2021-06-14',
    ]:

        data = dsd_to_data[_ds]

        def _map_id_to_data(dsd_id):
            return data.get(dsd_id, -1)

        _df['p_no_mobility'] = _df['id'].apply(_map_id_to_data)
        log.info('Expanded geo data')

        colors = [
            (0.5, 0.5, 0.5),
            (0, 0.4, 0),
            (0, 0.6, 0),
            (0, 0.8, 0),
            (0, 1, 0),

            (1, 0.8, 0),

            (1, 0.4, 0),
            (1, 0, 0),
            (0.8, 0, 0),
            (0.6, 0, 0),
            (0.4, 0, 0),
        ]
        bins = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
        labels = []
        for bin in bins:
            if bin == 0:
                labels.append('No Data')
            elif bin == 0.1:
                labels.append('< 10%')
            elif bin == 1:
                labels.append('> 90%')
            else:
                labels.append('%d%% - %d%%' % ((bin -  1) * 100, bin * 100))

        _df.plot(
            column='p_no_mobility',
            scheme='UserDefined',
            classification_kwds={
                'bins': bins,
            },
            legend=True,
            legend_kwds={
                'labels': labels,
            },
            figsize=(8, 9),
            cmap=ListedColormap(colors),
            norm=Normalize(0, len(colors)),
        )

        # name = 'The Colombo District'
        name = 'Sri Lanka'
        plt.title(
            'Mobility in %s by Divisional Secretariat (%s)' % (name, _ds),
        )
        plt.suptitle(
            'Data: https://data.humdata.org/dataset/movement-range-maps',
            fontsize=8,
        )
        plt.axis('off')
        img_file = '/tmp/mobility.%s.%s.png' % (map_ent_id, _ds)
        plt.savefig(img_file)
        log.info('Saved plot to %s', img_file)
        os.system('open %s' % img_file)
        plt.close()


if __name__ == '__main__':
    plot()
