import base64
import json
import requests
import frappe
from frappe import _
from frappe.utils import get_url, now
from frappe.utils.pdf import get_pdf


class DocumensoAPI:
    def __init__(self):
        self.settings = frappe.get_doc("Documenso Settings")
        self.base_url = self.settings.api_url
        self.api_key = self.settings.get_password("api_key")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def test_connection(self):
        """Test the API connection"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/teams",
                headers=self.headers,
                timeout=10
            )
            return {"success": response.status_code == 200}
        except Exception as e:
            frappe.log_error(str(e), "Documenso Connection Test Failed")
            return {"success": False, "error": str(e)}
    
    def create_document(self, title, pdf_content):
        """Create a document in Documenso"""
        try:
            # Convert PDF content to base64
            pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
            
            response = requests.post(
                f"{self.base_url}/api/v1/documents",
                headers=self.headers,
                json={
                    "title": title,
                    "documentData": pdf_base64,
                    "type": "application/pdf"
                },
                timeout=30
            )
            
            if response.status_code == 201:
                return response.json()
            else:
                frappe.throw(f"Failed to create document: {response.text}")
        except Exception as e:
            frappe.log_error(str(e), "Documenso Create Document Failed")
            frappe.throw(str(e))
    
    def add_recipient(self, document_id, recipient_data):
        """Add a recipient to a document"""
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/documents/{document_id}/recipients",
                headers=self.headers,
                json=recipient_data,
                timeout=30
            )
            
            if response.status_code == 201:
                return response.json()
            else:
                frappe.throw(f"Failed to add recipient: {response.text}")
        except Exception as e:
            frappe.log_error(str(e), "Documenso Add Recipient Failed")
            frappe.throw(str(e))
    
    def add_field(self, document_id, field_data):
        """Add a field to a document"""
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/documents/{document_id}/fields",
                headers=self.headers,
                json=field_data,
                timeout=30
            )
            
            if response.status_code == 201:
                return response.json()
            else:
                frappe.throw(f"Failed to add field: {response.text}")
        except Exception as e:
            frappe.log_error(str(e), "Documenso Add Field Failed")
            frappe.throw(str(e))
    
    def send_document(self, document_id):
        """Send a document for signing"""
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/documents/{document_id}/send",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                frappe.throw(f"Failed to send document: {response.text}")
        except Exception as e:
            frappe.log_error(str(e), "Documenso Send Document Failed")
            frappe.throw(str(e))
    
    def get_document_status(self, document_id):
        """Get document status"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/documents/{document_id}",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                frappe.throw(f"Failed to get document status: {response.text}")
        except Exception as e:
            frappe.log_error(str(e), "Documenso Get Document Status Failed")
            frappe.throw(str(e))
    
    def download_signed_document(self, document_id):
        """Download the signed document"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/documents/{document_id}/download",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.content
            else:
                frappe.throw(f"Failed to download document: {response.text}")
        except Exception as e:
            frappe.log_error(str(e), "Documenso Download Document Failed")
            frappe.throw(str(e))


@frappe.whitelist()
def test_connection():
    """Test Documenso API connection"""
    api = DocumensoAPI()
    return api.test_connection()


@frappe.whitelist()
def create_and_send_document(doctype, docname):
    """Create and send a document for signing"""
    doc = frappe.get_doc(doctype, docname)
    api = DocumensoAPI()
    
    # Generate PDF
    print_format = doc.requested_print_format
    letter_head = doc.requested_letter_head
    
    html = frappe.get_print(
        doctype=doctype,
        name=docname,
        print_format=print_format,
        letterhead=letter_head
    )
    pdf_content = get_pdf(html)
    
    # Create document in Documenso
    document_data = api.create_document(f"{doctype} - {docname}", pdf_content)
    document_id = document_data["id"]
    
    # Update document with Documenso document ID
    frappe.db.set_value(doctype, docname, "document_id", document_id)
    
    # Add recipients and fields
    for idx, signatory in enumerate(doc.signatory_detail):
        # Add recipient
        recipient_data = {
            "email": signatory.signatory_email,
            "name": signatory.signatory_name,
            "role": "SIGNER",
            "signingOrder": signatory.signing_order or idx + 1
        }
        
        if signatory.message:
            recipient_data["message"] = signatory.message
        
        recipient = api.add_recipient(document_id, recipient_data)
        signatory.recipient_id = recipient["id"]
        signatory.signature_status = "Pending"
        
        # Add signature field for this recipient
        field_data = {
            "recipientId": recipient["id"],
            "type": "SIGNATURE",
            "page": 1,
            "x": 100,
            "y": 100 + (idx * 100),  # Space out signatures
            "width": 200,
            "height": 50,
            "required": signatory.required
        }
        api.add_field(document_id, field_data)
    
    doc.save()
    
    # Send document
    api.send_document(document_id)
    
    frappe.msgprint(f"Document sent for signing. Document ID: {document_id}")
    return {"status": "success", "document_id": document_id}


@frappe.whitelist()
def check_document_status(doctype, docname):
    """Check the status of a document"""
    doc = frappe.get_doc(doctype, docname)
    if not doc.document_id:
        frappe.throw("No document ID found")
    
    api = DocumensoAPI()
    status_data = api.get_document_status(doc.document_id)
    
    # Update signatory statuses
    for recipient in status_data.get("recipients", []):
        for signatory in doc.signatory_detail:
            if signatory.recipient_id == recipient["id"]:
                status_map = {
                    "PENDING": "Pending",
                    "SENT": "Pending",
                    "VIEWED": "Viewed",
                    "SIGNED": "Signed",
                    "DECLINED": "Declined"
                }
                signatory.signature_status = status_map.get(recipient["status"], recipient["status"])
                if recipient.get("signedAt"):
                    signatory.signed_at = recipient["signedAt"]
    
    doc.save()
    
    # If all signed, download the document
    if status_data.get("status") == "COMPLETED":
        signed_pdf = api.download_signed_document(doc.document_id)
        file_doc = frappe.get_doc({
            "doctype": "File",
            "content": signed_pdf,
            "attached_to_doctype": doctype,
            "attached_to_name": docname,
            "file_type": "PDF",
            "is_private": 0,
            "file_name": f"{docname}_signed.pdf",
            "folder": "Home/Attachments"
        })
        file_doc.insert(ignore_permissions=True)
        
        frappe.db.set_value(doctype, docname, "signed_document", file_doc.file_url)
        frappe.msgprint("Document has been signed and attached")
    
    return status_data


@frappe.whitelist()
def send_reminder(doctype, docname):
    """Send reminder to signatories"""
    doc = frappe.get_doc(doctype, docname)
    
    for signatory in doc.signatory_detail:
        if signatory.signature_status in ["Pending", "Viewed"]:
            # Send reminder email through Documenso
            # This would use Documenso's reminder API if available
            # For now, send a manual reminder
            frappe.sendmail(
                recipients=[signatory.signatory_email],
                subject=f"Reminder: Please sign {doctype} {docname}",
                message=f"""
                <p>Dear {signatory.signatory_name},</p>
                <p>This is a reminder to sign the document: {doctype} {docname}</p>
                <p>Please check your email for the signing link from Documenso.</p>
                <p>Thank you.</p>
                """,
                reference_doctype=doctype,
                reference_name=docname
            )
    
    frappe.msgprint("Reminders sent successfully")
