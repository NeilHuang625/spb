
- [Web application structure](#web-application-structure)
  - [Technician Interface](#technician-interface)
    - [`base.html`](#basehtml)
    - [`currentjobslist.html`](#currentjobslisthtml)
    - [`job_details.html`](#job_detailshtml)
    - [`addPart.html` and `addService.html`](#addparthtml-and-addservicehtml)
  - [Admin Interface](#admin-interface)
    - [`admin.html`](#adminhtml)
    - [`customerList.html`](#customerlisthtml)
    - [`partList.html and serviceList.html`](#partlisthtml-and-servicelisthtml)
    - [`addPart.html and addService.html`](#addparthtml-and-addservicehtml-1)
    - [`addCustomer.html`](#addcustomerhtml)
    - [`unpaidBills.html`](#unpaidbillshtml)
    - [`report.html`](#reporthtml)
- [Design decisions](#design-decisions)
- [Database questions:](#database-questions)
  - [Answer to Question1](#answer-to-question1)
  - [Answer to Question2](#answer-to-question2)
  - [Answer to Question3](#answer-to-question3)
  - [Answer to Question4](#answer-to-question4)
  - [Answer to Question5](#answer-to-question5)



## Web application structure
### Technician Interface
#### `base.html`
Boilerplate for currentjobslist.html and job_details.html

------------
#### `currentjobslist.html`
Obtain database information through route `/currentjobs` get method and pass `job_list`

------------
#### `job_details.html`
Obtain database information through the route `/jobdetails/<job_id>` get method, and pass `job_details`, `parts`, `services`, `completed` to display the content and status of the job.

------------
#### `addPart.html` and `addService.html`
Add parts and services to the specified job through the route `/jobdetails/<job_id>` post method, and update the completion status of the job through the same route through the button "marked as completed".

------------
### Admin Interface
#### `admin.html`
Boilerplate for all templates that are not technician

------------
#### `customerList.html`
Rendered through route `/admin` and pass `customerList` and `message` to it. The `message` is displayed based on customer search results. The search button obtains the search customer through the route `/admin `get method.
The add job button takes customer_id to create a new job for the specified customer through the post method of route `/admin/addjob/<customer_id>`.

------------
#### `partList.html and serviceList.html`
Parts and services are obtained through the get methods of route `/admin/partList` and route `/admin/serviceList` respectively, and passed to the above two templates respectively.

------------
#### `addPart.html and addService.html`
Add new parts and services through the post methods of route `/admin/addpart` and `/admin/addservice` respectively.

------------
#### `addCustomer.html`
adds a new customer through route `/admin/addcustomer`.

------------
#### `unpaidBills.html`
Rendered through route `/admin/unpaidBills` and pass `bills` to it. Each customer has a mark as paid button. This button updates the `paid` status through the `/admin/unpaidBills` post method.

------------
#### `report.html`
Render through route `/admin/reports` and pass the `bills` to it, and the specific job is marked in red.

------------
## Design decisions
The naming of routes is the focus of my design. Good route naming principles can reflect its functions more clearly, thereby improving the efficiency of writing code. For example, in this project, all routes starting with `/admin` are interfaces related to admin. I like to use `if` statements to use get and post methods in the same route. Firstly, it is easy to distinguish them through `if` statements, and secondly, their functions are closely related to the route names. For example, through route `/admin/addcustomer`, the get method is to render the template for adding a new customer, and the post method is to add a new customer. Similarly, I merge add part and add service and use route `/jobdetails/<job_id>` to process them together, because they are closely related to a specific job.

In addition, I copied the boilerplate `admin.html` that are almost the same as `base.html` for the admin interface. This completely separates the boilerplate used by technician and admin, and also makes the file naming more meaningful.

In terms of page layout design, I keep the style of the page consistent, which is more conducive to the continued development and management of the web page. Using bootstrap, I designed them to be devices responsive. When the screen size reaches a certain level, the navbar will collapse and become a button, making the page easier to navigate and use.

In terms of form validation, I validate each field of the table strictly according to the data type of the database to ensure that the system will not crash due to inappropriate data types.
## Database questions:
### Answer to Question1


    CREATE TABLE IF NOT EXISTS job
    (
    job_id INT auto_increment PRIMARY KEY NOT NULL,
    job_date date NOT NULL,
    customer int NOT NULL,
    total_cost decimal(6,2) default null,
    tiny completedint default 0,
    paid tinyint default 0,
    
    FOREIGN KEY (customer) REFERENCES customer(customer_id)
    ON UPDATE CASCADE
    );
### Answer to Question2


    FOREIGN KEY (customer) REFERENCES customer(customer_id)
### Answer to Question3


    INSERT INTO part (`part_name`, `cost`) VALUES ('Windscreen', '560.65');
    INSERT INTO part (`part_name`, `cost`) VALUES ('Headlight', '35.65');
    INSERT INTO part (`part_name`, `cost`) VALUES ('Wiper blade', '12.43');
    INSERT INTO part (`part_name`, `cost`) VALUES ('Left fender', '260.76');
    INSERT INTO part (`part_name`, `cost`) VALUES ('Right fender', '260.76');
    INSERT INTO part (`part_name`, `cost`) VALUES ('Tail light', '120.54');
    INSERT INTO part (`part_name`, `cost`) VALUES ('Hub Cap', '22.89');

### Answer to Question4
In the `job_part` table, add new column `added_time`, and set the data type to be `DATETIME`.

### Answer to Question5
In a team, a clear division of labor for each position can improve the work efficiency of the entire team. The technician is responsible for auto repairing, and they know best what parts and services are used in a job. Similarly, the admin can quickly obtain relevant information from other departments. For example, the company has purchased new parts that need to be stored in the database and update the system's part options. If all functions of the system are accessible to people in all positions, many other problems will arise:

1. Data Privacy: Technicians and office administrators often have different roles and responsibilities within an organization. Allowing them different routes of access ensures that sensitive information is protected and only accessible by authorized personnel. For example: If all facilities are available to everyone, technicians may inadvertently access confidential office management data, such as financial records or employee information, compromising data privacy and security.

2. Workflow efficiency and task management: Providing access to specific routes customized for each role helps streamline workflow and improve task management. For example: Technicians may need access to routes designed specifically for managing service requests, updating job status, or accessing technical documentation related to their tasks. Allowing them access to only these routes ensures they can perform their job responsibilities effectively without having to navigate unrelated functions.