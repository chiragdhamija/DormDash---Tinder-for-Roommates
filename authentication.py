from flask import Flask, render_template, request, redirect, url_for,session,jsonify
import sqlite3

from flask_cors import CORS


app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
cors = CORS(app)

@app.route('/', methods=['POST','GET'])
def main():
    return render_template('main.html')
@app.route('/loginpage', methods=['POST','GET'])
def loginpage():
    return render_template('loginpage.html')

@app.route('/signup',methods=['POST','GET'])
def signup():
    return render_template('signup.html')


@app.route('/authenticate', methods=['POST'])
def login():
    userId = request.form['username']
    password = request.form['password']
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    query = "SELECT * FROM user WHERE userid=? AND pass=?"
    cursor.execute(query, (userId, password))
    
    result = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if result is not None:
        session['userId'] = userId
        return redirect('/home')
    else:
        return redirect('/loginpage?message=Invalid%20username%20or%20password')
    
@app.route('/home')
def home():
    userId = session.get('userId')
    name = None  # Assign a default value to the name variable
    
    if userId:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        query = "SELECT name FROM user WHERE userid=?"
        cursor.execute(query, (userId,))
        
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if result is not None:
            name = result[0]
            
    if name is not None:
        return render_template('home.html', namePlace=name)
    else:
        return redirect('/')

@app.route('/newuser', methods=['POST'])
def insert():
    userId = request.form['username']
    
    password = request.form['password']
    name = request.form['name']
    branch = request.form['branch']
    hobbies = request.form['hobbies']
    languages = request.form['languages']
    contact = request.form['contact']
    sleep = request.form['sleep']
    description = request.form['description']
    age = request.form['age']
    
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    query = "insert into user values (?,?,?,?,?,?,?,?,?,?,'','','')"
    cursor.execute(query, (userId, name,age,branch,languages,hobbies,sleep,description,contact,password))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    session['userId'] = userId
    return redirect('/home')
    
@app.route('/matches')
def get_matches():
    userId = session.get('userId')
    if not userId:
        return redirect('/')
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # get the user's liked list and convert to a list
    c.execute("SELECT like FROM user WHERE userid=?", (userId,))
    result = c.fetchone()
    if result is not None:
        like_string = result[0]
        if like_string:
            
            liked_list = like_string.split(',')
        else:
            liked_list=[]
    else:
        liked_list=[]
    
    # iterate through each person the user has liked
    matches = []
    for liked_person in liked_list:
        c.execute("SELECT like FROM user WHERE userid=?", (liked_person,))
        result = c.fetchone()
        if result is not None:
            like_string = result[0]
            if like_string:
                
                liked_list = like_string.split(',')
            else:
                liked_list=[]
        else:
            liked_list=[]
        
        
        if userId in liked_list:
            matches.append(liked_person)
    match_string = ','.join(matches)
    
    
    c.execute("update user set matches=? where userid = ?",(match_string,userId))
    conn.commit()  
   

    

    users_data=[]
    for user_id in matches:
        c.execute('SELECT * FROM user WHERE userid = ?', (user_id,))
        user_data = c.fetchone()
        user_dict = {
            'id':user_data[0],
            'name': user_data[1],
            'study':user_data[3],
            'languages': user_data[4],
            'age':user_data[2],
            'contact':user_data[8]
        }
        users_data.append(user_dict)
    conn.close()
    return render_template('matches.html', users=users_data)
@app.route('/browse')
def showroommates():
    userId = session.get('userId')
    if not userId:
        return redirect('/')
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT like FROM user WHERE userid=?", (userId,))
    like_string = c.fetchone()[0]
    liked_list=[]
    disliked_list=[]
    if like_string:
        liked_list = like_string.split(',')
    
        
    c.execute("SELECT dislike FROM user WHERE userid=?", (userId,))
    dislike_string = c.fetchone()[0]
    if dislike_string:
        disliked_list = dislike_string.split(',')

    # get the user's liked list and convert to a list
    c.execute("SELECT userid FROM user")
    results = c.fetchall()
    userIDs = [result[0] for result in results]
    final=[i for i in userIDs if i not in liked_list and i not in disliked_list and i!=userId]
    users_data=[]
    for user_id in final:
        c.execute('SELECT * FROM user WHERE userid = ?', (user_id,))
        user_data = c.fetchone()
        user_dict = {
            'id':user_data[0],
            'name': user_data[1],
            'study':user_data[3],
            'languages': user_data[4],
            'age':user_data[2],
            'hobbies':user_data[5],
            'sleep':user_data[6],
            'biodata':user_data[7]

        }
        users_data.append(user_dict)
    conn.close()
    return render_template('browse.html', users=users_data)


@app.route('/user/<userid>')
def display_user(userid):
    # Connect to the database
    conn = sqlite3.connect('database.db')

    c = conn.cursor()

    # Retrieve user information from the user_info table based on the provided user ID
    c.execute('SELECT * FROM user WHERE userid = ?', (userid,))
    user = c.fetchone()

    # Close the database connection
    c.close()

    # Render the user information in an HTML template
    return render_template('user.html', user=user, name=user[1], age=user[2], branch=user[3], language=user[4], hobbies=user[5], sleep=user[6], about=user[7], contact=user[8])

@app.route('/view', methods=['POST','GET'])
def display_view():

    userId = session.get('userId')
    if not userId:
        return redirect('/')
    conn = sqlite3.connect('database.db')

    c = conn.cursor()
    usees=session.get('userId')
    c.execute('SELECT * FROM user WHERE userid = ?', (usees,))
    user=c.fetchone()
    print(user)
    c.close()
    return render_template('view.html', user=user, name=user[1], age=user[2], branch=user[3], language=user[4], hobbies=user[5], sleep=user[6], about=user[7], contact=user[8])


@app.route('/submit-thumbs-up', methods=['POST'])
def update_thumbsup():
    userId = session.get('userId')
    liked_id = request.form.get('id')
    conn = sqlite3.connect('database.db')

    c = conn.cursor()
    c.execute("SELECT like FROM user WHERE userid=?", (userId,))
    like_string = c.fetchone()[0]
    liked_list=[]    
    if like_string:
        liked_list = like_string.split(',')
    liked_list.append(liked_id)

    like_string = ','.join(liked_list)
    
    c.execute("update user set like=? where userid = ?",(like_string,userId))
    conn.commit()

    # Close the database connection
    c.close()
    # Do something with div_id
    return 'Success'

@app.route('/submit-thumbs-down', methods=['POST'])
def update_thumbsdown():
    userId = session.get('userId')
    disliked_id = request.form.get('id')
    conn = sqlite3.connect('database.db')

    c = conn.cursor()
    c.execute("SELECT dislike FROM user WHERE userid=?", (userId,))
    dislike_string = c.fetchone()[0]
    disliked_list=[]    
    if dislike_string:
        disliked_list = dislike_string.split(',')
    disliked_list.append(disliked_id)

    dislike_string = ','.join(disliked_list)
    
    c.execute("update user set dislike=? where userid = ?",(dislike_string,userId))
    conn.commit()

    # Close the database connection
    c.close()
    # Do something with div_id
    return 'Success'
@app.route('/updateprofile', methods=['POST'])
def update():
    userId=session.get('userId')
        
    password = request.form['password']
    name = request.form['name']
    branch = request.form['branch']
    hobbies = request.form['hobbies']
    languages = request.form['languages']
    contact = request.form['contact']
    sleep = request.form['sleep']
    description = request.form['description']
    age = request.form['age']
    
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    query = "update user set name=?,age=?,branch=?,language=?,hobbies=?,sleep=?,about=?,contact=?,pass=? where userid =?"
    cursor.execute(query, ( name,age,branch,languages,hobbies,sleep,description,contact,password,userId))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    
    return redirect('/view')

@app.route('/edit',methods=['POST','GET'])
def edit():
    return render_template('edit.html')
@app.route('/about', methods=['POST','GET'])
def about():
    return render_template('about.html')
@app.route('/logout', methods=['POST','GET'])
def logout():
    session.pop('userId', None)
    return redirect('/')
if __name__ == '__main__':
    app.run(debug=True)   

