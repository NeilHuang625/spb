from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
import re
from datetime import date, timedelta
import mysql.connector
from mysql.connector import FieldType
import connect

app = Flask(__name__)

dbconn = None
connection = None


def getCursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(user=connect.dbuser,
                                         password=connect.dbpass, host=connect.dbhost,
                                         database=connect.dbname, autocommit=True)
    dbconn = connection.cursor()
    return dbconn


@app.route("/")
def home():
    return redirect("/currentjobs")


@app.route("/currentjobs")
def currentjobs():
    connection = getCursor()
    connection.execute(
        "SELECT job.job_id, customer.first_name, customer.family_name, job.job_date FROM job INNER JOIN customer ON job.customer = customer.customer_id WHERE job.completed = 0;")
    jobList = connection.fetchall()
    return render_template("currentjoblist.html", job_list=jobList)


@app.route("/jobdetails/<job_id>", methods=["GET", "POST"])
def jobdetails(job_id):
    connection = getCursor()

    # Fetch job status
    connection.execute(
        "SELECT completed FROM job WHERE job_id = %s", (job_id,))
    completed = connection.fetchone()[0]

    if request.method == "POST":

        # Handle part form submission
        if "part" in request.form:
            part_id = request.form["part"]
            part_qty = request.form["part_qty"]

            # Fetch part cost
            connection.execute(
                "SELECT cost FROM part WHERE part_id = %s", (part_id,))
            part_cost = connection.fetchone()[0]

            # Check if part is already added to job
            connection.execute(
                "SELECT * FROM job_part WHERE job_id = %s AND part_id = %s", (job_id, part_id))
            if connection.fetchone() is not None and part_qty != "0":
                # Update part quantity
                connection.execute(
                    "UPDATE job_part SET qty = qty + %s WHERE job_id = %s AND part_id = %s", (part_qty, job_id, part_id))
            else:
                # Server side validation for part quantity
                if part_qty != "0":
                    # Add part to job only if quantity is not 0
                    connection.execute(
                        "INSERT INTO job_part (job_id, part_id, qty) VALUES (%s, %s, %s)", (job_id, part_id, part_qty))

            # Update job cost
            connection.execute(
                "UPDATE job SET total_cost = COALESCE(total_cost, 0) + %s WHERE job_id = %s", (part_cost * int(
                    part_qty), job_id)
            )

        # Handle service form submission
        elif "service" in request.form:
            service_id = request.form["service"]
            service_qty = request.form["service_qty"]

            # Fetch service cost
            connection.execute(
                "SELECT cost FROM service WHERE service_id = %s", (service_id,))
            service_cost = connection.fetchone()[0]
            print(service_cost)

            # Check if service already exists in job
            connection.execute(
                "SELECT * FROM job_service WHERE job_id = %s AND service_id = %s", (job_id, service_id))
            if connection.fetchone() is not None and service_qty != "0":
                # Update service quantity
                connection.execute(
                    "UPDATE job_service SET qty = qty + %s WHERE job_id = %s AND service_id = %s", (service_qty, job_id, service_id))
            else:
                # Server side validation for service quantity
                if service_qty != "0":
                    # Add service to job only if quantity is not 0
                    connection.execute(
                        "INSERT INTO job_service (job_id, service_id, qty) VALUES (%s, %s, %s)", (job_id, service_id, service_qty))

            # Update job cost
            connection.execute(
                "UPDATE job SET total_cost = COALESCE(total_cost, 0) + %s WHERE job_id = %s", (
                    service_cost * int(service_qty), job_id)
            )

        # Handle Marked as Completed button
        elif "complete" in request.form:
            # Update job completion status to 1 and calculate job total cost
            connection.execute(
                "UPDATE job SET completed = 1 WHERE job_id = %s", (job_id,))

        return redirect(url_for('jobdetails', job_id=job_id))

    # Fetch job details based on job_id
    connection.execute(
        """
        SELECT 
            job.job_id, 
            GROUP_CONCAT(DISTINCT part.part_name, " ( qty: ", job_part.qty, " ) ") as parts,
            GROUP_CONCAT(DISTINCT service.service_name, " ( qty: ", job_service.qty, " ) ") as services,
            job.total_cost
        FROM 
            job 
        INNER JOIN 
            customer ON job.customer = customer.customer_id 
        LEFT JOIN 
            job_part ON job.job_id = job_part.job_id
        LEFT JOIN 
            part ON job_part.part_id = part.part_id
        LEFT JOIN 
            job_service ON job.job_id = job_service.job_id
        LEFT JOIN 
            service ON job_service.service_id = service.service_id
        WHERE 
            job.job_id = %s
        GROUP BY 
            job.job_id;
        """,
        (job_id,))
    jobDetails = connection.fetchone()

    # Fetch name of parts and services for dropdown list in job details page
    connection.execute("SELECT part_id, part_name FROM part")
    parts = connection.fetchall()
    connection.execute("SELECT service_id, service_name FROM service")
    services = connection.fetchall()

    return render_template("job_details.html", job_details=jobDetails, parts=parts, services=services, completed=completed)


@app.route("/admin", methods=["GET", "POST"])
def admin():
    message = ""
    connection = getCursor()
    searchTerm = request.args.get("search")
    if searchTerm is not None:
        connection.execute(
            "SELECT * FROM customer WHERE first_name LIKE %s OR family_name LIKE %s", (f"%{searchTerm}%", f"%{searchTerm}%"))
        customerList = connection.fetchall()
        if len(customerList) == 0:
            message = "No results found! Please try again."
    else:
        connection.execute("SELECT * FROM customer")
        customerList = connection.fetchall()
    return render_template("customerList.html", customerList=customerList, message=message)


@app.route("/admin/addcustomer", methods=["GET", "POST"])
def addCustomer():
    connection = getCursor()
    if request.method == "POST":
        first_name = request.form["firstName"]
        family_name = request.form["familyName"]
        email = request.form["email"]
        phone = request.form["phone"]
        connection.execute(
            "INSERT INTO customer (first_name, family_name, email, phone) VALUES (%s, %s, %s, %s)",
            (first_name, family_name, email, phone)
        )
        return redirect("/admin")

    # Render add customer page when request method is GET
    return render_template("addCustomer.html")


@app.route("/admin/addpart", methods=["GET", "POST"])
def addPart():
    connection = getCursor()
    if request.method == "POST":
        part_name = request.form["partName"]
        part_cost = request.form["partCost"]
        connection.execute(
            "INSERT INTO part (part_name, cost) VALUES (%s, %s)",
            (part_name, part_cost)
        )
        return redirect("/admin/partList")

    # Render add part page when request method is GET
    return render_template("addPart.html")


@app.route("/admin/partList")
def partList():
    connection = getCursor()
    connection.execute("SELECT * FROM part")
    partList = connection.fetchall()
    return render_template("partList.html", parts=partList)


@app.route("/admin/addservice", methods=["GET", "POST"])
def addService():
    connection = getCursor()
    if request.method == "POST":
        service_name = request.form["serviceName"]
        service_cost = request.form["serviceCost"]
        connection.execute(
            "INSERT INTO service (service_name, cost) VALUES (%s, %s)",
            (service_name, service_cost)
        )
        return redirect("/admin/serviceList")

    # Render add service page when request method is GET
    return render_template("addService.html")


@app.route("/admin/serviceList")
def serviceList():
    connection = getCursor()
    connection.execute("SELECT * FROM service")
    serviceList = connection.fetchall()
    return render_template("serviceList.html", services=serviceList)


@app.route("/admin/addjob/<customer_id>", methods=["GET", "POST"])
def addJob(customer_id):
    connection = getCursor()
    if request.method == "POST":
        job_date = request.form["jobDate"]
        connection.execute(
            "INSERT INTO job (job_date, customer) VALUES (%s, %s)",
            (job_date, customer_id)
        )
        return redirect("/admin")

    # Render add job page when request method is GET
    # Pass today's date and customer_id to the template
    return render_template("addJob.html", today=date.today().isoformat(), customer_id=customer_id)


@app.route("/admin/unpaidBills", methods=["GET", "POST"])
def unpaidBills():
    connection = getCursor()
    if request.method == "POST":
        # Mark selected bill as paid
        bill_id = request.form["billId"]
        connection.execute(
            "UPDATE job SET paid = 1 WHERE job_id = %s",
            (bill_id,)
        )
        return redirect("/admin/unpaidBills")

    # Fetch all unpaid bills, ordered by date and then by customer
    connection.execute(
        "SELECT * FROM job WHERE paid = 0 ORDER BY job_date, customer"
    )
    bills = connection.fetchall()

    return render_template("unpaidBills.html", bills=bills)


@app.route("/admin/reports", methods=["GET"])
def getBillReport():
    connection = getCursor()
    # Fetch all unpaid bills
    connection.execute(
        """
        SELECT customer.customer_id, customer.family_name, customer.first_name, job.job_date, COALESCE(job.total_cost, 0)
        FROM customer
        JOIN job ON customer.customer_id = job.customer
        WHERE job.paid = 0
        ORDER BY customer.customer_id, job.job_date ASC
        """
    )
    bills = connection.fetchall()

    # Setup today date and date 14 days ago
    today = date.today()
    days_ago_14 = today - timedelta(days=14)
    print(bills)

    return render_template("report.html", bills=bills, days_ago_14=days_ago_14)
