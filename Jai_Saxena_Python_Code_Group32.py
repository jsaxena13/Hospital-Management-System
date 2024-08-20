from flask import Flask, request, render_template, redirect, flash, session
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = '123'  # Needed to use sessions and flash messages

# Database Connection
def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Root@root',
            database='HospitalManagement',
            port=3306
        )
        return connection
    except Error as e:
        print(f"The error '{e}' occurred")
        return None

def close_connection(connection):
    if connection:
        connection.close()

# Utility for simplifying update operations
def construct_update_sql(table, args, primary_key, id_value):
    columns = [f"{k} = %s" for k, v in args.items() if v is not None]
    sql = f"UPDATE {table} SET {', '.join(columns)} WHERE {primary_key} = %s;"
    values = tuple(v for v in args.values() if v is not None) + (id_value,)
    return sql, values

# Routes for managing patients
@app.route('/patients', methods=['GET', 'POST'])
def manage_patients():
    if request.method == 'POST':
        args = request.form
        sql = "INSERT INTO Patients (Name, DOB, Address, Phone, InsuranceInfo) VALUES (%s, %s, %s, %s, %s)"
        conn = create_connection()
        if conn is None:
            return "Database connection failed", 500
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (args['Name'], args['DOB'], args['Address'], args['Phone'], args['InsuranceInfo']))
            conn.commit()
            new_patient_id = cursor.lastrowid  # Retrieve the ID of the newly inserted patient
            return redirect(f'/patients/edit/{new_patient_id}')  # Redirect to the edit page of the new patient
        finally:
            close_connection(conn)
    else:
        conn = create_connection()
        if conn is None:
            return "Database connection failed", 500
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Patients")
            rows = cursor.fetchall()
            return render_template('patients.html', patients=rows)
        finally:
            close_connection(conn)


# Routes for editing patients
@app.route('/patients/edit/<int:id>', methods=['GET', 'POST'])
def edit_patient(id):
    if request.method == 'POST':
        args = request.form
        sql = "UPDATE Patients SET Name = %s, DOB = %s, Address = %s, Phone = %s, InsuranceInfo = %s WHERE PatientID = %s"
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (args['Name'], args['DOB'], args['Address'], args['Phone'], args['InsuranceInfo'], id))
        conn.commit()
        close_connection(conn)
        return redirect('/patients')
    else:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Patients WHERE PatientID = %s", (id,))
        patient = cursor.fetchone()
        close_connection(conn)
        return render_template('edit_patient.html', patient=patient)

# Routes for deleting patients
@app.route('/patients/delete/<int:id>', methods=['GET'])
def delete_patient(id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Patients WHERE PatientID = %s", (id,))
    conn.commit()
    close_connection(conn)
    return redirect('/patients')

# Routes for managing doctors

@app.route('/doctors', methods=['GET', 'POST'])
def manage_doctors():
    if request.method == 'POST':
        args = request.form
        sql = "INSERT INTO Doctors (Name, Specialization, Schedule) VALUES (%s, %s, %s)"
        conn = create_connection()
        if conn is None:
            return "Database connection failed", 500
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (args['Name'], args['Specialization'], args['Schedule']))
            conn.commit()
            return redirect('/doctors')
        except Error as e:
            print(f"SQL Error: {e}")
            return "Error in database operation", 500
        finally:
            close_connection(conn)
    else:
        conn = create_connection()
        if conn is None:
            return "Database connection failed", 500
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Doctors")
            rows = cursor.fetchall()
            return render_template('doctors.html', doctors=rows)
        finally:
            close_connection(conn)

@app.route('/doctors/edit/<int:id>', methods=['GET', 'POST'])
def edit_doctor(id):
    if request.method == 'POST':
        args = request.form
        sql = "UPDATE Doctors SET Name = %s, Specialization = %s, Schedule = %s WHERE DoctorID = %s"
        conn = create_connection()
        if conn is None:
            return "Database connection failed", 500
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (args['Name'], args['Specialization'], args['Schedule'], id))
            conn.commit()
            return redirect('/doctors')
        except Error as e:
            print(f"SQL Error: {e}")
            return "Error in database operation", 500
        finally:
            close_connection(conn)
    else:
        conn = create_connection()
        if conn is None:
            return "Database connection failed", 500
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Doctors WHERE DoctorID = %s", (id,))
            doctor = cursor.fetchone()
            if doctor is None:
                return "No doctor found with that ID", 404
            return render_template('edit_doctor.html', doctor=doctor)
        finally:
            close_connection(conn)

@app.route('/doctors/delete/<int:id>', methods=['GET'])
def delete_doctor(id):
    conn = create_connection()
    if conn is None:
        return "Database connection failed", 500
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Doctors WHERE DoctorID = %s", (id,))
        conn.commit()
        return redirect('/doctors')
    except Error as e:
        print(f"SQL Error: {e}")
        return "Error in database operation", 500
    finally:
        close_connection(conn)

# Routes for managing appointments
@app.route('/appointments', methods=['GET', 'POST'])
def manage_appointments():
    if request.method == 'POST':
        args = request.form
        patient_id = args['PatientID']
        doctor_id = args['DoctorID']
        conn = create_connection()
        if conn is None:
            return "Database connection failed", 500
        cursor = conn.cursor()
        # Validate PatientID and DoctorID
        cursor.execute("SELECT 1 FROM Patients WHERE PatientID = %s", (patient_id,))
        if cursor.fetchone() is None:
            return "Invalid Patient ID", 400
        cursor.execute("SELECT 1 FROM Doctors WHERE DoctorID = %s", (doctor_id,))
        if cursor.fetchone() is None:
            return "Invalid Doctor ID", 400
        sql = "INSERT INTO Appointments (PatientID, DoctorID, Date, Time, Purpose) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, (patient_id, doctor_id, args['Date'], args['Time'], args['Purpose']))
        conn.commit()
        close_connection(conn)
        return redirect('/appointments')
    else:
        conn = create_connection()
        if conn is None:
            return "Database connection failed", 500
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Appointments")
        rows = cursor.fetchall()
        close_connection(conn)
        return render_template('appointments.html', appointments=rows)


# Routes for editing appointments
@app.route('/appointments/edit/<int:id>', methods=['GET', 'POST'])
def edit_appointment(id):
    if request.method == 'POST':
        args = request.form
        sql = "UPDATE Appointments SET PatientID = %s, DoctorID = %s, Date = %s, Time = %s, Purpose = %s WHERE AppointmentID = %s"
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (args['PatientID'], args['DoctorID'], args['Date'], args['Time'], args['Purpose'], id))
        conn.commit()
        close_connection(conn)
        return redirect('/appointments')
    else:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Appointments WHERE AppointmentID = %s", (id,))
        appointment = cursor.fetchone()
        close_connection(conn)
        return render_template('edit_appointment.html', appointment=appointment)

# Routes for deleting appointments
@app.route('/appointments/delete/<int:id>', methods=['GET'])
def delete_appointment(id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Appointments WHERE AppointmentID = %s", (id,))
    conn.commit()
    close_connection(conn)
    return redirect('/appointments')

# Routes for managing medical records
@app.route('/medicalrecords', methods=['GET', 'POST'])
def manage_medical_records():
    if request.method == 'POST':
        args = request.form
        patient_id = args['PatientID']
        conn = create_connection()
        if conn is None:
            return "Database connection failed", 500
        cursor = conn.cursor()
        # Validate PatientID
        cursor.execute("SELECT 1 FROM Patients WHERE PatientID = %s", (patient_id,))
        if cursor.fetchone() is None:
            close_connection(conn)
            return "Invalid Patient ID", 400
        sql = "INSERT INTO MedicalRecords (PatientID, VisitDate, Diagnosis, Treatment) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (patient_id, args['VisitDate'], args['Diagnosis'], args['Treatment']))
        conn.commit()
        close_connection(conn)
        return redirect('/medicalrecords')
    else:
        conn = create_connection()
        if conn is None:
            return "Database connection failed", 500
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM MedicalRecords")
        rows = cursor.fetchall()
        close_connection(conn)
        return render_template('medical_records.html', medicalrecords=rows)


# Routes for editing medical records
@app.route('/medicalrecords/edit/<int:id>', methods=['GET', 'POST'])
def edit_medical_record(id):
    if request.method == 'POST':
        args = request.form
        sql = "UPDATE MedicalRecords SET PatientID = %s, VisitDate = %s, Diagnosis = %s, Treatment = %s WHERE RecordID = %s"
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (args['PatientID'], args['VisitDate'], args['Diagnosis'], args['Treatment'], id))
        conn.commit()
        close_connection(conn)
        return redirect('/medicalrecords')
    else:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM MedicalRecords WHERE RecordID = %s", (id,))
        record = cursor.fetchone()
        close_connection(conn)
        return render_template('edit_medical_record.html', record=record)

# Routes for deleting medical records
@app.route('/medicalrecords/delete/<int:id>', methods=['GET'])
def delete_medical_record(id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM MedicalRecords WHERE RecordID = %s", (id,))
    conn.commit()
    close_connection(conn)
    return redirect('/medicalrecords')

# Routes for managing bills
@app.route('/bills', methods=['GET', 'POST'])
def manage_bills():
    if request.method == 'POST':
        args = request.form
        patient_id = args['PatientID']
        conn = create_connection()
        if conn is None:
            flash("Database connection failed", "error")
            return redirect('/bills')

        try:
            cursor = conn.cursor()
            # Validate PatientID
            cursor.execute("SELECT 1 FROM Patients WHERE PatientID = %s", (patient_id,))
            if cursor.fetchone() is None:
                flash("Invalid Patient ID", "error")
                close_connection(conn)
                return redirect('/bills')

            sql = "INSERT INTO Bills (PatientID, Date, Amount, Status) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (patient_id, args['Date'], args['Amount'], args['Status']))
            conn.commit()
            flash("Bill added successfully", "success")
        except Error as e:
            flash(f"An error occurred: {e}", "error")
        finally:
            close_connection(conn)
        return redirect('/bills')
    else:
        conn = create_connection()
        if conn is None:
            flash("Database connection failed", "error")
            return render_template('bills.html', bills=[])

        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Bills")
            rows = cursor.fetchall()
            return render_template('bills.html', bills=rows)
        finally:
            close_connection(conn)

# Routes for editing bills
@app.route('/bills/edit/<int:id>', methods=['GET', 'POST'])
def edit_bill(id):
    if request.method == 'POST':
        args = request.form
        sql = "UPDATE Bills SET PatientID = %s, Date = %s, Amount = %s, Status = %s WHERE BillID = %s"
        conn = create_connection()
        if conn is None:
            flash("Database connection failed", "error")
            return redirect('/bills')

        try:
            cursor = conn.cursor()
            cursor.execute(sql, (args['PatientID'], args['Date'], args['Amount'], args['Status'], id))
            conn.commit()
            flash("Bill updated successfully", "success")
        except Error as e:
            flash(f"An error occurred: {e}", "error")
        finally:
            close_connection(conn)
        return redirect('/bills')
    else:
        conn = create_connection()
        if conn is None:
            flash("Database connection failed", "error")
            return redirect('/bills')

        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Bills WHERE BillID = %s", (id,))
            bill = cursor.fetchone()
            if bill is None:
                flash("No bill found with that ID", "error")
                return redirect('/bills')
            return render_template('edit_bill.html', bill=bill)
        finally:
            close_connection(conn)

# Routes for deleting bills
@app.route('/bills/delete/<int:id>', methods=['GET'])
def delete_bill(id):
    conn = create_connection()
    if conn is None:
        flash("Database connection failed", "error")
        return redirect('/bills')

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Bills WHERE BillID = %s", (id,))
        conn.commit()
        flash("Bill deleted successfully", "success")
    except Error as e:
        flash(f"An error occurred: {e}", "error")
    finally:
        close_connection(conn)
    return redirect('/bills')


# Routes for managing staff
@app.route('/staff', methods=['GET', 'POST'])
def manage_staff():
    if request.method == 'POST':
        args = request.form
        sql = "INSERT INTO Staff (Name, Role, Department) VALUES (%s, %s, %s)"
        conn = create_connection()
        if not conn:
            flash("Database connection failed", "error")
            return redirect('/staff')  # Ensure a redirect if connection fails

        try:
            cursor = conn.cursor()
            cursor.execute(sql, (args['Name'], args['Role'], args['Department']))
            conn.commit()
            flash("Staff member added successfully", "success")
        except Error as e:
            flash(f"An error occurred: {e}", "error")
        finally:
            close_connection(conn)
        return redirect('/staff')
    else:
        conn = create_connection()
        if not conn:
            flash("Database connection failed", "error")
            return redirect('/')  # Redirect or show an error page

        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Staff")
            staff_members = cursor.fetchall()
            return render_template('staff.html', staff=staff_members)
        except Error as e:
            flash(f"An error occurred while retrieving data: {e}", "error")
            return redirect('/')  # Redirect or show an error page
        finally:
            close_connection(conn)


# Routes for editing staff
@app.route('/staff/edit/<int:id>', methods=['GET', 'POST'])
def edit_staff(id):
    if request.method == 'POST':
        args = request.form
        sql = "UPDATE Staff SET Name = %s, Role = %s, Department = %s WHERE StaffID = %s"
        conn = create_connection()
        if not conn:
            flash("Database connection failed", "error")
            return redirect('/staff')  # Redirect to staff list if connection fails

        try:
            cursor = conn.cursor()
            cursor.execute(sql, (args['Name'], args['Role'], args['Department'], id))
            conn.commit()
            flash("Staff updated successfully", "success")
        except Error as e:
            flash(f"An error occurred: {e}", "error")
        finally:
            close_connection(conn)
        return redirect('/staff')  # Always redirect after POST
    else:
        conn = create_connection()
        if not conn:
            flash("Database connection failed", "error")
            return redirect('/staff')  # Redirect if connection fails

        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Staff WHERE StaffID = %s", (id,))
            staff = cursor.fetchone()
            if not staff:
                flash("No staff found with that ID", "error")
                return redirect('/staff')  # Redirect if no staff is found
            return render_template('edit_staff.html', staff=staff)  # Render template if staff is found
        except Error as e:
            flash(f"An error occurred while retrieving staff data: {e}", "error")
            return redirect('/staff')  # Redirect on error
        finally:
            close_connection(conn)



# Routes for deleting staff
@app.route('/staff/delete/<int:id>', methods=['GET'])
def delete_staff(id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Staff WHERE StaffID = %s", (id,))
    conn.commit()
    close_connection(conn)
    return redirect('/staff')


# Routes for managing inventory
@app.route('/inventory', methods=['GET', 'POST'])
def manage_inventory():
    if request.method == 'POST':
        # Handle form submission for creating or updating inventory items
        pass
    else:
        conn = create_connection()
        if not conn:
            flash("Database connection failed", "error")
            return redirect('/')  # Redirect or show an error page if connection fails

        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Inventory")
            inventory_items = cursor.fetchall()
            return render_template('inventory.html', inventory=inventory_items)
        except Error as e:
            flash(f"An error occurred while retrieving inventory data: {e}", "error")
            return redirect('/')  # Redirect or show an error page on error
        finally:
            close_connection(conn)


# Routes for editing inventory
@app.route('/inventory/edit/<int:id>', methods=['GET', 'POST'])
def edit_inventory_item(id):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Inventory WHERE ItemID = %s", (id,))
    item = cursor.fetchone()
    close_connection(conn)

    if not item:
        flash("Inventory item not found", "error")
        return redirect('/inventory')

    if request.method == 'POST':
        args = request.form
        sql = "UPDATE Inventory SET Name = %s, Quantity = %s, ReorderLevel = %s WHERE ItemID = %s"
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (args['Name'], args['Quantity'], args['ReorderLevel'], id))
        conn.commit()
        close_connection(conn)
        return redirect('/inventory')
    else:
        return render_template('edit_inventory.html', item=item)


# Routes for deleting inventory
@app.route('/inventory/delete/<int:id>', methods=['GET'])
def delete_inventory(id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Inventory WHERE ItemID = %s", (id,))
    conn.commit()
    close_connection(conn)
    return redirect('/inventory')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
