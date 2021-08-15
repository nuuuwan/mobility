
import datetime

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as tkr
from infographics import Figure, Infographic

from utils import timex

from mobility import lk_data

POPULATION = 21_800_000
PADDING = 0.12
DS_FORMAT = '%Y-%m-%d'
DAYS_MOVING_WINDOW = 7

REGION_IDS = ['LK', 'LK-1', 'LK-11', 'LK-1103']

class PlotByRegion(Figure.Figure):
    def __init__(
        self,
        left_bottom=(PADDING, PADDING),
        width_height=(1 - PADDING * 2, 1 - PADDING * 2),
        figure_text='',
    ):
        super().__init__(
            left_bottom=left_bottom,
            width_height=width_height,
            figure_text=figure_text,
        )
        self.__data__ = PlotByRegion.__prep_data__(self)

    def __prep_data__(self):
        data_by_region = lk_data.get_data_by_region()

        dss = list(data_by_region[REGION_IDS[0]].keys())
        x = list(map(
            lambda ds: datetime.datetime.fromtimestamp(timex.parse_time(ds, DS_FORMAT)),
            dss[:-DAYS_MOVING_WINDOW + 1],
        ))


        ys = list(map(
            lambda region_id: np.convolve(
                list(data_by_region[region_id].values()),
                np.ones(DAYS_MOVING_WINDOW) / DAYS_MOVING_WINDOW,
                'valid',
            ),
            REGION_IDS,
        ))

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
            ['Sri Lanka', 'Western Province', 'Colombo District', 'Colombo DSD'],
            loc='upper left',
        )
        plt.ylabel('Proportion of Population "Staying Put"')
        ax.grid()
        ax.get_yaxis().set_major_formatter(
            tkr.FuncFormatter(lambda x, p: format(float(x), '.1%'))
        )
        fig = plt.gcf()
        fig.autofmt_xdate()

    def get_data(self):
        return self.__data__


def _plot():
    plot = PlotByRegion()
    (x, ys, date, date_id) = plot.get_data()

    image_file = '/tmp/mobility.plot_by_region.%s.png' % (date_id)
    Infographic.Infographic(
        title='Proportion of Population "Staying Put"',
        subtitle='(as of %s)' % date,
        footer_text='\n'.join(
            ['Data from https://data.humdata.org/dataset/movement-range-maps', 'Visualization by @nuuuwan']
        ),
        children=[plot],
    ).save(image_file)
    return image_file


if __name__ == '__main__':
    _plot()
