"""Tweet."""

from utils import twitter

from mobility.plot import _plot_all


def _tweet():
    plot_info = _plot_all()

    tweet_text = '''
Mobility Report {_ds}

% of Sri Lankans "Staying Put", according to @Facebook's mobility data.

#lka #SriLanka #COVID19SL #LockDown @HumanData
    '''.format(
        _ds=plot_info['ds'],
    )

    status_image_files = plot_info['image_files']

    twtr = twitter.Twitter.from_args()
    twtr.tweet(
        tweet_text=tweet_text,
        status_image_files=status_image_files,
        update_user_profile=True,
    )


if __name__ == '__main__':
    _tweet()
