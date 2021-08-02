class Bet(object):
    def __init__(
        self,
        event_id: str,
        sport: str,
        bet_id: int,
        brokerage_id: int,
        user_id: int,
        amount: float,
        order_type: str,
        on_team_abbrev: str,
    ):
        self.event_id = event_id
        self.sport = sport
        self.bet_id = bet_id
        self.brokerage_id = brokerage_id
        self.user_id = user_id
        self.amount = amount
        self.order_type = order_type
        self.on_team_abbrev = on_team_abbrev


class LimitBetOrder(Bet):
    def __init__(
        self,
        event_id: str,
        sport: str,
        bet_id: int,
        brokerage_id: int,
        user_id: int,
        amount: float,
        odds: int,
        order_type: str,
        on_team_abbrev: str
    ):
        super().__init__(
            event_id=event_id,
            sport=sport,
            bet_id=bet_id,
            brokerage_id=brokerage_id,
            user_id=user_id,
            amount=amount,
            order_type=order_type,
            on_team_abbrev=on_team_abbrev,
        )
        self.odds = odds


class MarketBetOrder(Bet):
    def __init__(
        self,
        event_id: str,
        sport: str,
        bet_id: int,
        brokerage_id: int,
        user_id: int,
        amount: float,
        order_type: str,
        on_team_abbrev: str
    ):
        super().__init__(
            event_id=event_id,
            sport=sport,
            bet_id=bet_id,
            brokerage_id=brokerage_id,
            user_id=user_id,
            amount=amount,
            order_type=order_type,
            on_team_abbrev=on_team_abbrev,
        )
