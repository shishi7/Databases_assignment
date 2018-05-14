from faker import Faker
from random_words import RandomWords, RandomNicknames
from typing import List
import math
import psycopg2
import random
from string import ascii_uppercase, digits

VEH_COLORS = ['red', 'green', 'black', 'vantablack', 'invisible', 'blue', 'white', 'chrome']

MANUF_LIST_STR = ['Nissan', 'Toyota', 'Jaguar', 'Bugatti', 'Lamborghini', 'McLaren', 'Koenigsegg', 'Mitsubishi',
                  'Renault', 'Audi', 'Porsche']
REG_NUMBER_SIZE = 7

last_coordinates = None


def getRandomCoordinates():
    """
    Get random tuple - gps coordinates.
    """
    global last_coordinates
    if last_coordinates is None or random.uniform(0.0, 1.0) > 0.3:
        last_coordinates = (random.uniform(-100.0, 100.0), random.uniform(-100.0, 100.0))
    return last_coordinates


def getRandomRegistration():
    """
    Get randomly generated registration plate for vehicle.

    :return: Registration plate's text
    """
    reg_number = ''.join(random.choice(ascii_uppercase + digits) for _ in range(REG_NUMBER_SIZE))
    if random.uniform(0.0, 1.0) < 0.85:
        reg_number = "AN" + reg_number[:-2]
    return reg_number


def getRandomTime():
    """
    Get randomly generated time moment.

    :return: Time
    """
    return str(random.randint(0, 23)) + ":" + str(random.randint(0, 59)) + ":" + str(random.randint(0, 59))


def getRandomDateString():
    """
    Get randomly generated date.

    :return: Date
    """
    year = 2017
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return str(year) + "-" + str(month) + "-" + str(day)


def addGPSEntry(latitude, longitude):
    """
    Insert new value into GPS table and return linking gps_id.

    :param latitude:  float value
    :param longitude: float value
    :return: gps_id integer
    """
    cursor.execute("INSERT INTO GPS (latitude, longitude) VALUES (%s,%s) RETURNING gps_id;",
                   (latitude, longitude))
    id = cursor.fetchone()[0]
    conn.commit()
    return id


def addCustomer(username, name, surname, email, is_blocked=False):
    """
    Add new customer into Customers table.

    :param username: Customer username
    :param name: Customer first name
    :param surname: Customer second name
    :param email: Customer email
    :param is_blocked: True if customer is in black list
    """
    try:
        cursor.execute(
            "INSERT INTO Customers (username, name, surname, email, is_blocked) VALUES (%s,%s,%s,%s,%s);",
            (username, name, surname, email, is_blocked))
    except:
        pass
    conn.commit()


def addSocket(socket_number, is_available, s_id):
    """
    Add new entry into Sockets table for according Charging Station.

    :param socket_number: total number of sockets
    :param is_available: state of socket
    :param s_id: id of charging station current socket belongs to
    """
    cursor.execute("INSERT INTO Sockets (socket_number, is_available, s_id) VALUES (%s,%s,%s);",
                   (socket_number, is_available, s_id))
    conn.commit()


def addChargingStation(num_sockets, is_available, gps_coord=(0, 0)):
    """
    Add new entry into Charging stations table.

    :param num_sockets: total number of sockets
    :param is_available: state of current charging station, boolean
    :param gps_coord: tuple of floats representing gps coordinates
    """
    gps_id = addGPSEntry(gps_coord[0], gps_coord[1])
    cursor.execute(
        "INSERT INTO Charging_stations (gps_id, is_available) VALUES (%s,%s) RETURNING s_id;",
        (gps_id, is_available))
    s_id = cursor.fetchone()[0]
    for i in range(0, num_sockets):
        addSocket(i + 1, is_available, s_id)
    conn.commit()


def addVehicle(reg_number, color, charge_level, state, model_id, gps_coord=(0, 0)):
    """
    Add new entry in Vehicles table.

    :param reg_number: Vehicle registration number
    :param color: Color of the vehicle
    :param charge_level: charge level of current vehicle
    :param state: state of vehicle: 'free', 'ordered', 'executing', 'in_service', 'broken', 'charging'
    :param model_id: id of according model
    :param gps_coord: tuple of floats representing gps coordinates
    """
    gps_id = addGPSEntry(gps_coord[0], gps_coord[1])
    cursor.execute(
        "INSERT INTO Vehicles (reg_number, color, charge_level, state, gps_id, model_id) VALUES (%s,%s,%s,%s,%s,%s);",
        (reg_number, color, charge_level, state, gps_id, model_id))
    conn.commit()


def addModel(manuf_id, name, bag_cap, seats_amount):
    """
    Add new entry into Models table.

    :param manuf_id: id of according manufacturer
    :param name: actual name of given model
    :param bag_cap: baggage capacity
    :param seats_amount: number of passenger seats in vehicle
    """
    cursor.execute("INSERT INTO Models (manuf_id, name, bag_cap, seats_amount) VALUES (%s,%s,%s,%s);",
                   (manuf_id, name, bag_cap, seats_amount))


def addManufacturers(names: List[str]):
    """
    Add new entry into Manufacturers table.

    :param names: name of manufacturer
    """
    for name in names:
        cursor.execute("INSERT INTO Manufacturers (name) VALUES (%s);", [name])
        conn.commit()


def addCard(number, date, c_id):
    """
    Add new entry into Cards table.

    :param number: card number
    :param date: card expiration date in format "mm/yy"
    :param c_id: id of owner (customer from Customers table)
    """
    cursor.execute("INSERT INTO Cards (number, date, c_id) VALUES (%s,%s,%s);",
                   (number, date, c_id))
    conn.commit()


def addOrder(c_id, v_id, date, time, departure: tuple, destination: tuple, state, to_user_dist, with_user_dist,
             cost):
    """
    Add new entry into Orders table.

    :param c_id: id of customer
    :param v_id: id of vehicle
    :param date: date of order
    :param time: time of order
    :param departure: gps_id of departure
    :param destination: gps_id of destination
    :param state: order state: 'processing', 'executing', 'cancelled', 'complete'
    :param to_user_dist: to user distance, in km
    :param with_user_dist: distance with user, in km
    :param cost: amount of money, actual cost of given order
    :return order id
    """
    cursor.execute(
        "INSERT INTO Orders (c_id, v_id, date, time, departure, destination, state, to_user_dist, with_user_dist, cost) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING o_id;",
        (c_id, v_id, date, time, departure, destination, state, to_user_dist, with_user_dist, cost))
    o_id = cursor.fetchone()[0]
    conn.commit()
    return o_id


def addTransaction(o_id, card_id, amount, date, time):
    """
    Add new entry into Transactions table.

    :param o_id: Order id
    :param card_id: Card id
    :param amount: Money value of transaction
    :param date: Date of transaction
    :param time: Time of transaction
    :return:
    """
    cursor.execute(
        "INSERT INTO Transactions (o_id, card_id, amount, date, time) VALUES (%s,%s,%s,%s,%s);",
        (o_id, card_id, amount, date, time))
    conn.commit()


def getIDListfromTable(table: str):
    """
    Construct list of all id's (primary keys) in table.

    :param table: name of table to take data from
    """
    result = []
    cursor.execute("SELECT * FROM {0};".format(table))
    for entry in cursor:
        result.append(entry[0])
    conn.commit()
    return result


def calculateDistance(a: tuple, b: tuple):
    """
    Calculate euclidian distance between two points represented by tuples.

    :param a: Point a
    :param b: Point b
    """
    return math.sqrt(math.pow(b[0] - a[0], 2) + math.pow(b[1] - a[1], 2))


def fillDBwithRandomData(amount: int):
    """
    Fill database with random data.

    :param amount: index of generated data amount, recommended 2-20
    """
    # add manufacturers
    addManufacturers(MANUF_LIST_STR)
    manuf_list = getIDListfromTable("Manufacturers")
    # add charging stations
    for i in range(0, int(amount / 4) + 1):
        addChargingStation(random.randint(7, 77), random.choice([True, False]), gps_coord=getRandomCoordinates())
    # add customers
    for i in range(0, amount * 7):
        name = fake.name().split()
        is_blocked = False if random.uniform(0.0, 1.0) < 0.91 else True
        addCustomer(run.random_nick(gender='u').lower(), name[0], name[1], fake.email(),
                    is_blocked=is_blocked)
    # add vehicle models
    for i in range(0, amount):
        addModel(random.choice(manuf_list), rw.random_word().capitalize(),
                 random.randint(14, 65), random.randint(2, 6))
    # add vehicles
    for i in range(0, amount * 3):
        addVehicle(getRandomRegistration(), random.choice(VEH_COLORS), random.randint(0, 100),
                   random.choice(['free', 'ordered', 'executing', 'in_service', 'broken', 'charging']),
                   random.choice(getIDListfromTable("Models")),
                   gps_coord=getRandomCoordinates())
    cust_list = getIDListfromTable("Customers")
    #  add bank cards
    for i in range(0, amount * 10):
        addCard(random.randint(10000000, 99999999),
                str(str(random.randint(1, 12)) + "/" + str(random.randint(16, 30))), random.choice(cust_list))
    veh_list = getIDListfromTable("Vehicles")
    # add orders
    for i in range(0, amount * 15):
        from_coord = getRandomCoordinates()
        to_coord = getRandomCoordinates()
        from_coord_gps = addGPSEntry(from_coord[0], from_coord[1])
        to_coord_gps = addGPSEntry(to_coord[0], to_coord[1])
        distance = calculateDistance(from_coord, to_coord)
        cost = random.randint(1, 100)
        date = getRandomDateString()
        time = getRandomTime()
        o_id = addOrder(random.choice(cust_list), random.choice(veh_list), date, time,
                        from_coord_gps, to_coord_gps,
                        random.choice(['processing', 'executing', 'cancelled', 'complete']), distance,
                        distance * random.uniform(0.1, 0.999), cost)
        card_list = getIDListfromTable("Cards")
        card_id = random.choice(card_list)
        amount_ = random.uniform(5.0, 15.0)
        addTransaction(o_id, card_id, amount_, date, time)
        if random.uniform(0.0, 1.0) < 0.2:
            addTransaction(o_id, card_id, amount_, date, time)


def fill_database(db_name: str, password: str):
    """
    Fill in the database for car sharing company with some random data.

    :param db_name: Database name
    :param password: Database manager's password (user: postgres)
    """
    global fake
    global rw
    global run
    global conn
    global cursor

    fake = Faker()
    rw = RandomWords()
    run = RandomNicknames()

    conn = psycopg2.connect(host='localhost', dbname=db_name, user='postgres', password=password, async=0)
    cursor = conn.cursor()
    fillDBwithRandomData(12)
    cursor.close()
    conn.close()

    print('Database was filled with random data successfully!\n')
