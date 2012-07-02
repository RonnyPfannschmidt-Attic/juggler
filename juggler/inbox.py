from .feedactor import FeedActor

class InboxActor(FeedActor):
    name = 'inbox'

    listen_for = [
        {'type': 'juggler:order', 'state':'received'},
    ]
