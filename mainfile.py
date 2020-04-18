from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_pymongo import PyMongo
import pymysql
from mysqlx import IntegrityError

pymysql.install_as_MySQLdb()
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from wtforms import Form, StringField, PasswordField, validators, SubmitField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from random import randint
from datetime import datetime

app=Flask(__name__)
app.config['SECRET_KEY']='wasteaf'
app.config["MONGO_URI"] = "mongodb://localhost:27017/wastedatabase"
mongo = PyMongo(app)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '***' #enter your password
app.config['MYSQL_DB'] = 'wastedata'

mysql = MySQL(app)


@app.route('/')
def screen1():
    return render_template('openscreen.html')


@app.route('/adminlogin',methods=['GET', 'POST'])
def screen2():
    msg=''
    if request.method == 'POST' and 'username' in request.form and 'pass' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['pass']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM administrator WHERE Admin_ID = %s AND A_Password = %s', (username, password))
        account = cursor.fetchone()
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['ID'] = account['Admin_ID']
            session['username']= account['First_name']
            # Redirect to home page
            return redirect(url_for('screen8'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
        # Show the login form with message (if any)
    return render_template('index.html',msg=msg)


@app.route('/stafflogin',methods=['GET', 'POST'])
def screen3():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'pass' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['pass']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM cleaner WHERE Cleaner_ID = %s AND C_Password = %s', (username, password))
        account = cursor.fetchone()
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['cleanerid'] = account[0]
            #session['username'] = account['First_name']
            # Redirect to home page
            return redirect(url_for('screen14'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
        # Show the login form with message (if any)
    return render_template('indexstaff.html',msg=msg)

@app.route('/adminpage')
def screen4():
    return render_template('adminpage.html')

@app.route('/contactus')
def screen5():
    return render_template('contactus.html')

@app.route('/aboutus')
def screen6():
    todisplay=mongo.db.cleaners.find()
    return render_template('aboutus.html',todisplay=todisplay)

@app.route('/stat',methods=['GET', 'POST'])
def screen7():
    import datetime
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    today = datetime.date.today()
    week_ago = today - datetime.timedelta(days=7)
    query="""select SUM(Wet_qty) as wet,SUM(Dry_qty) as dry,SUM(Total_qty) as tot  from wastes where Collected_datetime between %s and %s """
    val=(week_ago,today)
    cursor.execute(query,val)
    quant=cursor.fetchone()
    #query="""SELECT cleaner.First_name, cleaner.Last_name, SUM(Total_qty) as Amount  FROM cleaner,empty_bin where Cleaner_ID in (select top 3 empty_bin.Cleaner_ID from empty_bin  inner join waste on empty_bin.Bin_ID= waste.ID_num  order by Total_qty desc)"""
    query="""select cleaner.First_name, cleaner.Last_name, SUM(Total_qty) as Amount from ((wastes NATURAL JOIN empty_bin )natural join cleaner) group by cleaner.Cleaner_ID order by SUM(wastes.Total_qty) desc"""
    cursor.execute(query)
    top=cursor.fetchall()
    query="""select empty_bin.Bin_ID,Cleaner_ID from empty_bin order by Collected_datetime desc limit 4"""
    cursor.execute(query)
    recent=cursor.fetchall()
    query="""select department from rooms join bin join wastes order by total_qty desc limit 1"""
    cursor.execute(query)
    sqltest = cursor.fetchall()
    return render_template('stat.html',quant=quant,top=top,recent=recent,sqltest=sqltest)

@app.route('/admin',methods=['GET', 'POST'])
def screen8():
    if request.method == 'POST':
        cursor = mysql.connection.cursor()
        binid = request.form.get('binid')
        cleanername = request.form.get('cleanername')
        query = """ select Cleaner_ID from cleaner where First_name=%s """
        val = (cleanername)
        cursor.execute(query, val)
        found = cursor.fetchone()
        cleanerid = found[0]
        query = """ insert into assigned(Bin_ID,Cleaner_ID) values(%s,%s)"""
        val = (binid, cleanerid)
        cursor.execute(query, val)
        mysql.connection.commit()
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    query=""" SELECT * FROM binalert WHERE Collected_datetime IS NULL AND NOT EXISTS (SELECT Bin_ID from assigned WHERE binalert.ID_num=assigned.Bin_ID)"""
    cursor.execute(query)
    bins = cursor.fetchall()
    cursor.execute('SELECT * FROM cleaner')
    cleaners = cursor.fetchall()
    mysql.connection.commit()

    return render_template('admin_dashboard.html', bins=bins, cleaners=cleaners)

@app.route('/addcleaner',methods=['GET', 'POST'])
def screen9():
    if request.method == 'POST':
        cursor = mysql.connection.cursor()
        first_name = request.form.get('fname')
        last_name = request.form.get('lname')
        gender = request.form.get('gender')
        dob = request.form.get('bdate')
        phone = request.form.get('phone')
        passw = request.form.get('psw')
        x=randint(100, 999)
        cleanerid=str(x)+first_name[:3]
        query ="""INSERT INTO cleaner(Cleaner_ID,First_name,Last_name,Gender,DOB,Contact_no,C_password)VALUES(%s,%s,%s,%s,%s,%s,%s)"""
        val=(cleanerid,first_name,last_name,gender,dob,phone,passw)
        cursor.execute(query,val)
        flash("Successfully Added")
        flash("Cleaner ID= "+cleanerid+" Password= "+passw,)
        mysql.connection.commit()
    return render_template('addcleaner.html')

@app.route('/addbin',methods=['GET', 'POST'])
def screen10():
    cursor = mysql.connection.cursor()
    query = """SELECT MAX(ID_num) FROM bin"""
    cursor.execute(query)
    maxid = cursor.fetchone()
    newid = maxid[0]+1
    mysql.connection.commit()
    if request.method == 'POST':
        department = request.form.get('department')
        floor = request.form.get('floor')
        roomno = request.form.get('roomno')
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            query = """INSERT INTO rooms(Room_no,Department,Floor)VALUES(%s,%s,%s)"""
            val = (roomno, department, floor)
            cursor.execute(query,val)
        except: #IntegrityError as e:
            flash("Please enter a different room number")
            return redirect(url_for('screen10'))
        query = """INSERT INTO bin(ID_num,Room_no)VALUES(%s,%s)"""
        val = (newid,roomno)
        cursor.execute(query, val)
        cursor = mysql.connection.cursor()
        query = """SELECT MAX(ID_num) FROM bin"""
        cursor.execute(query)
        maxid = cursor.fetchone()
        newid = maxid[0] + 1
        flash("Successfully Added")
        mysql.connection.commit()
    return render_template('addbin.html',maxid=maxid)

@app.route('/notifications', methods=['GET','POST'])
def screen11():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    query="""SELECT DISTINCT assigned.Bin_ID,cleaner.First_name FROM cleaner,assigned WHERE  cleaner.Cleaner_ID=assigned.Cleaner_ID """
    cursor.execute(query)
    results=cursor.fetchall()
    return render_template('notifholder.html',results=results)


@app.route('/cleanerlist',methods=['GET', 'POST'])
def screen12():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM cleaner')
    rows=cursor.fetchall()
    return render_template('cleanerlist.html',rows=rows)

@app.route('/binlist',methods=['GET', 'POST'])
def screen13():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM bin NATURAL JOIN rooms ORDER BY Department,Floor,Room_no,ID_num')
    rows=cursor.fetchall()
    return render_template('binlist.html',rows=rows)


@app.route('/cleaner',methods=['GET', 'POST'])
def screen14():
    if request.method == 'POST':
        cursor = mysql.connection.cursor()
        binid = request.form.get('binid')
        #cleanername = request.form.get('')
        date =request.form.get('date')
        alert = request.form.get('alert')
        timeinp=request.form.get('time')
        collected = date + " " + timeinp+":01"
        #collected = collected.split(" ")
        #collected[-1] = collected[-1][:4]
        #collected = " ".join(collected)
        alert = datetime.strptime(alert, '%Y-%m-%d %H:%M:%S')
        collected = datetime.strptime(str(collected), '%Y-%m-%d %H:%M:%S')
        cleanerid=request.form.get('cleanerid')
        wetqty=request.form.get('wetqty')
        dryqty=request.form.get('dryqty')
        totalqty=float(wetqty)+float(dryqty)
        if(alert>collected):
            flash("Invalid collected date and time. Cannot be greater than alert date and time.")
            return redirect(url_for('screen14'))
        query = """ delete from assigned where Bin_ID=%s """
        val = (binid)
        cursor.execute(query, val)
        query = """ update binalert set Collected_datetime=%s where ID_num=%s AND Alert_datetime=%s"""
        val = (collected,binid,alert)
        cursor.execute(query, val)
        query="""insert into empty_bin values(%s,%s,%s)"""
        val=(binid,cleanerid,collected)
        cursor.execute(query, val)
        query="""insert into wastes values(%s,%s,%s,%s,%s)"""
        val=(binid,wetqty,dryqty,totalqty,collected)
        cursor.execute(query, val)
        mysql.connection.commit()
        flash("Successfully updated")
        return redirect(url_for('screen14'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    Cleaner_ID = session['cleanerid']
    query=""" SELECT * FROM (((assigned as A JOIN binalert as BA ON BA.ID_num=A.Bin_ID) NATURAL JOIN bin as B)NATURAL JOIN rooms as R) WHERE BA.Collected_datetime IS NULL and A.Cleaner_ID=%s"""
    val=(Cleaner_ID)
    cursor.execute(query,val)
    results = cursor.fetchall()
    mysql.connection.commit()

    return render_template('cleaner_dashboard.html',results=results)

@app.route('/history/<cleanerid>',methods=['GET', 'POST'])
def screen15(cleanerid):
    #cleanerid=session['cleanerid']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    query="""SELECT * FROM  ((empty_bin as EB NATURAL JOIN cleaner as C) NATURAL JOIN binalert as BA) where EB.Cleaner_ID=%s"""
    val=(cleanerid)
    cursor.execute(query,val)
    rows=cursor.fetchall()
    return render_template('history.html',rows=rows)


if __name__ == '__main__':
    app.run(debug=True)
