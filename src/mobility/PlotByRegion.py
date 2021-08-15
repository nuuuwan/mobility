import datetime

import matplotlib.pyplot as plt
import matplotlib.ticker as tkr
import numpy as np
from infographics import Figure, Infographic
from utils import timex

from mobility import lk_data

POPULATION = 21_800_000
PADDING = 0.12
DS_FORMAT = '%Y-%m-%d'
DAYS_MOVING_WINDOW = 7
URL_HDX = 'https://data.humdata.org/dataset/movement-range-maps'


class PlotByRegion(Figure.Figure):
    def __init__(
        self,
        region_to_labels,
        left_bottom=(PADDING, PADDING),
        width_height=(1 - PADDING * 2, 1 - PADDING * 2),
        figure_text='',
    ):
        super().__init__(
            left_bottom=left_bottom,
            width_height=width_height,
            figure_text=figure_text,
        )
        self.region_to_labels = region_to_labels
        self.__data__ = PlotByRegion.__prep_data__(self)

    def __prep_data__(self):
        data_by_region = lk_data.get_data_by_region()
        region_ids = list(self.region_to_labels.keys())
        dss = list(data_by_region[region_ids[0]].keys())
        x = list(
            map(
                lambda ds: datetime.datetime.fromtimestamp(
                    timex.parse_time(ds, DS_FORMAT)
                ),
                dss[: -DAYS_MOVING_WINDOW + 1],
            )
        )

        ys = list(
            map(
                lambda region_id: np.convolve(
                    list(
                        map(
                            lambda ds: data_by_region[region_id].get(ds, 0),
                            dss,
                        )
                    ),
                    np.ones(DAYS_MOVING_WINDOW) / DAYS_MOVING_WINDOW,
                    'valid',
                ),
                region_ids,
            )
        )

        date = dss[-1][:10]
        date_id = date.replace('-', '')

        return (x, ys, date, date_id)

    def draw(self):
        super().draw()

        (x, ys, date, date_id) = self.__data__

        ax = plt.axes(self.left_bottom + self.width_height)
        for y in ys:
            plt.plot(x, y)
        plt.legend(
            self.region_to_labels.values(),
            loc='upper left',
        )
        plt.ylabel(
            'Proportion of Population "Staying Put" (%d Day Moving Average)'
            % DAYS_MOVING_WINDOW
        )
        ax.grid()
        ax.get_yaxis().set_major_formatter(
            tkr.FuncFormatter(lambda x, p: format(float(x), '.1%'))
        )
        fig = plt.gcf()
        fig.autofmt_xdate()

    def get_data(self):
        return self.__data__


def _plot(region_to_labels, subtitle, tag):
    plot = PlotByRegion(region_to_labels=region_to_labels)
    (x, ys, date, date_id) = plot.get_data()

    image_file = '/tmp/mobility.plot_by_region.%s.%s.png' % (date_id, tag)
    Infographic.Infographic(
        title='Proportion of Population "Staying Put"',
        subtitle='%s (as of %s)' % (subtitle, date),
        footer_text='\n'.join(
            [
                'Data from %s' % URL_HDX,
                'Visualization by @nuuuwan',
            ]
        ),
        children=[plot],
    ).save(image_file)
    return image_file


if __name__ == '__main__':
    _plot(
        {
            'LK': 'Sri Lanka',
            'LK-1': 'Western Province',
            'LK-2': 'Central Province',
            'LK-3': 'Southern Province',
            'LK-4': 'Northern Province',
            # 'LK-5': 'Eastern Province',
            'LK-6': 'North Western Province',
            'LK-7': 'North Central Province',
            # 'LK-8': 'Uva Province',
            'LK-9': 'Sabaragamuwa Province',
        },
        'By Province - Uva and Eastern Provinces have incomplete data',
        'provinces',
    )

    _plot(
        {
            'LK-1103': 'Colombo',
            'LK-1106': 'Kolonnawa',
            'LK-1109': 'Kaduwela',
            'LK-1112': 'Homagama',
            'LK-1115': 'Seethawaka',
            'LK-1118': 'Padukka',
            'LK-1121': 'Maharagama',
            'LK-1124': 'Sri Jayawardanapura Kotte',
            'LK-1127': 'Thimbirigasyaya',
            'LK-1130': 'Dehiwala-Ratmalana',
            'LK-1133': 'Moratuwa',
            'LK-1136': 'Kesbewa',
        },
        'Colombo District',
        'colombo',
    )
