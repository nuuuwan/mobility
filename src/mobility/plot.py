"""Plot."""

import matplotlib.pyplot as plt
from geo import geodata
from matplotlib.colors import ListedColormap, Normalize

from mobility import lk_data
from mobility._constants import URL_HDX_MOBILITY
from mobility._utils import log


def _plot(region_id, child_region_type, label, _ds):
    _df = geodata.get_region_geodata(region_id, child_region_type)
    log.info('Got geo data')

    data_by_region = lk_data.get_data_by_region()
    log.info('Got mobility data')

    def _get_p_non_mobile(region_id):
        return data_by_region.get(region_id, {}).get(_ds, -1)

    _df['p_non_mobile'] = _df['id'].apply(_get_p_non_mobile)

    _df.plot(
        column='p_non_mobile',
        scheme='UserDefined',
        classification_kwds={
            'bins': [0, 0.2, 0.4, 0.6, 0.8, 1.0],
        },
        legend=True,
        legend_kwds={
            'labels': [
                'No Data',
                '< 20%',
                '20% - 40%',
                '40% - 60%',
                '60% - 80%',
                '%80 <',
            ],
        },
        norm=Normalize(0, 6),
        cmap=ListedColormap(
            [
                'lightgray',
                'green',
                'orange',
                'red',
                'brown',
                'black',
            ]
        ),
        figsize=(8, 9),
    )
    image_file = '/tmp/tmp.mobility.%s.%s.%s.png' % (
        _ds,
        region_id,
        child_region_type,
    )
    plt.axis('off')
    plt.suptitle('Data Source: %s' % URL_HDX_MOBILITY, fontsize=8)
    plt.title('%% of %s "Staying Put" (%s)' % (label, _ds), fontsize=16)
    plt.savefig(image_file)
    plt.close()
    return image_file


def _plot_all():
    ds_list = lk_data.get_ds_list()
    latest_ds = ds_list[-1]
    ds_list[-1 - 7]
    return {
        'ds': latest_ds,
        'image_files': [
            _plot('LK', 'dsd', 'Sri Lanka', latest_ds),
            _plot('LK-1', 'dsd', 'the Western Province', latest_ds),
        ],
    }


if __name__ == '__main__':
    _plot_all()
