from main.src.flask_lite import FlaskLite
from main.src.utils import Response, Request, dec_to_float, first, iso_format, transform_event_dtm_to_date, encrypt, generate_token, datetime_to_display_format
from main.src.db import login_required, MySql, DynamoDb
from main.src.logger import LoggerFactory

from pymysql import OperationalError
from validate_email import validate_email
import boto3
import os
from json import dumps


flask = FlaskLite()
app = flask.app


@app.route("/portfolio/overview", methods=["GET"])
@login_required
def portfolio_overview(request: Request):
    # logger = LoggerFactory().get_logger(__name__)
    uid = request.body['uid']
    db = MySql()
    active_statuses = ", ".join(["'pending'", "'submitted'", "'partially executed'", "'executed'", "'active'"])
    in_play_to_win = db.fetch("""
        SELECT SUM(AMOUNT) AS inPlay, SUM(EST_PROFIT) AS toWin FROM BETS
        WHERE USER_ID = %s
        AND STATUS IN (%s);
    """ % uid, active_statuses)

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
@login_required
def portfolio_bets(request: Request):
    uid = request.body['uid']
    status = request.body['status']
    market = request.body['market']
    page = request.body['page']
    page_size = request.body.get('pageSize', 10)
    offset = page_size * (page - 1)
    db = MySql()

    pending_statuses = ", ".join(["'pending cancel'", "'pending friend'", "'pending user'"])
    active_statuses = ", ".join(["'pending'", "'submitted'", "'partially executed'", "'executed'", "'active'"])
    completed_statuses = ", ".join(["'completed'"])
    status_lookup = {
        "pending": pending_statuses,
        "active": active_statuses,
        "completed": completed_statuses
    }
    status = status_lookup[status]

    bets = db.fetch("""
        SELECT e.EVENT_ID AS eventId, e.DTM AS dtm, e.HOME AS homeTeam,
        e.AWAY AS awayTeam, b.ON_TEAM AS 'on', b.STATUS AS status,
        b.AMOUNT as amount, u.FIRST_NAME as friendFirstName, u.LAST_NAME as friendLastName FROM EVENT e
        RIGHT JOIN
        (SELECT * FROM BETS
        WHERE USER_ID = %s
        AND STATUS IN (%s)
        AND MARKET = '%s'
        ) AS b
        ON b.EVENT_ID = e.EVENT_ID
        LEFT JOIN USERS u
        ON b.FRIEND = u.USER_ID
        ORDER BY DTM DESC
        LIMIT %s
        OFFSET %s;
    """ % (uid, status, market, page_size, offset))

    def transform_bets(bet):
        date = iso_format(bet['dtm'])

        friend = f"{bet['friendFirstName']} {bet['friendLastName']}"
        del bet['friendFirstName']
        del bet['friendLastName']

        bet['date'] = date
        del bet['dtm']

        bet['friend'] = friend
        bet['amount'] = dec_to_float(bet['amount'])

        return bet

    body = list(map(transform_bets, bets))
    return Response(body=body, status_code=200)


@app.route("/portfolio/recommended", methods=["GET"])
@login_required
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
@login_required
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
@login_required
def event_make_bet_market(request: Request):
    """
    1. update/check user balance
    2. submit bet and get bet id
    3. submit bet to kinesis
    """
    event_id = request.body['eventId']
    uid = request.body['uid']
    on = request.body['on']
    amount = request.body['amount']
    market = "exchange"
    bet_type = "market"
    status = "pending"

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

    bet_id = db.multi_execute("""
        INSERT INTO BETS(USER_ID, EVENT_ID, MARKET, ODDS, AMOUNT, EST_PROFIT, ON_TEAM, TYPE, STATUS, FRIEND, DTM, WON)
        VALUES
            (%s, %s, '%s', %s, %s, %s, '%s', '%s', '%s', NULL, now(), NULL);
        SELECT last_insert_id();
    """ % (uid, event_id, market, odds, amount, 0, on, bet_type, status))[1][0]["last_insert_id()"]

    payload = {**request.body, "bet_id": bet_id, "type": bet_type}
    stream_name = os.environ.get('EXCHANGE_BET_KINESIS_STREAM')

    try:
        client = boto3.client('kinesis', endpoint_url=os.environ.get("ENDPOINT_URL", None))
        client.put_record(
            StreamName=stream_name,
            Data=dumps(payload),
            PartitionKey=str(uid)
        )
        return Response(status_code=204)
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


@app.route("/event/makeBet/limit", methods=["POST"])
@login_required
def event_make_bet_limit(request: Request):
    """
    1. update/check user balance
    2. submit bet and get bet id
    3. submit bet to kinesis
    """
    event_id = request.body['eventId']
    uid = request.body['uid']
    on = request.body['on']
    amount = request.body['amount']
    odds = request.body['odds']
    market = "exchange"
    bet_type = "limit"
    status = "pending"

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

    bet_id = db.multi_execute("""
        INSERT INTO BETS(USER_ID, EVENT_ID, MARKET, ODDS, AMOUNT, EST_PROFIT, ON_TEAM, TYPE, STATUS, FRIEND, DTM, WON)
        VALUES
            (%s, %s, '%s', %s, %s, %s, '%s', '%s', '%s', NULL, now(), NULL);
        SELECT last_insert_id();
    """ % (uid, event_id, market, odds, amount, 0, on, bet_type, status))[1][0]["last_insert_id()"]

    payload = {**request.body, "bet_id": bet_id, "type": bet_type}
    stream_name = os.environ.get('EXCHANGE_BET_KINESIS_STREAM')

    try:
        client = boto3.client('kinesis', endpoint_url=os.environ.get("ENDPOINT_URL", None))
        client.put_record(
            StreamName=stream_name,
            Data=dumps(payload),
            PartitionKey=str(uid)
        )
        return Response(status_code=204)
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


@app.route("/event/makeBet/friend", methods=["POST"])
# @login_required
def event_make_bet_friend(request: Request):
    """
    1. subtract/check user balance
    2. submit bet and get bet id
    3. send to sns for email notification
    """
    event_id = request.body['eventId']
    uid = request.body['uid']
    on = request.body['on']
    amount = request.body['amount']
    odds = request.body['odds']
    friend_id = request.body['friendId']
    market = "social"
    status = "pending friend"

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

    try:
        bet_id = db.multi_execute("""
            INSERT INTO BETS(USER_ID, EVENT_ID, MARKET, ODDS, AMOUNT, EST_PROFIT, ON_TEAM, TYPE, STATUS, FRIEND, DTM, WON)
            VALUES
                (%s, %s, '%s', %s, %s, %s, '%s', NULL, '%s', '%s', now(), NULL);
            SELECT last_insert_id();
        """ % (uid, event_id, market, odds, amount, 0, on, status, friend_id))[1][0]["last_insert_id()"]
    except OperationalError as e:
        error_code, error_message = e.args
        # rollback
        db.execute("""
            UPDATE USERS
            SET BALANCE = BALANCE + %s
            WHERE USER_ID = %s;
        """ % (amount, uid))
        if error_code == 1452:
            return Response(body={"error": "friend does not exist"}, status_code=500)
        else:
            raise e
    try:
        friend_odds = odds * -1
        friend_amount = (amount/100/friend_odds) if friend_odds > 0 else (amount/100*abs(friend_odds))
        event_details = first(db.fetch("""
            SELECT HOME AS homeTeam, AWAY AS awayTeam FROM EVENT
            WHERE EVENT_ID = '%s'
        """ % event_id))
        home_team, away_team = event_details['homeTeam'], event_details['awayTeam']
        friend_on = home_team if on == away_team else away_team
        friend_status = "pending user"

        friend_bet_id = db.multi_execute("""
            INSERT INTO BETS(USER_ID, EVENT_ID, MARKET, ODDS, AMOUNT, EST_PROFIT, ON_TEAM, TYPE, STATUS, FRIEND, DTM, WON, PAIRED_BET_ID)
            VALUES
                (%s, %s, '%s', %s, %s, %s, '%s', NULL, '%s', '%s', now(), NULL, %s);
            SELECT last_insert_id();
        """ % (friend_id, event_id, market, friend_odds, friend_amount, 0, friend_on, friend_status, uid, bet_id))[1][0]["last_insert_id()"]

        db.execute("""
            UPDATE BETS
            SET PAIRED_BET_ID = %s
            WHERE BET_ID = %s
        """ % (friend_bet_id, bet_id))
    except Exception as e:
        # rollback
        db.multi_execute("""
            UPDATE USERS
            SET BALANCE = BALANCE + %s
            WHERE USER_ID = %s;
            DELETE FROM BETS
            WHERE BET_ID = %s
            OR BET_ID = %s;
        """ % (amount, uid, bet_id, friend_bet_id))
        raise e

    payload = first(db.fetch("""
        SELECT u.EMAIL AS email, u.FIRST_NAME AS first_name, b.ON_TEAM AS 'on', e.HOME AS home,
        e.AWAY AS away, e.DTM AS dtm, b.AMOUNT AS amount, f.FIRST_NAME AS friendFirstName, f.LAST_NAME AS friendLastName,
        b.ODDS AS odds
        FROM USERS u
        LEFT JOIN BETS b
        ON u.USER_ID = b.USER_ID
        LEFT JOIN EVENT e
        ON b.EVENT_ID = e.EVENT_ID
        LEFT JOIN USERS f
        ON f.USER_ID = b.FRIEND
        WHERE u.USER_ID = %s
        AND f.USER_ID = %s
        AND b.BET_ID = %s
        AND b.EVENT_ID = %s
        AND e.EVENT_ID = %s;
    """ % (uid, friend_id, bet_id, event_id, event_id)))
    
    if payload:
        payload['date'] = datetime_to_display_format(payload['dtm'])
        del payload['dtm']
        
        payload['with'] = f"{payload['friendFirstName']} {payload['friendLastName']}"
        del payload['friendFirstName']
        del payload['friendLastName']

        topic_arn = os.environ.get('BET_STATUS_CHANGE_EMAIL_SNS_TOPIC_ARN')
        client = boto3.client('sns', endpoint_url=os.environ.get("ENDPOINT_URL", None))
        client.publish(
            TargetArn=topic_arn,
            Message=dumps(payload),
            Subject="BET_SUBMITTED"
        )
    
    return Response(status_code=204)


@app.route("/signup", methods=["POST"])
def signup(request: Request):
    email = request.body['email']
    password = request.body['password']
    first_name = request.body['firstName']
    last_name = request.body['lastName']
    db = MySql()

    hashed_password = encrypt(password=password, email=email)

    is_valid = validate_email(email)
    if not is_valid:
        return Response(body={"error": "invalid email format"}, status_code=403)
    results = db.fetch("""
        SELECT * FROM USERS
        WHERE EMAIL = '%s'
    """ % email)
    results = first(results)
    if results:
        return Response(body={"error": "user already exists"}, status_code=409)

    db.execute("""
        INSERT INTO USERS(EMAIL, FIRST_NAME, LAST_NAME, PWD)
        VALUES
        ('%s', '%s', '%s', '%s');
    """ % (email, first_name, last_name, hashed_password))

    return Response(status_code=200)


@app.route("/login", methods=["GET"])
def login(request: Request):
    email = request.body['email']
    password = request.body['password']

    hashed_password = encrypt(email=email, password=password)

    db = MySql()
    dynamo = DynamoDb()

    result = first(db.fetch("""
        SELECT USER_ID AS uid FROM USERS
        WHERE EMAIL = '%s'
        AND PWD = '%s'
    """ % (email, hashed_password)))

    if not result:
        return Response(body={"error": "incorrect email or password"}, status_code=401)

    uid = result['uid']
    # token = generate_token()
    # TODO: remove this and replace with above token
    token = "foo"

    dynamo.insert_token(uid=uid, token=token)

    body = {'uid': uid, 'token': token}
    return Response(body=body, status_code=200)


@app.route("/bet/social/accept", methods=["PUT"])
@login_required
def bet_social_accept(request: Request):
    uid = request.body['uid']
    bet_id = request.body['betId']

    db = MySql()

    # TODO: come back to this as may have to rethink how friend bets are added to bets


@app.route("/bet/social/cancel", methods=["PUT"])
# @login_required
def bet_social_cancel(request: Request):
    uid = request.body['uid']
    bet_id = request.body['betId']

    db = MySql()

    # TODO: come back after figuring out social bets


@app.route("/bet/social/decline", methods=["PUT"])
@login_required
def bet_social_decline(request: Request):
    uid = request.body['uid']
    bet_id = request.body['betId']

    db = MySql()

    # TODO: come back after figuring out social bets


@app.route("/bet/exchange/cancel", methods=["PUT"])
# @login_required
def bet_exchange_cancel(request: Request):
    uid = request.body['uid']
    bet_id = request.body['betId']

    db = MySql()

    db.execute("""
        UPDATE BETS
        SET STATUS = '%s'
        WHERE BET_ID = %s;
    """ % ('pending cancel', bet_id))

    payload = {
        "action": "cancel",
        "bet_id": bet_id
    }

    stream_name = os.environ.get('MAKE_EXCHANGE_BET_KINESIS_STREAM_NAME')

    client = boto3.client('kinesis', endpoint_url=os.environ.get("ENDPOINT_URL", None))
    client.put_record(
        StreamName=stream_name,
        Data=dumps(payload),
        PartitionKey=str(uid)
    )


