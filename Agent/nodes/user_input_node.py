import re


class UserInputNode:
    def __init__(self, logger=None):
        self.logger = logger

    def prompt_topic(self):
        try:
            topic = input("Enter topic for debate: ")
        except EOFError:
            topic = ""
        if self.logger:
            self.logger.log_event({"event":"user_input_received","topic":topic})
        return topic

    def validate_and_sanitize(self, topic: str):
        if not topic or not isinstance(topic, str):
            return None
        t = topic.strip()
        # length checks
        if len(t) < 5 or len(t) > 200:
            return None
        # remove suspicious control characters
        t = re.sub(r"[\x00-\x1f]","",t)
        # basic sanitize: remove angle brackets
        t = t.replace("<","&lt;").replace(">","&gt;")
        if self.logger:
            self.logger.log_event({"event":"topic_validated","topic":t})
        return t
