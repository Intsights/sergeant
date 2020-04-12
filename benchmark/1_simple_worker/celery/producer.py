from . import consumer


consumer.simple.apply_async(
    kwargs={
        'phase': 'start',
    },
)

for i in range(100000):
    consumer.simple.apply_async(
        kwargs={
            'phase': '',
        },
    )

consumer.simple.apply_async(
    kwargs={
        'phase': 'end',
    },
)
