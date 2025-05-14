import frappe
from frappe import _
from frappe.utils import get_url, now
from documenso.documenso.api.documenso import create_and_send_document


@frappe.whitelist()
def send_signing_request(doctype, docname):
    """Send signing request for a document"""
    doc = frappe.get_doc(doctype, docname)
    
    # Check if signatories are populated
    if not doc.signatory_detail:
        frappe.throw("Please add signatories before sending signing request")
    
    # Check if all signatories have valid emails
    for signatory in doc.signatory_detail:
        if not signatory.signatory_email:
            frappe.throw(f"Please provide email for {signatory.signatory_name}")
    
    # Update status to indicate sending started
    for signatory in doc.signatory_detail:
        if signatory.signature_status == "Not Initiated":
            signatory.last_tried = now()
    doc.save()
    
    # Create and send document
    try:
        result = create_and_send_document(doctype, docname)
        if result.get("status") == "success":
            frappe.msgprint(f"Document sent for signing. Document ID: {result.get('document_id')}")
        else:
            frappe.throw("Failed to send document for signing")
    except Exception as e:
        frappe.log_error(str(e), "Documenso Send Request Failed")
        frappe.throw(f"Failed to send document: {str(e)}")


@frappe.whitelist()
def fetch_authorized_signatories(doctype, docname):
    """Fetch authorized signatories for a doctype"""
    settings_doc = frappe.get_doc("Documenso Settings")
    doc = frappe.get_doc(doctype, docname)
    
    # Clear existing signatories
    doc.signatory_detail = []
    
    # Add authorized signatories
    for signatory in settings_doc.authorized_signatory:
        if signatory.permitted_doctype == doctype:
            doc.append("signatory_detail", {
                "signatory": signatory.signatory,
                "signatory_name": signatory.signatory_name,
                "signatory_email": signatory.signatory_email,
                "signing_order": signatory.signing_order,
                "required": signatory.required,
                "message": signatory.message
            })
    
    # Set print format and letter head
    for print_format in settings_doc.print_format:
        if print_format.permitted_doctype == doctype:
            doc.requested_print_format = print_format.print_format
            doc.requested_letter_head = print_format.letter_head
            break
    
    doc.save()
    frappe.msgprint("Signatories fetched successfully")


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
    doc = frappe.get_doc(doctype, docname)
    
    # Generate PDF
    html = frappe.get_print(
        doctype=doctype,
        name=docname,
        print_format=doc.requested_print_format,
        letterhead=doc.requested_letter_head
    )
    
    from frappe.utils.pdf import get_pdf
    pdf_content = get_pdf(html)
    
    # Return as base64
    import base64
    return base64.b64encode(pdf_content).decode('utf-8')
