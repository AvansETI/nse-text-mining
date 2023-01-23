import logging


class DrawStage:
    def __init__(self, name, draw_func) -> None:
        self._name = name
        self.draw_func = draw_func
        self._should_draw = False

    def set_should_draw(self, state):
        self._should_draw = state


class Page:
    def __init__(self, name) -> None:
        self._handlers = {}
        self._name = name

    def add_handler(self, event, func):
        self._handlers[event] = func

    def notify(self, event, value):
        logging.debug(f'Received notify of \"{event}\" for follower \"{self._name}\" with event_value: {value}')
        if event in self._handlers:
            self._handlers[event](event_value=value)


class PageDrawStack:
    def __init__(self) -> None:
        self._queue = {}
        self._followers = []
        self._events_before_start = []
        self._queue_started = False

    def get_stages(self):
        return self._queue.keys()

    def add_draw_stage(self, stage_name, stage, should_draw=False):
        self._queue[stage_name] = DrawStage(stage_name, stage)

        self.notify_followers('stage_added', stage_name)

        self.set_stage_should_draw_state(stage_name, should_draw)

    def get_draw_stage(self, stage_name) -> DrawStage:
        return self._queue[stage_name]

    def set_stage_should_draw_state(self, stage_name, state):
        stage = self.get_draw_stage(stage_name)
        stage.set_should_draw(state)

        self.notify_followers('stage_should_draw_changed', {'stage_name': stage_name, 'state': state})

    def start(self):
        self._queue_started = True

        if len(self._events_before_start) > 0:
            logging.info(f'Notifying {len(self._followers)} follower(s) of {len(self._events_before_start)} event(s) in events_before_queue_started')
        for event in self._events_before_start:
            self.notify_followers(event['event'], event['value'])

        self._events_before_start = []

    # --- observable ---
    # add a follower for the observable
    def listen(self, follower: Page):
        logging.info(f'New follower \"{follower._name}\" started listening to draw queue')
        self._followers.append(follower)

    def notify_followers(self, event, value):
        logging.info(f'Notifying followers of event \"{event}\"')
        if (self._queue_started):
            logging.debug(f'Notifying followers of \"{event}\" with event_value: {value}')

            for follower in self._followers:
                follower.notify(event, value)
        else:
            logging.debug(f'Storing \"{event}\" with event_value: {value} in events_before_queue_started')
            self._events_before_start.append({'event': event, 'value': value})
    # --- observable ---
