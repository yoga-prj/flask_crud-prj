from flask import Flask,render_template, request, jsonify, redirect, session
import mysql.connector

app =Flask(__name__)
app.secret_key="super_secret_key_123"

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Yoga@mysql100#",
        database="flask_db"
    )

#Login routes

@app.route("/")
def start_page():
    return redirect("/login")

@app.route("/login",methods=["GET"])

def login_page():
    return render_template("login_page.html")

@app.route("/login", methods =["POST"])

def login():
    staff_no=request.form.get("staff_no")
    password=request.form.get("password")
    conn = get_db_connection()
    cursor=conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM staff_login WHERE staff_no =%s AND password=%s",(staff_no,password))
    user=cursor.fetchone()
    cursor.close()
    conn.close()

    if user:
        session["staff_no"]=staff_no
        return redirect("/students")
    else:
        return "Invalid Staff Number or Password"
    
#CRUD routes

@app.route("/students")

def show_students():
    if "staff_no" not in session:
        return redirect("/login")
    
    page = request.args.get("page",1,type=int)
    limit=10
    offset=(page-1)*limit    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students LIMIT %s OFFSET %s",(limit,offset))
    students = cursor.fetchall()
    cursor.execute("SELECT COUNT(*) AS total FROM students")
    total=cursor.fetchone()["total"]
    cursor.close()
    conn.close()

    has_next=page * limit < total
    has_prev=page > 1
    
    return render_template("home_page.html",students=students,page=page,has_next=has_next,has_prev=has_prev)

@app.route("/add", methods =["GET"])

def add_form():
    return render_template("add_student.html")

@app.route("/add",methods =["POST"])

def add_student():
    name = request.form.get("name")
    age = request.form.get("age") 
    city = request.form.get("city")
    course=request.form.get("course")
    score=request.form.get("score")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    sql =""" INSERT INTO students(name, age, city, course, score)
    VALUES (%s, %s, %s, %s, %s) """

    values=(name, age, city, course, score)
    cursor.execute(sql,values)
    conn.commit()
    cursor.close()
    conn.close()

    return redirect ("/students")

@app.route("/edit/<int:id>",methods =["GET"])

def edit_form(id):
    conn = get_db_connection()
    cursor=conn.cursor(dictionary =True)
    cursor.execute("SELECT * FROM students where id =%s",(id,))
    student=cursor.fetchone()
    conn.close()
    cursor.close()  
    return render_template("edit_page.html",student=student)

@app.route("/edit/<int:id>",methods=["POST"])

def update_student(id):
    name=request.form.get("name")
    age=request.form.get("age")
    city=request.form.get("city")
    course=request.form.get("course")
    score=request.form.get("score")
    conn =get_db_connection()
    cursor=conn.cursor(dictionary=True)
    sql=""" 
    UPDATE students 
    SET name =%s, age=%s, city=%s, course=%s, score=%s
    WHERE id =%s 
    """
    values=(name, age, city, course, score, id)
    cursor.execute(sql,values)
    conn.commit()
    cursor.close()
    conn.close()

    return redirect("/students")

@app.route("/delete/<int:id>")
def delete_student(id):
    conn=get_db_connection()
    cursor=conn.cursor(dictionary=True)
    cursor.execute("DELETE FROM students WHERE id=%s",(id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect('/students')
@app.route("/logout")

def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)

