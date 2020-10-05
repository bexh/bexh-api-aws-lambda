from main.src.flask_lite import FlaskLite
from main.src.utils import Response, Request, dec_to_float, first, iso_format, transform_event_dtm_to_date
from main.src.db import login_required, MySql
from main.src.logger import LoggerFactory

from pymysql import OperationalError
import boto3
import os
from json import dumps


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
        AND STATUS = '%s'
        AND MARKET = '%s'
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

    body = list(map(transform_event_dtm_to_date, events))

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
        AND SPORT = '%s'
        LIMIT %s
        OFFSET %s;
    """ % (sport, page_size, offset))

    body = list(map(transform_event_dtm_to_date, events))

    return Response(body=body, status_code=200)


@app.route("/event/overview", methods=["GET"])
def event_overview(request: Request):
    event_id = request.body['eventId']
    db = MySql()
    events = db.fetch("""
        SELECT HOME AS homeTeam, AWAY AS awayTeam, CURRENT_ODDS AS currentOdds, DTM AS dtm
        FROM EVENT
        WHERE EVENT_ID = %s;
    """ % event_id)

    body = transform_event_dtm_to_date(first(events))

    return Response(body=body, status_code=200)


@app.route("/event/odds", methods=["GET"])
def event_odds(request: Request):
    event_id = request.body['eventId']
    db = MySql()
    odds = db.fetch("""
        SELECT ODDS AS odds, DTM AS dtm
        FROM ODDS
        WHERE EVENT_ID = %s;
    """ % event_id)

    body = list(map(transform_event_dtm_to_date, odds))

    return Response(body=body, status_code=200)


@app.route("/event/bets", methods=["GET"])
def event_bets(request: Request):
    event_id = request.body['eventId']
    uid = request.body['uid']
    status = request.body['status']
    market = request.body['market']
    page = request.body['page']
    page_size = request.body.get('pageSize', 10)
    offset = page_size * (page - 1)
    db = MySql()

    bets = db.fetch("""
        SELECT b.EVENT_ID AS eventId, b.ON_TEAM AS 'on', STATUS AS status, b.AMOUNT AS amount,
        u.FIRST_NAME AS friendFirst, u.LAST_NAME AS friendLast, e.HOME AS homeTeam, e.AWAY AS awayTeam, e.DTM AS dtm
        FROM (
            SELECT *
            FROM BETS
            WHERE EVENT_ID = %s
            AND USER_ID = %s
            AND STATUS = '%s'
            AND MARKET = '%s'
            LIMIT %s
            OFFSET %s
        ) b
        LEFT JOIN USERS u
        ON b.FRIEND = u.USER_ID
        LEFT JOIN EVENT e
        ON b.EVENT_ID = e.EVENT_ID;
    """ % (event_id, uid, status, market, page_size, offset))

    def transform_bets(bet):
        if market == 'social':
            bet['friend'] = f"{bet['friendFirst']} {bet['friendLast']}"
        else:
            bet['friend'] = None
        del bet['friendFirst']
        del bet['friendLast']
        bet['date'] = iso_format(bet['dtm'])
        del bet['dtm']
        bet['amount'] = dec_to_float(bet['amount'])
        return bet

    body = list(map(transform_bets, bets))

    return Response(body=body, status_code=200)


@app.route("/event/makeBet/market", methods=["POST"])
def event_make_bet_market(request: Request):
    event_id = request.body['eventId']
    uid = request.body['uid']
    on = request.body['on']
    amount = request.body['amount']
    db = MySql()

    try:
        db.execute("""
            UPDATE USERS
            SET BALANCE = BALANCE - %s
            WHERE USER_ID = %s;
        """ % (amount, uid))
    except OperationalError as e:
        error_code, error_message = e.args
        if error_code == 3819:
            return Response(body={"error": "insufficient funds"}, status_code=502)
        else:
            raise e

    odds = first(db.fetch("""
        SELECT CURRENT_ODDS AS odds FROM EVENT
        WHERE EVENT_ID = '%s';
    """ % event_id))['odds']

    est_profit = round((amount*odds/100), 2) if odds > 0 else round((amount/odds/100), 2)

    bet_id = db.multi_execute("""
        INSERT INTO BETS(USER_ID, EVENT_ID, MARKET, ODDS, AMOUNT, EST_PROFIT, ON_TEAM, TYPE, STATUS, FRIEND, DTM, WON)
        VALUES
            (%s, %s, '%s', %s, %s, %s, '%s', '%s', '%s', NULL, now(), NULL);
        SELECT last_insert_id();
    """ % (uid, event_id, "exchange", odds, amount, est_profit, on, 'market', 'pending'))[1][0]["last_insert_id()"]

    payload = {**request.body, "bet_id": bet_id}
    stream_name = os.environ.get('MAKE_BET_KINESIS_STREAM_NAME')

    try:
        client = boto3.client('kinesis', endpoint_url=os.environ.get("ENDPOINT_URL", None))
        client.put_record(
            StreamName=stream_name,
            Data=dumps(payload),
            PartitionKey=str(uid)
        )
    except Exception as e:
        # rollback
        db.execute("""
            UPDATE USERS
            SET BALANCE = BALANCE + %s
            WHERE USER_ID = %s;
        """ % amount)
        db.execute("""
            DELETE FROM BETS
            WHERE BET_ID = %s
        """ % bet_id)
        return Response(body={"error": f"could not write to kinesis {e}"}, status_code=500)
