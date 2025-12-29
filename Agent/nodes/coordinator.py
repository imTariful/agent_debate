class RoundCoordinator:
    def __init__(self, total_rounds=8, logger=None):
        self.total = total_rounds
        self._round = 1
        self.logger = logger

    def round_number(self):
        return self._round

    def finished(self):
        return self._round > self.total

    def advance_round(self):
        if not self.finished():
            self._round += 1
            if self.logger:
                self.logger.log_event({"event":"advance_round","round":self._round})

    def require_turn(self, agent_name, expected_agent):
        # expected_agent is name of agent expected at this turn
        if agent_name != expected_agent:
            raise Exception(f"Out of order turn: expected {expected_agent}, got {agent_name}")
