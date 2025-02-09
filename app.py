
from flask import Flask, request, render_template, redirect, url_for
import mysql.connector



app = Flask(__name__)

# MySQL Database Connection
db = mysql.connector.connect(
    host="localhost",
    user="root",  # Replace with your MySQL username
    password="Slushie3345",  # Replace with your MySQL password
    database="project"   # Replace with your MySQL database name
)
cursor = db.cursor()

@app.route('/')
def home():
    return render_template('home.html')

# Route for the main page where user chooses sign up or login
@app.route("/patient")
def index():
    return render_template("index.html")

@app.route('/doctor')
def doctor():
    return render_template('index2.html')

@app.route('/signupdoctor', methods=['GET', 'POST'])
def signupdoctor():
    if request.method == 'POST':
        doctor_email = request.form.get('doctor_email')
        doctor_password = request.form.get('doctor_password')
        doctor_confirm_password = request.form.get('doctor_confirm_password')

        # Check if passwords match
        if doctor_password != doctor_confirm_password:
            return "Passwords do not match!"

        # Check if the email is already registered
        cursor.execute("SELECT * FROM doctors WHERE doctor_email = %s", (doctor_email,))
        existing_user = cursor.fetchone()

        if existing_user:
            return "Email is already registered."

        # Insert the new doctor data into the 'doctors' table
        cursor.execute("INSERT INTO doctors (doctor_email, doctor_password) VALUES (%s, %s)", (doctor_email, doctor_password))
        db.commit()
        
        cursor.execute("SELECT doctor_id FROM doctors WHERE doctor_email = %s", (doctor_email,))
        doctor_id = cursor.fetchone()[0]  

        return redirect(url_for('doctor_details', doctor_id = doctor_id))

    # Render the sign-up form
    return render_template('signupdoctor.html')

@app.route('/doctor_details/<int:doctor_id>', methods=['GET', 'POST'])
def doctor_details(doctor_id):
    if request.method == 'POST':
        # Get the doctor's details from the form
        name = request.form.get('name')
        speciality = request.form.get('speciality')
        slots_input = request.form.get('slots')  # Get the entered slots as a string
        
        # Split the slots by commas and clean them up
        slots = [slot.strip() for slot in slots_input.split(',')]
        
        # Insert or update doctor's details
        cursor.execute("""
            INSERT INTO doctor_info (doctor_id, name, speciality, available_slots)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE name=%s, speciality=%s, available_slots=%s
        """, (doctor_id, name, speciality, ', '.join(slots), name, speciality, ', '.join(slots)))
        
        db.commit()
        return redirect(url_for('doctor_dashboard', doctor_id=doctor_id))

    return render_template('doctor_details.html', doctor_id=doctor_id)

@app.route('/doctor_dashboard/<int:doctor_id>', methods=['GET', 'POST'])
def doctor_dashboard(doctor_id):
    cursor.execute("SELECT name, speciality, available_slots FROM doctor_info WHERE doctor_id = %s", (doctor_id,))
    doctor_info = cursor.fetchone()
    return render_template('doctor_dashboard.html', doctor_id=doctor_id, doctor_info=doctor_info)

@app.route('/doctor_profile/<int:doctor_id>', methods=['GET', 'POST'])
def doctor_profile(doctor_id):
    # Retrieve doctor's profile information
    cursor.execute("SELECT* FROM doctor_info WHERE doctor_id = %s", (doctor_id,))
    doctor_info = cursor.fetchone()
    
    return render_template('doctor_profile.html', doctor_info=doctor_info)

@app.route("/doctor_edit_profile/<int:doctor_id>", methods=["GET", "POST"])
def doctor_edit_profile(doctor_id):
    # Fetch current doctor information
    cursor.execute("SELECT * FROM doctor_info WHERE doctor_id = %s", (doctor_id,))
    doctor_info = cursor.fetchone()

    if request.method == 'POST':
        # Get form values
        available_slots = request.form.get('available_slots') 

        # Update doctor information
        cursor.execute("""
            UPDATE doctor_info
            SET available_slots = %s
            WHERE doctor_id = %s
        """, (available_slots, doctor_id))

        db.commit()

        return redirect(url_for('doctor_profile', doctor_id=doctor_id))

    return render_template('doctor_edit_profile.html', doctor_info=doctor_info)

@app.route('/doctor_appointments/<int:doctor_id>', methods=['GET', 'POST'])
def doctor_appointments(doctor_id):
    # Join the user_info and appointment_info tables to fetch the required details
    query = """
    SELECT user_info.name, user_info.age, user_info.height, user_info.weight, user_info.gender, 
    appointment_info.slot, appointment_info.date
    FROM appointment_info
    JOIN user_info ON appointment_info.patient_email = user_info.email
    WHERE appointment_info.doctor_id = %s
    ORDER BY appointment_info.date, appointment_info.slot
    """
    
    cursor.execute(query, (doctor_id,))
    appointments = cursor.fetchall()
    
    # Check if there are appointments
    if not appointments:
        return "You have no appointments right now."

    return render_template('doctor_appointments.html', appointments=appointments)


@app.route('/logindoctor', methods=['GET', 'POST'])
def logindoctor():
    if request.method == 'POST':
        doctor_email = request.form.get('doctor_email')
        doctor_password = request.form.get('doctor_password')
        cursor = db.cursor()  # Create a cursor to interact with the database
        cursor.execute("SELECT * FROM doctors WHERE doctor_email = %s", (doctor_email,))
        doctor = cursor.fetchone()  # Fetch the doctor record
        cursor.execute("SELECT doctor_id FROM doctors WHERE doctor_email = %s", (doctor_email,))
        doctor_id = cursor.fetchone()[0]
        
        if doctor:
            
            if doctor[2] == doctor_password: 
                
                return redirect(url_for('doctor_dashboard', doctor_id=doctor_id))
  
            else:
                return "Invalid password!"  # Incorrect password
        else:
            return "Doctor not found!"  # No doctor with this email exists

    return render_template('logindoctor.html')


# Route for the Sign Up page
@app.route("/signup")
def signup():
    return render_template("signup.html")

# Route to handle Sign Up form submission
@app.route("/submit_signup", methods=["POST"])
def submit_signup():
    email = request.form.get("email")
    password = request.form.get("password")
    confirm_password = request.form.get("confirm_password")

    # Check if the password and confirm password match
    if password != confirm_password:
         return"Passwords do not match!"
         
    # Check if the email already exists in the database
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    existing_user = cursor.fetchone()

    if existing_user:
        return "Email is already registered."

    # Insert the new user data into the 'users' table
    cursor.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, password))
    db.commit()

    # Redirect to the additional info form
    return redirect(url_for('additional_info', email=email))

# Route to handle additional user info submission
@app.route("/additional_info/<email>", methods=["GET", "POST"])
def additional_info(email):
    if request.method == "POST":
        name = request.form.get("name")
        phone = request.form.get("phone")
        age = request.form.get("age")
        gender = request.form.get("gender")
        weight = request.form.get("weight")
        height = request.form.get("height")

        # Insert additional information into the 'user_info' table
        cursor.execute(
            "INSERT INTO user_info (email, name, phone, age, gender, weight, height) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (email, name, phone, age, gender, weight, height)
        )
        db.commit()

        return redirect(url_for('user_dashboard', email=email))

    return render_template("additional_info.html", email=email)

# Route for the Login page
@app.route("/login")
def login():
    return render_template("login.html")

# Route to handle Login form submission
@app.route("/submit_login", methods=["POST"])
def submit_login():
    email = request.form.get("email")
    password = request.form.get("password")

    # Check if the user exists and the password is correct
    cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
    user = cursor.fetchone()

    if user:
        return redirect(url_for('user_dashboard', email=email))
    else:
        return "Invalid email or password."

# Route for the user dashboard
@app.route("/dashboard/<email>")
def user_dashboard(email):
    return render_template("dashboard.html", email=email)

# Route for the profile page
@app.route("/profile/<email>")
def profile(email):
    cursor.execute("SELECT * FROM user_info WHERE email = %s", (email,))
    user_info = cursor.fetchone()

    if user_info:
        # Unpack all columns from the user_info table
        id, email, name, phone, age, gender, weight, height = user_info
        return render_template(
            "profile.html",
            email=email,
            name=name,
            phone=phone,
            age=age,
            gender=gender,
            weight=weight,
            height=height
        )
    else:
        return "User info not found."

# Route for the Edit Profile page
@app.route("/edit_profile/<email>")
def edit_profile(email):
    # Fetch current user details to pre-fill the form (optional)
    cursor.execute("SELECT name, phone, age, gender, weight, height FROM user_info WHERE email = %s", (email,))
    user_info = cursor.fetchone()

    if user_info:
        name, phone, age, gender, weight, height = user_info
    else:
        name = phone = age = gender = weight = height = ""

    return render_template("edit_profile.html", email=email, name=name, phone=phone, age=age, gender=gender, weight=weight, height=height)

# Route to handle Edit Profile form submission
@app.route("/submit_edit_profile/<email>", methods=["POST"])
def submit_edit_profile(email):
    # Fetch new values from the form
    new_name = request.form.get("name")
    new_phone = request.form.get("phone")
    new_age = request.form.get("age")
    new_gender = request.form.get("gender")
    new_weight = request.form.get("weight")
    new_height = request.form.get("height")

    # Get current values from the database
    cursor.execute("SELECT name, phone, age, gender, weight, height FROM user_info WHERE email = %s", (email,))
    current_info = cursor.fetchone()

    if current_info:
        current_name, current_phone, current_age, current_gender, current_weight, current_height = current_info

        # Update values only if new input is provided, otherwise retain old values
        name = new_name if new_name else current_name
        phone = new_phone if new_phone else current_phone
        age = new_age if new_age else current_age
        gender = new_gender if new_gender else current_gender
        weight = new_weight if new_weight else current_weight
        height = new_height if new_height else current_height

        # Update the user information in the database
        cursor.execute(""" 
            UPDATE user_info 
            SET name = %s, phone = %s, age = %s, gender = %s, weight = %s, height = %s 
            WHERE email = %s 
        """, (name, phone, age, gender, weight, height, email))
        db.commit()

        return redirect(url_for('profile', email=email))

    return "Error: User not found."

# Route to show all user appointments
@app.route("/show_appointments/<email>")
def show_appointments(email):
    cursor.execute(
        "SELECT a.doctor_id, d.name, d.speciality, a.date, a.slot "
        "FROM appointment_info a "
        "JOIN doctor_info d ON a.doctor_id = d.doctor_id "
        "WHERE a.patient_email = %s", (email,)
    )
    appointments = cursor.fetchall()

    if not appointments:
        return "No appointments found. Please book an appointment first."

    return render_template("show_appointments.html", appointments=appointments)

@app.route("/cancel_appointment/<doctor_id>/<appointment_date>/<appointment_slot>", methods=["GET", "POST"])
def cancel_appointment(doctor_id, appointment_date, appointment_slot):
    # Query to find the appointment for the given doctor ID, date, and slot
    cursor.execute(
        "SELECT * FROM appointment_info WHERE doctor_id = %s AND date = %s AND slot = %s",
        (doctor_id, appointment_date, appointment_slot)
    )
    appointment = cursor.fetchone()

    if appointment:
        # If the appointment exists, delete it
        cursor.execute(
            "DELETE FROM appointment_info WHERE doctor_id = %s AND date = %s AND slot = %s",
            (doctor_id, appointment_date, appointment_slot)
        )
        db.commit()
        # Pass the success message to the template
        return redirect(url_for('appointment_cancelled'))
    
@app.route("/appointment_cancelled")
def appointment_cancelled():
    
    return render_template("appointment_cancelled.html")
    
# Route for the search doctor page
@app.route("/search_doctor", methods=["GET", "POST"])
def search_doctor():
    email = request.args.get("email")  # Fetch email from query parameters or session
    if request.method == "POST":
        speciality = request.form.get("speciality")
        cursor.execute("SELECT doctor_id, name, speciality, available_slots FROM doctor_info WHERE speciality = %s", (speciality,))
        doctors = cursor.fetchall()
        return render_template("search_result.html", doctors=doctors, email=email)
    return render_template("search_doctor.html")

# Route to show search results
@app.route("/search_result", methods=["GET", "POST"])
def search_result():
    return render_template("search_result.html")

# Route for booking an appointment
@app.route("/book_appointment/<email>/<doctor_id>", methods=["GET", "POST"])
def book_appointment(email, doctor_id):
    # Fetch doctor's available slots
    cursor.execute("SELECT available_slots FROM doctor_info WHERE doctor_id = %s", (doctor_id,))
    available_slots = cursor.fetchone()

    if available_slots:
        available_slots = available_slots[0].split(",")  # Assuming slots are stored as a comma-separated string

    if request.method == "POST":
        date = request.form.get("date")
        slot = request.form.get("slot")

        # Check if the selected slot is in the available slots
        if slot not in available_slots:
            return "Error: The selected slot is not available for booking."

        # Check if the slot is already booked
        cursor.execute(
            "SELECT * FROM appointment_info WHERE doctor_id = %s AND date = %s AND slot = %s",
            (doctor_id, date, slot)
        )
        existing_appointment = cursor.fetchone()

        if existing_appointment:
            return "Error: The selected slot is already booked."

        # Insert the new appointment
        cursor.execute(
            "INSERT INTO appointment_info (doctor_id, patient_email, date, slot) VALUES (%s, %s, %s, %s)",
            (doctor_id, email, date, slot)
        )
        db.commit()
        return redirect(url_for('show_appointments', email=email))

    cursor.execute("SELECT doctor_id, name FROM doctor_info WHERE doctor_id = %s", (doctor_id,))
    doctor = cursor.fetchone()
    return render_template("book_appointment.html", email=email, doctor=doctor, available_slots=available_slots)

if __name__ == "__main__":
    app.run(debug=True)
