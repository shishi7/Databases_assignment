import psycopg2

_query = '''
-- Enums --

DROP TYPE IF EXISTS VEH_STATES CASCADE;
CREATE TYPE VEH_STATES AS ENUM ('free', 'ordered', 'executing', 'in_service', 'broken', 'charging');

DROP TYPE IF EXISTS ORDER_STATES CASCADE;
CREATE TYPE ORDER_STATES AS ENUM ('processing', 'executing', 'cancelled', 'complete');

-- Main schema --

DROP TABLE IF EXISTS Customers CASCADE;
CREATE TABLE Customers (
  c_id       SERIAL PRIMARY KEY,
  username   TEXT UNIQUE NOT NULL,
  name       TEXT,
  surname    TEXT,
  email      TEXT NOT NULL,
  is_blocked BOOLEAN NOT NULL
);

DROP TABLE IF EXISTS Cards CASCADE;
CREATE TABLE Cards (
  card_id SERIAL PRIMARY KEY,
  number  VARCHAR(16) NOT NULL,
  date    VARCHAR(5) NOT NULL,
  c_id    INTEGER REFERENCES Customers(c_id)
);

DROP TABLE IF EXISTS Manufacturers CASCADE;
CREATE TABLE Manufacturers (
  manuf_id SERIAL PRIMARY KEY,
  name     TEXT UNIQUE NOT NULL
);

DROP TABLE IF EXISTS Models CASCADE;
CREATE TABLE Models (
  model_id     SERIAL PRIMARY KEY,
  manuf_id     INTEGER REFERENCES Manufacturers(manuf_id),
  name         TEXT NOT NULL,
  bag_cap      INTEGER NOT NULL,
  seats_amount INTEGER NOT NULL
);

DROP TABLE IF EXISTS GPS CASCADE;
CREATE TABLE GPS (
  gps_id    SERIAL PRIMARY KEY,
  latitude  FLOAT,
  longitude FLOAT
);

DROP TABLE IF EXISTS Vehicles CASCADE;
CREATE TABLE Vehicles (
  v_id         SERIAL PRIMARY KEY,
  reg_number   TEXT NOT NULL,
  color        TEXT,
  charge_level INTEGER NOT NULL,
  state        VEH_STATES,
  gps_id       INTEGER REFERENCES GPS(gps_id),
  model_id     INTEGER REFERENCES Models(model_id)
);

DROP TABLE IF EXISTS Charging_stations CASCADE;
CREATE TABLE Charging_stations (
  s_id         SERIAL PRIMARY KEY,
  gps_id       INTEGER REFERENCES GPS(gps_id),
  is_available BOOLEAN
);

DROP TABLE IF EXISTS Sockets CASCADE;
CREATE TABLE Sockets (
  socket_number INTEGER,
  is_available  BOOLEAN,
  s_id          INTEGER REFERENCES Charging_stations(s_id),
  PRIMARY KEY(socket_number, s_id)
);

DROP TABLE IF EXISTS Orders CASCADE;
CREATE TABLE Orders (
  o_id           SERIAL PRIMARY KEY,
  c_id           INTEGER REFERENCES Customers(c_id),
  v_id           INTEGER REFERENCES Vehicles(v_id),
  date           DATE NOT NULL,
  time           TIME NOT NULL,
  departure      INTEGER REFERENCES GPS(gps_id),
  destination    INTEGER REFERENCES GPS(gps_id),
  state          ORDER_STATES,
  to_user_dist   FLOAT NOT NULL,
  with_user_dist FLOAT NOT NULL,
  cost           FLOAT NOT NULL
);

DROP TABLE IF EXISTS Transactions CASCADE;
CREATE TABLE Transactions (
  t_id SERIAL PRIMARY KEY,
  o_id INTEGER REFERENCES Orders(o_id),
  card_id INTEGER REFERENCES Cards(card_id),
  amount INTEGER NOT NULL,
  date DATE NOT NULL,
  time TIME
);'''


def initialise_schema(db_name: str, password: str):
    """
    Initialise base schema of the DB for car sharing system.
    NOTE: You need to enter PostgreSQL DB manager's password.

    :param db_name: Name of the DB
    :param password: Database manager's password (user: postgres)
    """
    conn = psycopg2.connect(host='localhost', dbname=db_name, user='postgres', password=password)
    cursor = conn.cursor()
    cursor.execute(_query)
    conn.commit()
    conn.close()

    print('Database schema was created successfully!\n')
