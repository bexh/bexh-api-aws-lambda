-- CREATE DATABASE BEXH;
USE db;

CREATE TABLE IF NOT EXISTS USERS (
	USER_ID INTEGER NOT NULL,
	FIRST_NAME VARCHAR(100) NOT NULL, 
	LAST_NAME VARCHAR(100) NOT NULL, 
	YEAR_OF_BIRTH INTEGER,
	MONTH_OF_BIRTH INTEGER,
	DAY_OF_BIRTH INTEGER,
	SSN INTEGER,
	EMAIL VARCHAR(100),
	PHONE INTEGER,
	PWD VARCHAR(100),
	ADDRESS VARCHAR(500),
	PRIMARY KEY(USER_ID)
);

CREATE TABLE IF NOT EXISTS FRIENDS (
	USER1_ID INTEGER,
	USER2_ID INTEGER,
	FOREIGN KEY (USER1_ID) REFERENCES USERS(USER_ID) ON DELETE CASCADE,
	FOREIGN KEY (USER2_ID) REFERENCES USERS(USER_ID) ON DELETE CASCADE,
	PRIMARY KEY(USER1_ID, USER2_ID),
	CHECK(USER1_ID!=USER2_ID)
);

-- CREATE TRIGGER FRIENDS_TRIGGER
--    BEFORE INSERT ON FRIENDS
--     FOR EACH ROW
--       DECLARE
--         TEMP INTEGER;
--       BEGIN
--         IF :new.USER1_ID > :new.USER2_ID THEN
--           TEMP := :new.USER1_ID;
--           :new.USER1_ID := :new.USER2_ID;
--           :new.USER2_ID := TEMP;
--         END IF;
--     END;
-- /

CREATE TABLE IF NOT EXISTS BANKING (
	PAYMENT_ID INTEGER NOT NULL,
	USER_ID INTEGER NOT NULL,
	PAYMENT_TYPE VARCHAR(100),
	WALLET_ADDR VARCHAR(200),
	ACCOUNT_NUM VARCHAR(200),
	ROUTING_NUM VARCHAR(200),
	CARD_NUM INTEGER,
	EXP_DATE DATE,
	CVV INTEGER,
	ZIP INTEGER,
	FOREIGN KEY (USER_ID) REFERENCES USERS(USER_ID) ON DELETE CASCADE,
	PRIMARY KEY(PAYMENT_ID)
);

CREATE TABLE IF NOT EXISTS ODDS(
	EVENT_ID VARCHAR(100),
	DTM DATETIME,
	ODDS VARCHAR(100),
	PRIMARY KEY(EVENT_ID, DTM)
);

CREATE TABLE IF NOT EXISTS EVENT (
	EVENT_ID VARCHAR(100) NOT NULL,
	HOME VARCHAR(100),
	AWAY VARCHAR(100),
	SPORT VARCHAR(100),
	DTM DATETIME,
	CURRENT_ODDS INTEGER
);

-- ALTER TABLE ODDS ADD CONSTRAINT FK_ODD FOREIGN KEY (EVENT_ID) REFERENCES EVENT;
-- ALTER TABLE EVENT ADD CONSTRAINT FK_EVNT FOREIGN KEY (EVENT_ID, DTM) REFERENCES ODDS

CREATE TABLE IF NOT EXISTS BETS (
	BET_ID INTEGER NOT NULL,
	TYPE VARCHAR(50) NOT NULL,
	ODD1S INTEGER NOT NULL,
	AMOUNT INTEGER NOT NULL,
	EVENT VARCHAR(200) NOT NULL,
	FRIEND VARCHAR(200),
	-- FOREIGN KEY (EVENT) REFERENCES EVENT(EVENT_ID) ON DELETE CASCADE,
	-- FOREIGN KEY (FRIEND) REFERENCES USERS(USER_ID) ON DELETE CASCADE,
	PRIMARY KEY(BET_ID)
);