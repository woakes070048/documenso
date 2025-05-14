import frappe
from frappe.utils import now_datetime, add_days


def check_pending_signatures():
    """Check for pending signatures and send reminders"""
    settings = frappe.get_doc("Documenso Settings")
    
    if not settings.reminder_days:
        return
    
    reminder_date = add_days(now_datetime(), -settings.reminder_days)
    
    # Get all enabled doctypes
    for doctype_row in settings.doctypes:
        doctype = doctype_row.doctype_name
        
        # Find documents with pending signatures
        docs = frappe.get_all(
            doctype,
            filters={
                "document_id": ["!=", ""],
                "signed_document": ["=", ""]
            },
            fields=["name", "modified"]
        )
        
        for doc in docs:
            if doc.modified < reminder_date:
                # Send reminder
                from documenso.documenso.api.documenso import send_reminder
                try:
                    send_reminder(doctype, doc.name)
                except Exception as e:
                    frappe.log_error(str(e), f"Reminder Failed for {doctype} {doc.name}")


def sync_document_status():
    """Sync document status with Documenso"""
    settings = frappe.get_doc("Documenso Settings")
    
    # Get all enabled doctypes
    for doctype_row in settings.doctypes:
        doctype = doctype_row.doctype_name
        
        # Find documents with pending signatures
        docs = frappe.get_all(
            doctype,
            filters={
                "document_id": ["!=", ""],
                "signed_document": ["=", ""]
            },
            fields=["name"]
        )
        
        for doc in docs:
            # Check status
            from documenso.documenso.api.documenso import check_document_status
            try:
                check_document_status(doctype, doc.name)
            except Exception as e:
                frappe.log_error(str(e), f"Status Sync Failed for {doctype} {doc.name}")
