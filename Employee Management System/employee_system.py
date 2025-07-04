import os
from datetime import datetime
from tabulate import tabulate  
from db_config import connect_db

def add_employee():
    db = connect_db()
    cursor = db.cursor()
    
    # Show available departments
    cursor.execute("SELECT * FROM departments")
    departments = cursor.fetchall()
    if not departments:
        print("❌ No departments found. Please add one first.")
        db.close()
        return

    print("Available Departments:")
    for dept in departments:
        print(f"{dept[0]} - {dept[1]}")

    name = input("Enter Name: ")
    gender = input("Enter Gender (Male/Female): ")
    position = input("Enter Position: ")
    dept_id = int(input("Enter Department ID from above list: "))
    salary = float(input("Enter Salary per Day: "))
    cursor.execute("INSERT INTO employees (name, gender, position, dept_id, salary_per_day) VALUES (%s, %s, %s, %s, %s)",
                   (name, gender, position, dept_id, salary))
    db.commit()
    print("✅ Employee added successfully!\n")
    db.close()

def view_employees():
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT e.emp_id AS 'ID', e.name AS 'Name', e.position AS 'Position', 
               d.dept_name AS 'Department', e.salary_per_day AS 'Salary/Day'
        FROM employees e
        JOIN departments d ON e.dept_id = d.dept_id
    """)
    result = cursor.fetchall()
    headers = [i[0] for i in cursor.description]  
    if result:
        print("\n" + tabulate(result, headers=headers, tablefmt="grid"))
    else:
        print("No employees found.")
    db.close()

def mark_attendance():
    db = connect_db()
    cursor = db.cursor()
    emp_id = int(input("Enter Employee ID: "))
    today = datetime.today().strftime('%Y-%m-%d')
    cursor.execute("INSERT INTO attendance (emp_id, date, status) VALUES (%s, %s, 'Present')", (emp_id, today))
    db.commit()
    print("✅ Attendance marked.\n")
    db.close()

def generate_salary_report():
    db = connect_db()
    cursor = db.cursor()
    month = input("Enter Month (YYYY-MM): ")
    query = """
        SELECT e.emp_id, e.name, COUNT(a.id) as days_present, e.salary_per_day,
               (COUNT(a.id) * e.salary_per_day) as total_salary
        FROM employees e
        JOIN attendance a ON e.emp_id = a.emp_id
        WHERE DATE_FORMAT(a.date, '%Y-%m') = %s AND a.status = 'Present'
        GROUP BY e.emp_id
    """
    cursor.execute(query, (month,))
    result = cursor.fetchall()
    headers = ["ID", "Name", "Days Present", "Salary/Day", "Total Salary"]
    if result:
        print("\n" + tabulate(result, headers=headers, tablefmt="grid"))
    else:
        print("No records found for that month.")
    db.close()

def view_attendance():
    db = connect_db()
    cursor = db.cursor()
    emp_id = input("Enter Employee ID (or leave blank for all): ")

    if emp_id:
        cursor.execute("""
            SELECT a.id, e.name, a.date, a.status
            FROM attendance a
            JOIN employees e ON a.emp_id = e.emp_id
            WHERE a.emp_id = %s
            ORDER BY a.date DESC
        """, (emp_id,))
    else:
        cursor.execute("""
            SELECT a.id, e.name, a.date, a.status
            FROM attendance a
            JOIN employees e ON a.emp_id = e.emp_id
            ORDER BY a.date DESC
        """)

    result = cursor.fetchall()
    headers = ["Attendance ID", "Employee Name", "Date", "Status"]
    if result:
        print("\n" + tabulate(result, headers=headers, tablefmt="grid"))
    else:
        print("No attendance records found.")
    db.close()

def backup_database():
    os.system("mysqldump -u root -pyourpassword employee_db > backup.sql")
    print("✅ Database backup created as 'backup.sql'.\n")

def main_menu():
    while True:
        print("Welcome to Employee Management System")
        print("1. Add Employee")
        print("2. View Employee")
        print("3. Mark Attendance")
        print("4. Generate Monthly Salary Report")
        print("5. View Attendance")
        print("6. Backup Database")
        print("7. Exit")
        choice = input("Enter your choice: ")
        if choice == '1':
            add_employee()
        elif choice == '2':
            view_employees()
        elif choice == '3':
            mark_attendance()
        elif choice == '4':
            generate_salary_report()
        elif choice == '5':
            view_attendance()
        elif choice == '6':
            backup_database()
        elif choice == '7':
            print("Exiting...")
            break
        else:
            print("❌ Invalid choice!\n")

if __name__ == "__main__":
    main_menu()
