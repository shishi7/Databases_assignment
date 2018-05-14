import psycopg2

DB_NAME = 'self_driving'


def main():
    print('Welcome to TaxiApp!\n')
    password = input("Please, enter DB manager's password: ")

    while True:
        print('Choose what you want to know:')
        print('1 - Find red cars which plates starts with "AN"')
        print('2 - Get statistics for one week on how many taxis are busy during the morning, afternoon and evening')
        print('3 - Check someone for double paying')
        print("4 - Average distance a car has to travel per day to customer's order location; Average trip duration")
        print('5 - Top-3 most popular pick-up locations and travel destination for morning, afternoon and evening')
        print('0 - Exit')
        tmp = input('> ')

        conn = psycopg2.connect(host='localhost', dbname=DB_NAME, user='postgres', password=password)
        cursor = conn.cursor()

        if tmp == '0':
            print('\nSee you soon!..')
            break
        elif tmp == '1':
            query = '''SELECT *
                       FROM vehicles
                       WHERE color = 'red' AND reg_number LIKE 'AN%' '''
            cursor.execute(query)
            res = cursor.fetchall()
            for row in res:
                for i in row:
                    print(i, end=' ')
                print()
        elif tmp == '2':
            dateSt = input('Please, enter the first day of required week in format yyyy-mm-dd: ')
            dateFn = input('\nPlease, enter the last day of required week in format yyyy-mm-dd: ')
            queryFt = '''SELECT COUNT(DISTINCT v_id)
                         FROM (
                           SELECT v_id, time
                           FROM Orders
                           WHERE date BETWEEN '{0}' AND '{1}'
                         ) AS foo
                         WHERE time BETWEEN '7:00' AND '10:00' '''.format(dateSt, dateFn)
            querySd = '''SELECT COUNT(DISTINCT v_id)
                         FROM (
                           SELECT v_id, time
                           FROM Orders
                           WHERE date BETWEEN '{0}' AND '{1}'
                         ) AS foo
                         WHERE time BETWEEN '12:00' AND '14:00' '''.format(dateSt, dateFn)
            queryTd = '''SELECT COUNT(DISTINCT v_id)
                         FROM (
                           SELECT v_id, time
                           FROM Orders
                           WHERE date BETWEEN '{0}' AND '{1}'
                         ) AS foo
                         WHERE time BETWEEN '17:00' AND '19:00' '''.format(dateSt, dateFn)
            query = '''SELECT COUNT (DISTINCT v_id)
                       FROM Orders
                       WHERE date BETWEEN '{0}' AND '{1}' '''.format(dateSt, dateFn)
            cursor.execute(query)
            total = cursor.fetchone()[0]
            if total == 0:
                total = 1
            cursor.execute(queryFt)
            res = cursor.fetchone()[0] / total * 100
            print('Morning: {}'.format(res))
            cursor.execute(querySd)
            res = cursor.fetchone()[0] / total * 100
            print('Afternoon: {}'.format(res))
            cursor.execute(queryTd)
            res = cursor.fetchone()[0] / total * 100
            print('Evening: {}'.format(res))
        elif tmp == '3':
            query = '''SELECT Transactions.o_id, Customers.username, count(*)
                       FROM Transactions
                         INNER JOIN Cards ON Transactions.card_id=Cards.card_id
                         INNER JOIN Customers ON Cards.c_id=Customers.c_id
                       WHERE Transactions.date >= date_trunc('month', current_date - interval '1' month)
                         AND Transactions.date < date_trunc('month', current_date)
                       GROUP BY Transactions.o_id, Customers.username
                       HAVING count(*) > 1'''
            cursor.execute(query)
            res = cursor.fetchall()
            if cursor.rowcount == 0:
                print('No double-paying found.')
            else:
                for row in res:
                    for i in row:
                        print(i, end=' ')
                    print()
        elif tmp == '4':
            date = input('Please, enter the date in format yyyy-mm-dd: ')
            query = '''SELECT AVG(to_user_dist)AS to, AVG(with_user_dist)AS with
                       FROM Orders 
                       WHERE Date = '{0}' '''.format(date)
            cursor.execute(query)
            res = cursor.fetchone()
            print('Average distance to customer: {}'.format(res[0]))
            print('Average distance with customer: {}'.format(res[1]))
        elif tmp == '5':
            queryFt_from = '''SELECT Departure, count(*) AS cnt FROM Orders
                              WHERE time BETWEEN '7:00' AND '10:00' GROUP BY 1 LIMIT 3'''
            queryFt_to = '''SELECT destination, count(*) AS cnt FROM Orders
                            WHERE time BETWEEN '7:00' AND '10:00' GROUP BY 1 LIMIT 3'''
            querySd_from = '''SELECT Departure, count(*) AS cnt FROM Orders
                              WHERE time BETWEEN '12:00' AND '14:00' GROUP BY 1 LIMIT 3'''
            querySd_to = '''SELECT destination, count(*) AS cnt FROM Orders
                            WHERE time BETWEEN '12:00' AND '14:00' GROUP BY 1 LIMIT 3'''
            queryTd_from = '''SELECT Departure, count(*) AS cnt FROM Orders
                              WHERE time BETWEEN '17:00' AND '19:00' GROUP BY 1 LIMIT 3'''
            queryTd_to = '''SELECT destination, count(*) AS cnt FROM Orders
                            WHERE time BETWEEN '17:00' AND '19:00' GROUP BY 1 LIMIT 3'''
            cursor.execute(queryFt_from)
            res_from = cursor.fetchall()
            cursor.execute(queryFt_to)
            res_to = cursor.fetchall()
            print('Morning (departure, how many); (destination, how many) :\n{0}; {1}\n{2}; {3}\n{4}; {5}'.format(
                res_from[0], res_to[0], res_from[1], res_to[1], res_from[2], res_to[2]))
            cursor.execute(querySd_from)
            res_from = cursor.fetchall()
            cursor.execute(querySd_to)
            res_to = cursor.fetchall()
            print('Afternoon (departure, how many); (destination, how many):\n{0}; {1}\n{2}; {3}\n{4}; {5}'.format(
                res_from[0], res_to[0], res_from[1], res_to[1], res_from[2], res_to[2]))
            cursor.execute(queryTd_from)
            res_from = cursor.fetchall()
            cursor.execute(queryTd_to)
            res_to = cursor.fetchall()
            print('Evening (departure, how many); (destination, how many):\n{0}; {1}\n{2}; {3}\n{4}; {5}'.format(
                res_from[0], res_to[0], res_from[1], res_to[1], res_from[2], res_to[2]))
        else:
            print('Contract violation: wrong input!')
        conn.close()
        print()


if __name__ == '__main__':
    main()
