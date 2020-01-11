
import config
from analytics import Client

segment_client = Client(config.SEGMENT_API_KEY, sync_mode=True)


def _annotation_event(user, action, collection, document, label_type_id, *args, **kwargs):
    properties = {
        'collection': collection,
        'document': document,
        'label_type_id': label_type_id,
    }

    segment_client.track(user_id=user, event=action, properties=properties)


def _login_event(user, *args, **kwargs):
    segment_client.identify(user_id=user)

event_mapper = {'login': _login_event}


class AuditLog:
    def log_event(user, action, *args, **kwargs):
        if action in event_mapper:
            event_mapper[action](user=user, action=action, *args, **kwargs)
        else:
            _annotation_event(user=user, action=action, *args, **kwargs)
