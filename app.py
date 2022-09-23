
from flask import Flask, render_template, request, redirect, session, flash
import sqlite3 as sql
import os


app = Flask(__name__)
app.secret_key = os.urandom(24)


@app.route('/')
def home():
    return render_template('login.html')


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/logout')
def logout():
    session.pop('user_id')
    session.pop('uniqueid')
    return redirect('/')


@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        with sql.connect("kanban.db") as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM list where uemail=?",
                        [session['uniqueid']])
            rows = cur.fetchall()
            cur.execute("SELECT * FROM card where uemail=?",
                        [session['uniqueid']])
            columns = cur.fetchall()
            print(rows)
            print(columns)
        return render_template('dashboard.html', name=session['user_id'], rows=rows, columns=columns)
    else:
        return redirect('/')


@app.route('/list')
def list():
    if 'user_id' in session:
        return render_template('list.html', name=session['user_id'])
    else:
        return redirect('/')


@app.route('/card')
def card():

    if 'user_id' in session:
        with sql.connect("kanban.db") as con:
            cur = con.cursor()
            cur.execute("SELECT list_title FROM list where uemail=?", [
                        session['uniqueid']])
            user = cur.fetchall()
            print(user)
        return render_template('card.html', name=session['user_id'], listtitle=user)
    else:
        return redirect('/')


@app.route('/addlist', methods=['GET', 'POST'])
def addlist():
    if request.method == 'POST':
        try:
            list_title = request.form['list_title']
            list_title=list_title.strip()
            list_description = request.form['list_description']
            with sql.connect("kanban.db") as con:
                cur = con.cursor()
                cur.execute("SELECT list_title FROM list where uemail=?", [
                        session['uniqueid']])
                title=cur.fetchall()
                flag=0
                for i in title:
                    if list_title in i[0]:
                        flag=1
                        break
                if flag==1:
                    flash('list title is alredy there')
                    return redirect('/list')
                else:
                    print('lets do it')
                    cur.execute("INSERT INTO list(uemail,list_title,list_description) VALUES(?,?,?)",
                            (session['uniqueid'], list_title, list_description))
                    con.commit()
                    return redirect('/dashboard')
        except:
            con.rollback()
            flash("List is Already Created With This Name!!!")
            return redirect('/list')

    else:
        return redirect('/list')


@app.route('/addcard', methods=['GET', 'POST'])
def addcard():
    if request.method == 'POST':
        try:
            list_title = request.form['list_title']
            card_title = request.form['card_title']
            list_title=list_title.strip()
            card_title=card_title.strip()
            content = request.form['content']
            deadline = request.form['deadline']
            complete = request.form.get('complete')

            if (complete == None):
                complete = 'NotCompleted'
            print(complete)
            with sql.connect("kanban.db") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO card(uemail,list_title,card_title,content,deadline,complete) VALUES(?,?,?,?,?,?)",
                            (session['uniqueid'], list_title, card_title, content, deadline, str(complete)))
                con.commit()
                return redirect('/dashboard')
        except:
            con.rollback()
            print('error in insertion')
            return redirect('/card')

    else:
        print('error in post')
        return redirect('/card')


@app.route('/login_validation', methods=['GET', 'POST'])
def login_validation():
    if request.method == 'POST':
        try:
            uemail = request.form['uemail']
            upassword = request.form['upassword']
            with sql.connect("kanban.db") as con:
                cur = con.cursor()
                cur.execute(
                    "SELECT * FROM signup WHERE uemail=? and upassword=?", (uemail, upassword))
                user = cur.fetchone()

                print(user)
                if user is None:
                    msg = "No User Found"
                    return redirect('/')

                else:
                    session['user_id'] = user[0]
                    session['uniqueid'] = user[1]
                    msg = "User Found"
                    return redirect('/dashboard')
                con.close()
        except:
            msg = "Error in Login"
            return redirect('/')
    else:

        return redirect('/')


@app.route("/signup_validation", methods=['GET', 'POST'])
def signup_validation():
    if request.method == 'POST':
        try:
            uemail = request.form['uemail']
            upassword = request.form['upassword']
            uname = request.form['uname']
            with sql.connect("kanban.db") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO signup (uname,uemail,upassword) VALUES (?,?,?)", (uname, uemail, upassword))
                con.commit()
                return redirect('/')
        except:
            con.rollback()
            msg = "Error in Insert Operation"
    
    return redirect('/signup')


@app.route("/delete-list/<string:title>")
def delete_list(title):
    if 'user_id' in session:
        with sql.connect("kanban.db") as con:
            cur = con.cursor() 
            cur.execute( "DELETE from card where uemail=? and list_title=?",(session["uniqueid"],title))
            con.commit()
        with sql.connect("kanban.db") as con:
            cur = con.cursor()     
            cur.execute( "DELETE from list where uemail=? and list_title=?",(session["uniqueid"],title))
            con.commit()
            con.close

    return redirect('/dashboard')
    


@app.route("/delete-card/<string:title>")
def delete_card(title):
    if 'user_id' in session:
        with sql.connect("kanban.db") as con:
            cur = con.cursor() 
            cur.execute( "DELETE from card where uemail=? and card_title=?",(session["uniqueid"],title))
            con.commit()
    return redirect('/dashboard')
    


if __name__ == "__main__":
    app.run(debug=True)
