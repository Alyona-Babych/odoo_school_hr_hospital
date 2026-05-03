{
    'name': 'HR Hospital',
    'summary': 'Hospital management system for doctors, patients, diseases, and visit tracking.',
    'author': 'Alyona Babych',
    'website': 'https://odoo.school/',
    'category': 'Services',
    'license': 'LGPL-3',
    'version': '19.0.1.1.0',

    'depends': [
        'base',
    ],

    'data': [

        'security/ir.model.access.csv',

        'data/hr_hospital_disease_data.xml',
        'data/hr_hospital_doctor_category.xml',

        'views/hr_hospital_patient_view.xml',
        'views/hr_hospital_doctor_category_view.xml',
        'views/hr_hospital_doctor_view.xml',
        'views/hr_hospital_doctor_history_view.xml',
        'views/hr_hospital_disease_view.xml',
        'views/hr_hospital_appointment_view.xml',
        'views/hr_hospital_menu.xml',

        'wizard/hr_hospital_mass_reassign_doctor_wizard_view.xml',
        'wizard/hr_hospital_visit_report_wizard.xml',
    ],

    'demo': [
        'demo/hr_hospital_doctor_demo.xml',
        'demo/hr_hospital_patient_demo.xml',
        'demo/hr_hospital_doctor_history_demo.xml',
        'demo/hr_hospital_appointment_demo.xml'
    ],

    'installable': True,
    'application': True,
    'auto_install': False,

    'images': [
        'static/description/icon.png',
    ],

}