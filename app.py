from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy




app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///project.db"
db = SQLAlchemy(app)
uname = 21




class db_attr(db.Model):
    sno = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable = False)
    age = db.Column(db.Integer, nullable = False)
    desc = db.Column(db.String(200), nullable = False)
    uniqueid = db.Column(db.Integer, nullable = False)
    def __str__(self):
        return 'db_attr {}'.format(db_attr.sno)
    



class check_log(db.Model):
    uniqueid = db.Column(db.Integer, primary_key = True)
    loggedin = db.Column(db.Boolean)
    username = db.Column(db.String(100), nullable = False)
    password = db.Column(db.String(100), nullable = False)




with app.app_context():
    db.create_all()
    arr = check_log.query.all()
    l = len(arr)
    if l>0:
        uname = arr[l-1].uniqueid+50



#homepage
@app.route('/')
def login():
    return render_template('login.html')



#login-verification
@app.route('/verify', methods = ['POST', 'GET'])
def verify():
    
    if request.method=='POST':
        print('inside verify2')
        username = request.form['username']
        password = request.form['password']
    else:
        return render_template('signup.html')
    test = check_log.query.filter_by(username = username, password = password).first()
    if test==None:
        return render_template('signup.html')
    test.loggedin = True
    db.session.add(test)
    db.session.commit()
    return redirect('/dashboard/{}'.format(test.uniqueid))
    



#sign-up new user
@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    global uname
    uname = uname+1
    
    if request.method=='POST':
        if request.form['con_password']!=request.form['password']:
            return render_template('signup.html')
        if check_log.query.filter_by(username = request.form['username'], password = request.form['password']).first() !=None:
            return redirect('/')
        if request.form['username']=='admin' and request.form['password']=='1234':
            new_user = db_attr(name = "", age = 0, desc = "", uniqueid = 1)
            status = check_log(username = request.form['username'],password = request.form['password'], uniqueid = new_user.uniqueid, loggedin = False)
        else:
            new_user = db_attr(name = "", age = 0, desc = "", uniqueid = uname)
            status = check_log(username = request.form['username'],password = request.form['password'], uniqueid = new_user.uniqueid, loggedin = False)
        uname+=1
        db.session.add(new_user)
        db.session.commit()
        db.session.add(status)
        db.session.commit()
    return redirect('/')




#taking input from the homepage form
@app.route('/dashboard/<int:uniqueid>', methods = ['GET', 'POST'])
def hello_world(uniqueid):
    check = check_log.query.filter_by(uniqueid=uniqueid).first()
    if check==None:
        return redirect('/')
    if check.loggedin==False:
        return redirect('/')
    username = ''
    if request.method=='POST':
        if(request.form['name']=="" or request.form['age']=="" or request.form['role']==""):
            test = db_attr.query.filter_by(uniqueid=uniqueid).all()
            return render_template('index.html', dbase = test, uniqueid = uniqueid)
        namee = request.form['name']
        agee = request.form['age']
        role = request.form['role']
        test = check_log.query.filter_by(uniqueid = uniqueid).first()
        username = test.username
        dbase = db_attr(name = namee, age = agee, desc = role, uniqueid = uniqueid)
        db.session.add(dbase)
        db.session.commit()
    if uniqueid==1:
        test = db_attr.query.all()
    else:
        test = db_attr.query.filter_by(uniqueid=uniqueid).all()
    if test is None:
        return render_template('index.html', dbase = None, uniqueid = uniqueid, username = username)
    test1 = check_log.query.filter_by(uniqueid = uniqueid).first()
    username = test1.username
    return render_template('index.html', dbase = test, uniqueid = uniqueid, username = username)




#update entry once the update button is clicked
@app.route('/update/<int:sno>', methods = ['GET', 'POST'])
def update(sno):
    if request.method=='POST':
        newE = db_attr.query.filter_by(sno=sno).first()
        uniqueid = newE.uniqueid
        newE.name = request.form['name']
        newE.desc = request.form['role']
        newE.age = request.form['age']
        db.session.add(newE)
        db.session.commit()
    return redirect('/dashboard/{}'.format(uniqueid))



#delete entry once the delete button is clicked
@app.route('/delete/<int:sno>/<int:uniqueid>')
def delete(sno, uniqueid, check = True):
    if check:
        tbDel = db_attr.query.filter_by(sno=sno).first()
        #uniqueid = tbDel.uniqueid
        db.session.delete(tbDel)
        db.session.commit()     
        if uniqueid==1:
            return redirect('/dashboard/{}'.format(1))  
        return redirect('/dashboard/{}'.format(uniqueid))
    


#logout from the current user/admin page
@app.route('/logout/<int:uniqueid>')
def logout(uniqueid):
    check = check_log.query.filter_by(uniqueid=uniqueid).first()
    check.loggedin = False
    db.session.add(check)
    db.session.commit()
    return redirect(url_for('login'))




#delete all entries at once
@app.route('/delete_all')
def deleteAll():
    #test = db_attr.query.all()
    db_attr.query.delete()
    db.session.commit()
    check_log.query.delete()
    db.session.commit()
    return redirect('/')




#search entry by name
@app.route('/search/<int:uniqueid>', methods = ['GET', 'POST'])
def search(uniqueid):
    t = ''
    if request.method=='POST':
        print(request.form['searched'])
        t = request.form['searched']
    if uniqueid==1:
        dbase = db_attr.query.filter_by(name=t).all()
    else:
        dbase = db_attr.query.filter_by(name=t, uniqueid = uniqueid).all()
    return render_template('search.html', dbase=dbase, uniqueid=uniqueid)




#delete last entered element for the given user (last entered row in database in case of admin)
@app.route('/delete_first/<int:uniqueid>')
def delete_first(uniqueid):
    if uniqueid==1:
        data = db_attr.query.all() 
        l = len(data)
        if l==0:
            return redirect('/dashboard/{}'.format(uniqueid))
        for i in reversed(range(0, l)):
            sno = data[i].sno
            tbDel = db_attr.query.filter_by(sno=sno).first()
            if tbDel.age >0:
                break
        #tbDel = db_attr.query.filter_by(sno=sno).first()
        if tbDel.age>0:
            uniqueid = tbDel.uniqueid
            db.session.delete(tbDel)
            db.session.commit() 

        return redirect('/dashboard/{}'.format(1))   
    else:
        data = db_attr.query.filter_by(uniqueid=uniqueid).all() 
    if len(data)==0:
        return redirect('/dashboard/{}'.format(uniqueid))
    l = len(data)
    sno = data[l-1].sno
    print('was here outside')
    return redirect('/delete/{}/{}'.format(sno, uniqueid))



#update the selected entry
@app.route('/updateNow/<int:sno>')
def updateNow(sno):
    data = db_attr.query.get(sno)
    uniqueid = data.uniqueid
    return render_template('update.html', test = db_attr.query.filter_by(sno=sno).first(), uniqueid=uniqueid)



#about page
@app.route('/about/')
def about():
    return 'This is a test project made using Flask'




if __name__=="__main__":
    app.run(debug=True)
