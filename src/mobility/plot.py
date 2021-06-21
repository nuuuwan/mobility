"""Implements plot."""
import os
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

from utils.cache import cache

from geo import geodata
from mobility import lk_data
from mobility._utils import log
from mobility._constants import CACHE_NAME, CACHE_TIMEOUT


def plot():
    """Plot mobility data."""
    dsd_to_data = lk_data.get_data()
    ds_list = lk_data.get_ds_list()
    ds = '2020-03-28'
    data = dsd_to_data[ds]
    log.info('Got mobility data')

    def _map_id_to_data(dsd_id):
        if dsd_id not in data:
            return -1
        return data.get(dsd_id, -1)

    map_ent_id = 'LK-1'
    df = geodata.get_region_geodata(map_ent_id, 'dsd')
    log.info('Got geo data')

    df['p_no_mobility'] = df['id'].apply(_map_id_to_data)
    log.info('Expanded geo data')

    colors = [
        (0.5, 0.5, 0.5),
        (0, 0.5, 0),
        (0, 1, 0),
        (1, 0.5, 0),
        (1, 0, 0),
        (0.8, 0, 0),
        (0.6, 0, 0),
        (0.4, 0, 0),
        (0.2, 0, 0),
        (0, 0, 0),
    ]
    df.plot(
        column='p_no_mobility',
        scheme='UserDefined',
        classification_kwds={
            'bins': [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1],
        },
        legend=True,
        legend_kwds={
            'labels': [
                'No Data',
                '< 10%',
                '10% - 20%',
                '20% - 30%',
                '30% - 40%',
                '40% - 50%',
                '50% < ',
            ],
        },
        figsize=(8, 9),
        cmap=ListedColormap(colors),
    )

    # name = 'The Colombo District'
    name = 'Sri Lanka'
    plt.title(
        'Mobility in %s by Divisional Secretariat (%s)' % (name, ds),
    )
    plt.suptitle(
        'Data: https://data.humdata.org/dataset/movement-range-maps',
        fontsize=8,
    )
    plt.axis('off')
    img_file = '/tmp/mobility.%s.png' % map_ent_id
    plt.savefig(img_file)
    log.info('Saved plot to %s', img_file)
    os.system('open %s' % img_file)



if __name__ == '__main__':
    plot()
