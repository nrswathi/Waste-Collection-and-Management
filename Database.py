import mysql.connector
mydb=mysql.connector.connect(
    host="localhost",
    user="root",
    password="****", #use your password
    database="wastedata"
)
mycursor=mydb.cursor()

sql_command="""CREATE DATABASE wastedata"""

#sql_command="""CREATE TABLE rooms( Room_no INT PRIMARY KEY,Department VARCHAR(10), Floor INT );"""

#sql_command="""CREATE TABLE bin(ID_num INT PRIMARY KEY, Room_no INT,
#                 FOREIGN KEY(Room_no) REFERENCES rooms(Room_no)); """

#sql_command="""CREATE TABLE binalert(ID_num INT , Alert_datetime DATETIME ,
#               CONSTRAINT PK_binalert PRIMARY KEY(ID_num,Alert_datetime),
#               CONSTRAINT FK_binalert FOREIGN KEY (ID_num) REFERENCES bin(ID_num));"""

#sql_command="""CREATE TABLE cleaner(Cleaner_ID VARCHAR(10) PRIMARY KEY, First_name VARCHAR(15), Last_name VARCHAR(15), Gender CHAR(1), DOB DATE, Contact_no CHAR(10),C_password VARCHAR(20)); """

#sql_command="""CREATE TABLE empty_bin(Bin_ID INT, Cleaner_ID VARCHAR(10), Collected_datetime DATETIME,
#                CONSTRAINT FK_empty1 FOREIGN KEY(Bin_ID) REFERENCES bin(ID_num),
#                CONSTRAINT FK_empty2 FOREIGN KEY(Cleaner_ID) REFERENCES cleaner(Cleaner_ID),
#                CONSTRAINT PK_empty PRIMARY KEY (Collected_datetime));"""

#sql_command="""CREATE TABLE waste(ID_num INT PRIMARY KEY, Wet_qty DECIMAL(5,2), Dry_qty DECIMAL(5,2), Total_qty DECIMAL(6,2),
 #               CONSTRAINT FK_waste FOREIGN KEY (ID_num ) REFERENCES bin(ID_num));"""
#sql_command= """CREATE TABLE administrator(Admin_ID VARCHAR(10) PRIMARY KEY, First_name VARCHAR(10), Last_name VARCHAR(10),
 #               A_password VARCHAR(10), Contact_no CHAR(10));"""



mycursor.execute(sql_command)
