from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
import re
from datetime import datetime
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
    if request.method == "POST":
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
        return redirect(url_for('jobdetails', job_id=job_id))

    # Fetch job details based on job_id
    connection.execute(
        """
        SELECT 
            job.job_id, 
            GROUP_CONCAT(DISTINCT part.part_name, " ( qty: ", job_part.qty, " ) ") as parts,
            GROUP_CONCAT(DISTINCT service.service_name, " ( qty: ", job_service.qty, " ) ") as services
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

    return render_template("job_details.html", job_details=jobDetails, parts=parts, services=services)
