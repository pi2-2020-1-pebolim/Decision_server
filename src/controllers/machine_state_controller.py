class MachineStateController:
    def __init__(self):
        self.handlers = {}
        self.start_state = None
        self.end_states = []

    def add_state(self, name, handler, end_state=0):
        name = name.upper()
        self.handlers[name] = handler
        if end_state:
            self.end_states.append(name)

    def set_start(self, name):
        self.start_state = name.upper()

    def run(self, direction):
        try:
            handler = self.handlers[self.start_state]
        except:
            raise InterruptedError("must call .set_start() before .run()")
        if not self.end_states:
            raise InterruptedError("at least one state must be an end_state")

        while True:
            (decision, new_state) = handler(direction)
            
            if new_state.upper() in self.end_states:
                return decision
            else:
                handler = self.handlers[new_state.upper()]