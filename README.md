**Table of Contents**

[TOCM]

[TOC]
##Web application structure
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
###Admin Interface
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
##Design decisions
##Database questions:
### Question1
### Question2
### Question3
### Question4
### Question5