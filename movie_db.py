import sqlite3 as lite
import csv
import re
import pandas as pd
import argparse
import collections
import json
import glob
import math
import os
import requests
import string
import sqlite3
import sys
import time
import xml


class Movie_db(object):
    def __init__(self, db_name):
        #db_name: "cs1656-public.db"
        self.con = lite.connect(db_name)
        self.cur = self.con.cursor()
        
        
    
    #q0 is an example 
    def q0(self):
        query = '''SELECT count(*) from Actors'''
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows

    # Actors (aid, fname, lname, gender)
    # Movies (mid, title, year, rank)
    # Directors (did, fname, lname)
    # Cast (aid, mid, role)
    # Movie_Director (did, mid)
    #need Actors, Movies, Cast
    #done
    def q1(self):
        query = '''
        SELECT Actors.fname, Actors.lname
        FROM Cast AS c INNER JOIN Actors ON c.aid = Actors.aid
        WHERE c.aid in (SELECT c.aid
                        FROM Cast AS c INNER JOIN Movies AS m ON m.mid = c.mid
                        WHERE m.year < 1990 AND m.year > 1980) 
        AND c.aid in (SELECT c.aid
                        FROM Cast AS c INNER JOIN Movies AS m ON m.mid = c.mid
                        WHERE m.year >= 2000) 
        GROUP BY c.aid 
        '''
        #returns fname and lname of actor in movies in specified years 
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows
        
    #done
    #show movoes made in the same year as Rogue One with a better rank
    def q2(self):
        query = '''
        SELECT title, year
        FROM Movies
        WHERE year in (SELECT Movies.year
                            FROM Movies
                            WHERE title = "Rogue One: A Star Wars Story")
        AND rank > (SELECT rank
                    FROM Movies
                    WHERE title = "Rogue One: A Star Wars Story")
        ORDER BY title
            
        '''
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows

    def q3(self):
        self.cur.execute('DROP VIEW IF EXISTS v')
        self.cur.execute('CREATE VIEW v as SELECT a.fname, a.lname, SUM(m.mid) as cc FROM Actors as a INNER JOIN Cast as c ON a.aid = c.aid INNER JOIN Movies as m ON c.mid = m.mid WHERE m.title LIKE "%Star Wars%" GROUP By a.fname, a.lname ORDER BY cc DESC;')
        query = '''
        SELECT v.fname, v.lname 
        FROM v  
        GROUP BY v.fname, v.lname
        ORDER BY v.cc desc, v.lname, v.fname     
        '''
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows


    def q4(self):
        #done
        query = '''
        SELECT a.fname, a.lname
        FROM Actors as a INNER JOIN Cast as c on a.aid=c.aid
        INNER JOIN Movies as m ON c.mid=m.mid
        WHERE NOT a.aid IN (SELECT ac.aid
                        FROM Actors AS ac
                        INNER JOIN Cast AS ca ON ac.aid = ca.aid
                        INNER JOIN Movies AS mo ON mo.mid = ca.mid
                        WHERE mo.year > 1980) 
        GROUP BY a.fname, a.lname
        ORDER BY a.lname, a.fname    
        '''
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows

        #top 10 directors
        #done
    def q5(self):
        query = '''
        SELECT Directors.fname, Directors.lname, count(*) AS c
        FROM Directors
        INNER JOIN Movie_Director m on m.did = Directors.did
        GROUP BY Directors.lname, Directors.fname
        ORDER BY c DESC, Directors.lname, Directors.fname 
        LIMIT 10
        '''
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows

        #done
        #show movies and cast count in decreasing order 
    def q6(self):    
        query = '''
        SELECT m.title, COUNT(DISTINCT c.aid) AS cast_count
        FROM Movies as m INNER JOIN Cast as c ON c.mid = m.mid
        GROUP BY m.mid
        HAVING cast_count >= (SELECT MIN(n)
                            FROM (SELECT COUNT(ca.aid) AS n
                                  FROM Movies as mo INNER JOIN Cast as ca ON ca.mid = mo.mid
                                  GROUP BY mo.mid
                                  ORDER BY n DESC
                                  LIMIT 10))
        ORDER BY cast_count DESC
        '''
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows

    #more females than males
    def q7(self):
        self.cur.execute('DROP VIEW IF EXISTS q7a')
        self.cur.execute('CREATE VIEW q7a AS SELECT m.title as title, a.gender AS gender FROM Actors as a INNER JOIN Cast as c on c.aid = a.aid INNER JOIN Movies as m on c.mid = m.mid GROUP BY fname, lname, m.title;')
        self.cur.execute('DROP VIEW IF EXISTS q7b')
        self.cur.execute('CREATE VIEW q7b AS SELECT q7a.title as title, sum(CASE WHEN q7a.gender = "Female" THEN 1 ELSE 0 END) AS FEM, sum(CASE WHEN q7a.gender = "Male" THEN 1 ELSE 0 END) AS MALE FROM q7a GROUP BY q7a.title;')
        query = '''
        SELECT q7b.title, q7b.FEM, q7b.MALE
        FROM q7b
        WHERE q7b.FEM > q7b.MALE
        '''
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows

        #actors who worked w at least 7 directors 
    def q8(self):
        query = '''
        SELECT a.fname, a.lname, COUNT(DISTINCT m_d.did) AS cc
        FROM Actors AS a
        INNER JOIN Cast AS c ON a.aid = c.aid
        INNER JOIN Movie_Director AS m_d ON c.mid = m_d.mid
        GROUP BY a.aid, a.fname, a.lname
        HAVING cc >= 7 
        ORDER BY cc DESC, a.lname, a.fname          
        '''
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows


    def q9(self):
        self.cur.execute('DROP VIEW IF EXISTS d')
        self.cur.execute('CREATE VIEW d AS SELECT Actors.aid, Actors.fname, Actors.lname FROM Actors WHERE Actors.fname LIKE "D%" GROUP BY Actors.aid;')
        self.cur.execute('DROP VIEW IF EXISTS minyr')
        self.cur.execute('CREATE VIEW minyr AS SELECT c.aid, MIN(m.year) as min_year FROM Movies as m INNER JOIN Cast as c on m.mid=c.mid INNER JOIN d ON c.aid=d.aid GROUP BY c.aid')

        query = '''
        SELECT d.fname, d.lname, count(m.mid) as cc
        FROM d INNER JOIN Cast as c ON d.aid=c.aid INNER JOIN Movies as m ON c.mid=m.mid INNER JOIN minyr on minyr.aid=c.aid
        WHERE m.year= minyr.min_year 
        GROUP BY d.fname, d.lname
        ORDER by cc DESC    
        '''
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows
    #where actors and directors have the same last
    def q10(self):
        query = '''
        SELECT a.lname, m.title
        FROM Actors AS a
        INNER JOIN Cast AS c ON a.aid = c.aid
        INNER JOIN Movies AS m ON c.mid = m.mid
        INNER JOIN Movie_Director AS md ON c.mid = md.mid
        INNER JOIN Directors AS d ON d.did = md.did
        WHERE a.lname = d.lname
        ORDER BY a.lname, m.title     
        '''
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows

    def q11(self):
        query = '''
            
        '''
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows
        #top 20 most popular actors
        #done
    def q12(self):
        query = '''
        SELECT a.fname, a.lname, COUNT(m.mid), AVG(m.rank) AS p
        FROM Actors AS a INNER JOIN Cast AS c ON a.aid = c.aid
        INNER JOIN Movies AS m ON c.mid = m.mid
        GROUP BY a.aid
        ORDER BY p DESC
        LIMIT 20
        '''
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows

if __name__ == "__main__":
    task = Movie_db("cs1656-public.db")
    rows = task.q0()
    print(rows)
    print()
    rows = task.q1()
    print(rows)
    print()
    rows = task.q2()
    print(rows)
    print()
    rows = task.q3()
    print(rows)
    print()
    rows = task.q4()
    print(rows)
    print()
    rows = task.q5()
    print(rows)
    print()
    rows = task.q6()
    print(rows)
    print()
    rows = task.q7()
    print(rows)
    print()
    rows = task.q8()
    print(rows)
    print()
    rows = task.q9()
    print(rows)
    print()
    rows = task.q10()
    print(rows)
    print()
    rows = task.q11()
    print(rows)
    print()
    rows = task.q12()
    print(rows)
    print()