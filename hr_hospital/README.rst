===================
HR Hospital
===================

Overview
========

The ``hr_hospital`` module is a hospital management solution for Odoo 19.

The module provides functionality for managing:

* Doctors
* Patients
* Diseases and disease hierarchy
* Patient visits
* Doctor qualifications
* Personal doctor history
* Medical reports and analytics
* Appointment scheduling

The module also includes advanced Odoo features such as:

* Wizards
* Calendar, Kanban, Pivot, Graph, and Search views
* Access rights and security groups
* Printable QWeb report
* Demo and master data
* Ukrainian translations
* Automated business logic and validations


Installation
============

To install the module:

1. Copy the ``hr_hospital`` module into the Odoo custom addons directory.
2. Restart the Odoo server.
3. Activate Developer Mode in Odoo.
4. Open the Apps menu.
5. Click ``Update Apps List``.
6. Search for ``HR Hospital``.
7. Click ``Activate``.

Requirements
------------

* Odoo 19
* Python 3.12+
* Required standard Odoo applications:

  * Base
  * Web


Configuration
=============

After installation:

1. Open the ``HR Hospital`` menu.
2. Configure doctor categories.
3. Create doctors and patients.
4. Configure diseases hierarchy if necessary.
5. Assign users and access groups.
6. Create and manage patient visits.


Usage
=====

Doctors
-------

* Manage doctor profiles and qualifications.
* Assign mentors for interns.
* View intern relationships in Kanban and Form views.
* Print doctor visit report.

Patients
--------

* Store personal and medical information.
* Assign personal doctors.
* Track doctor assignment history.
* Create quick appointments from the patient form.

Visits
------

* Schedule patient visits.
* Track visit statuses:

  * Planned
  * Done
  * Cancelled

* Use calendar, graph, and pivot views for analytics.
* Generate reports using wizard tools.

Reports
-------

The module includes:

* Visit report wizard
* Disease report wizard
* Printable doctor reports in PDF format


Security
========

The module provides several user groups:

* Patient
* Intern
* Doctor
* Manager
* Administrator

Access rights and record rules are configured according to hospital roles.


Demo Data
=========

The module includes demo and master data for:

* Doctors
* Patients
* Diseases
* Doctor categories
* Visits
* Doctor history


Authors
=======

* Alyona Babych

Contact Information
-------------------

* Email: to.olena.babych@gmail.com
* GitHub: https://github.com/Alyona-Babych