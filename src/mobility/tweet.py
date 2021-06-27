
"""Tweet."""

from utils import twitter

from mobility import lk_data
from mobility.plot import _plot_all

from gig import ents


def _tweet():
    latest_ds = lk_data.get_latest_ds()
    all_data = lk_data.get_data()
    latest_data = all_data[latest_ds].items()
    latest_data_dsd = list(filter(
        lambda x: len(x[0]) == 7,
        latest_data,
    ))
    latest_data_dsd = sorted(latest_data_dsd, key=lambda x: x[1])
    dsd_index = ents.get_entity_index('dsd')

    rendered_detail_lines = ['🔴 HIGHEST']
    for i in range(0, 3):
        info = latest_data_dsd[-(i + 1)]
        dsd = dsd_index[info[0]]
        name = dsd['name']
        if len(name) > 10:
            name = name.split(' ')[:10]
        name = '#' + name
        rendered_detail_lines.append(
            '{dsd_id} {p_non_mobile:.1%}'.format(
                dsd_id=name,
                p_non_mobile=info[1],
            )
        )
    rendered_detail_lines += ['', '🟢 LOWEST']
    for i in range(0, 3):
        info = latest_data_dsd[i]
        dsd = dsd_index[info[0]]
        name = dsd['name']
        if len(name) > 10:
            name = name.split(' ')[:10]
        name = '#' + name
        rendered_detail_lines.append(
            '{dsd_id} {p_non_mobile:.1%}'.format(
                dsd_id=name,
                p_non_mobile=info[1],
            )
        )
    rendered_details = '\n'.join(rendered_detail_lines)

    tweet_text = '''#Mobility Report ({_ds})
% of Sri Lankans "Staying Put"

{rendered_details}

Method: @Facebook Mobility
#lka #SriLanka #COVID19SL #LockDown @HumanData
    '''.format(
        _ds=latest_ds,
        rendered_details=rendered_details,
    )

    print(tweet_text)
    print(len(tweet_text))

    plot_info = _plot_all()

    status_image_files = plot_info['image_files']

    twtr = twitter.Twitter.from_args()
    twtr.tweet(
        tweet_text=tweet_text,
        status_image_files=status_image_files,
        update_user_profile=True,
    )


if __name__ == '__main__':
    _tweet()
