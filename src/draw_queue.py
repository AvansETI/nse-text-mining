class Stage:
    def __init__(self, name, draw_func, should_draw=False) -> None:
        self.name = name
        self.draw_func = draw_func
        self.should_draw = should_draw

    def set_should_draw(self, state):
        self.should_draw = state


class Follower:
    def __init__(self) -> None:
        self._handlers = {}

    def add_handler(self, event, func):
        self._handlers[event] = func

    def notify(self, event, value):
        self._handlers[event](event_value=value)


class DrawQueue:
    def __init__(self) -> None:
        self._queue = {}
        self._followers = []

    def get_stages(self):
        return self._queue.keys()

    def add_draw_stage(self, stage_name, stage):
        self._queue[stage_name] = Stage(stage_name, stage)

        self.notify_followers('stage_added', stage_name)

    def get_draw_stage(self, stage_name) -> Stage:
        return self._queue[stage_name]

    def set_stage_should_draw_state(self, stage_name, state):
        stage = self.get_draw_stage(stage_name)
        stage.set_should_draw(state)

        self.notify_followers('stage_should_draw_changed', stage_name)

    # --- observable ---
    # add a follower for the observable
    def listen(self, follower: Follower):
        self._followers.append(follower)

    def notify_followers(self, event, value):
        for follower in self._followers:
            follower.notify(event, value)
    # --- observable ---
