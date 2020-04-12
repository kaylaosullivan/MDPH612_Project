import psycopg2



database_name = "db612"
user_name = "postgres"
password = "1202db"
host = "127.0.0.1"
port = "5432"

con = psycopg2.connect(database=database_name, user=user_name, password=password, host=host, port=port)

print("Database opened successfully")

cur = con.cursor()

cur.execute('''CREATE TABLE PATIENT
      (ADMISSION INT PRIMARY KEY     NOT NULL,
      NAME           TEXT    NOT NULL,
      AGE            INT     NOT NULL,
      COURSE        CHAR(50),
      DEPARTMENT        CHAR(50));''')

print("Table created successfully")


# cur.execute("INSERT INTO STUDENT (ADMISSION,NAME,AGE,COURSE,DEPARTMENT) VALUES (3420, 'John', 18, 'Computer Science', 'ICT')")
# cur.execute("INSERT INTO STUDENT (ADMISSION,NAME,AGE,COURSE,DEPARTMENT) VALUES (3421, 'John', 18, 'Computer Science', 'ICT')")
# cur.execute("INSERT INTO STUDENT (ADMISSION,NAME,AGE,COURSE,DEPARTMENT) VALUES (3422, 'Antony', 19, 'Electrical Engineering', 'Engineering')")
# cur.execute("INSERT INTO STUDENT (ADMISSION,NAME,AGE,COURSE,DEPARTMENT) VALUES (3423, 'Alice', 18, 'Information Technology', 'ICT')")

# print("Record inserted successfully")


# con.commit()

# cur.execute("SELECT admission, name, age, course, department from STUDENT")
# cur.execute("SELECT name, age, department from STUDENT WHERE ADMISSION = 3421")
# cur.execute("SELECT name, age, department from STUDENT WHERE NAME = 'John' ")
# cur.execute("SELECT name, age, department from STUDENT WHERE DEPARTMENT = 'ICT       ' ")
# cur.execute("SELECT name, age, department from STUDENT WHERE DEPARTMENT = 'ICT       ' OR NAME='Antony'")

# rows = cur.fetchall()

# for row in rows:
#     print (row)


# # cur.execute("UPDATE STUDENT set AGE = 20 where ADMISSION = 3420")
# # con.commit()


# # cur.execute("DELETE from STUDENT where ADMISSION=3420;")
# # con.commit()

# con.close()
