import frappe
from frappe import _
from documenso.documenso.api.documenso import create_and_send_document


@frappe.whitelist()
def send_email_request(doctype, docname):
    """Send signing request using placeholder-based field placement"""
    try:
        # Create and send the document
        result = create_and_send_document(doctype, docname)
        
        if result.get("status") == "success":
            frappe.msgprint(f"Document sent for signing with placeholders")
        else:
            frappe.throw("Failed to send document for signing")
    except Exception as e:
        frappe.log_error(str(e), "Documenso Send Request Failed")
        frappe.throw(f"Failed to send document: {str(e)}")


@frappe.whitelist()
def fetch_authorized_signatories(doctype, docname):
    """Fetch authorized signatories from contacts and document owner"""
    from documenso.documenso.api.documenso import fetch_documenso_authorized_signatory
    fetch_documenso_authorized_signatory(doctype, docname)


@frappe.whitelist()
def check_signing_status(doctype, docname):
    """Check signing status of a document"""
    from documenso.documenso.api.documenso import check_document_status
    
    status = check_document_status(doctype, docname)
    frappe.msgprint(f"Document status: {status.get('status')}")
    return status


@frappe.whitelist()
def download_document_pdf(doctype, docname):
    """Download the PDF for preview"""
    from documenso.documenso.api.documenso import download_document_pdf as download_pdf
    return download_pdf(doctype, docname)