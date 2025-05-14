from frappe import _

def get_data():
    return [
        {
            "module_name": "Documenso",
            "category": "Modules", 
            "label": _("Documenso"),
            "color": "blue",
            "icon": "octicon octicon-file-code",
            "type": "module",
            "description": "Digital signing with Documenso",
            "onboard_present": 1
        }
    ]
