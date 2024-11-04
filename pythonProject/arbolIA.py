class BTNode:
    def __init__(self):
        self.status = "ready"  # ready, running, success, failure

    def run(self):
        if self.status != "running":
            self.reset()
        return self.process()

    def reset(self):
        self.status = "ready"

    def process(self):
        return "success"


class Sequence(BTNode):
    def __init__(self, children=None):
        super().__init__()
        self.children = children or []

    def process(self):
        if not self.children:
            return "success"

        for child in self.children:
            status = child.run()

            if status == "running":
                self.status = "running"
                return "running"
            elif status == "failure":
                self.status = "failure"
                return "failure"

        self.status = "success"
        return "success"


class Selector(BTNode):
    def __init__(self, children=None):
        super().__init__()
        self.children = children or []

    def process(self):
        if not self.children:
            return "failure"

        for child in self.children:
            status = child.run()

            if status == "running":
                self.status = "running"
                return "running"
            elif status == "success":
                self.status = "success"
                return "success"

        self.status = "failure"
        return "failure"


class Action(BTNode):
    def __init__(self, action_func):
        super().__init__()
        self.action_func = action_func

    def process(self):
        status = self.action_func()
        self.status = status
        return status


class Condition(BTNode):
    def __init__(self, condition_func):
        super().__init__()
        self.condition_func = condition_func

    def process(self):
        if self.condition_func():
            self.status = "success"
            return "success"
        self.status = "failure"
        return "failure"