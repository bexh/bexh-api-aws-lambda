from main.src.flask_lite import FlaskLite
from main.src.utils import Response, Request, dec_to_float, first, iso_format
from main.src.db import login_required, MySql
from main.src.logger import LoggerFactory


flask = FlaskLite()
app = flask.app


@app.route("/portfolio/overview", methods=["GET"])
def portfolio_overview(request: Request):
    # logger = LoggerFactory().get_logger(__name__)
    uid = request.body['uid']
    db = MySql()
    in_play_to_win = db.fetch("""
        SELECT SUM(AMOUNT) AS inPlay, SUM(EST_PROFIT) AS toWin FROM BETS
        WHERE USER_ID = %s
        AND (STATUS = 'active' OR STATUS = 'pending');
    """ % uid)

    vig_savings = db.fetch("""
        SELECT SUM(AMOUNT + EST_PROFIT)*0.1 AS vigSavings FROM BETS
        WHERE USER_ID = %s
        AND STATUS = 'completed'
        AND WON = 1;
    """ % uid)

    account_balance = db.fetch("""
        SELECT ACCOUNT_AMOUNT AS accountBalance FROM USERS
        WHERE USER_ID = %s;
    """ % uid)

    body = {
        "inPlay": dec_to_float(first(in_play_to_win).get("inPlay", 0.00)),
        "toWin": dec_to_float(first(in_play_to_win).get("toWin", 0.00)),
        "vigSavings": dec_to_float(first(vig_savings).get("vigSavings", 0.00)),
        "accountBalance": dec_to_float(first(account_balance).get("accountBalance", 0.00)),
    }
    return Response(body=body, status_code=200)


@app.route("/portfolio/bets", methods=["GET"])
def portfolio_bets(request: Request):
    uid = request.body['uid']
    status = request.body['status']
    market = request.body['market']
    page = request.body['page']
    page_size = request.body.get('pageSize', 10)
    offset = page_size * (page - 1)
    db = MySql()

    # TODO: fix query to get friend name not uid
    bets = db.fetch("""
        SELECT e.EVENT_ID AS eventId, e.DTM AS dtm, e.HOME AS homeTeam,
        e.AWAY AS awayTeam, b.ON_TEAM AS 'on', b.STATUS AS status,
        b.AMOUNT as amount, b.FRIEND AS friend FROM EVENT e
        RIGHT JOIN
        (SELECT * FROM BETS
        WHERE USER_ID = %s
        AND STATUS = \"%s\"
        AND MARKET = \"%s\"
        ) AS b
        ON b.EVENT_ID = e.EVENT_ID
        ORDER BY DTM DESC
        LIMIT %s
        OFFSET %s;
    """ % (uid, status, market, page_size, offset))

    def transform_bets(bet):
        date = iso_format(bet['dtm'])
        # TODO: temp hack for friend
        friend = str(bet['friend'])

        bet['date'] = date
        del bet['dtm']

        bet['friend'] = friend
        bet['amount'] = dec_to_float(bet['amount'])

        return bet

    body = list(map(transform_bets, bets))
    return Response(body=body, status_code=200)


@app.route("/portfolio/recommended", methods=["GET"])
def portfolio_recommended(request: Request):
    uid = request.body['uid']
    page = request.body['page']
    page_size = request.body.get('pageSize', 10)
    offset = page_size * (page - 1)
    db = MySql()
    events = db.fetch("""
        SELECT e.HOME AS homeTeam, e.AWAY AS awayTeam, e.dtm AS dtm,
        e.CURRENT_ODDS AS currentOdds, e.EVENT_ID AS eventId, e.SPORT AS sport
        FROM EVENT e
        RIGHT JOIN (
            SELECT COUNT(BET_ID) AS count, EVENT_ID FROM BETS
            GROUP BY EVENT_ID
            ORDER BY count DESC
            LIMIT %s
            OFFSET %s
            ) AS popular
        ON e.EVENT_ID = popular.EVENT_ID;
    """ % (page_size, offset))

    def transform_events(event):
        date = iso_format(event['dtm'])
        event['date'] = date
        del event['dtm']
        return event

    body = list(map(transform_events, events))

    return Response(body=body, status_code=200)


@app.route("/sport", methods=["GET"])
def event_sport(request: Request):
    sport = request.body['sport']
    page = request.body['page']
    page_size = request.body.get('page', 10)
    offset = page_size * (page - 1)
    db = MySql()
    events = db.fetch("""
        SELECT HOME AS homeTeam, AWAY AS awayTeam, DTM AS dtm, CURRENT_ODDS AS currentOdds,
        EVENT_ID AS eventId, SPORT AS sport
        FROM EVENT
        WHERE DTM > now()
        AND SPORT = \"%s\"
        LIMIT %s
        OFFSET %s;
    """ % (sport, page_size, offset))

    def transform_events(event):
        date = iso_format(event['dtm'])
        event['date'] = date
        del event['dtm']
        return event

    body = list(map(transform_events, events))

    return Response(body=body, status_code=200)
