{
    "name": "L10N CR ASISTENCIAS",
    'summary': """
        Mejora de asistencias para trabajadores""",
    'description': """       
        1. Agregar configuración tiempo max permitido.
        2. Controlar tiempo de asistencia -> Envio de correo (acorde el tiempo max)
        3. Capturar dirección ip en lista de asistencias
    """,
    'version': '0.3',
    "author": "Jhonny Mack Merino Samillán. Chiclayo - Perú",
    'license': 'LGPL-3',
    "depends": ['base','hr','hr_attendance','web_notify'],
    "data": [
        # security
        "security/security.xml",
        "security/ir.model.access.csv",
        # data
        "data/mail_template_coach.xml",
        "data/mail_template_employee.xml",
        "data/mail_template_justify.xml",
        "data/mail_template_justify_validate.xml",
        "data/sequence.xml",
        # views
        "views/menu.xml",
        "views/hr_attendance_view.xml",
        "views/res_config_settings_views.xml",
        "views/hr_attendance_justify_wizard.xml",
        "views/hr_attendance_justify_views.xml",
        "views/web_asset_backend_template.xml",

    ],
}
