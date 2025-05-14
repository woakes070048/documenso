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
                f"{self.base_url}/api/v1/documents",
                headers=self.headers,
                params={"limit": 1},
                timeout=10
            )
            return {"success": response.status_code == 200}
        except Exception as e:
            frappe.log_error(str(e), "Documenso Connection Test Failed")
            return {"success": False, "error": str(e)}
    
    def create_document(self, title, pdf_content):
        """Create a document in Documenso"""
        try:
            pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
            
            response = requests.post(
                f"{self.base_url}/api/v1/documents",
                headers=self.headers,
                json={
                    "title": title,
                    "documentDataAsBase64": pdf_base64,
                    "type": "application/pdf"
                },
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                frappe.throw(f"Failed to create document: {response.status_code} - {response.text}")
        except Exception as e:
            frappe.log_error(str(e), "Documenso Create Document Failed")
            frappe.throw(str(e))
    
    def add_recipient(self, document_id, recipient_data):
        """Add a recipient to a document"""
        try:
            payload = {
                "email": recipient_data["email"],
                "name": recipient_data["name"],
                "role": recipient_data.get("role", "SIGNER")
            }
            
            if "signingOrder" in recipient_data:
                payload["signingOrder"] = recipient_data["signingOrder"]
            
            response = requests.post(
                f"{self.base_url}/api/v1/documents/{document_id}/recipients",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                frappe.throw(f"Failed to add recipient: {response.status_code} - {response.text}")
        except Exception as e:
            frappe.log_error(str(e), "Documenso Add Recipient Failed")
            frappe.throw(str(e))
    
    def add_field(self, document_id, field_data):
        """Add a field to a document"""
        try:
            # Documenso API expects specific format
            payload = {
                "recipientId": field_data["recipientId"],
                "type": field_data.get("type", "SIGNATURE"),
                "placeholder": field_data.get("placeholder", ""),
                "required": field_data.get("required", True)
            }
            
            # If placeholder text is provided, use it for positioning
            if field_data.get("placeholder"):
                payload["placeholder"] = field_data["placeholder"]
            else:
                # Fallback to coordinate-based if no placeholder
                payload.update({
                    "page": field_data.get("page", 1),
                    "x": field_data.get("x", 100),
                    "y": field_data.get("y", 100),
                    "width": field_data.get("width", 200),
                    "height": field_data.get("height", 50)
                })
            
            response = requests.post(
                f"{self.base_url}/api/v1/documents/{document_id}/fields",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                frappe.throw(f"Failed to add field: {response.status_code} - {response.text}")
        except Exception as e:
            frappe.log_error(str(e), "Documenso Add Field Failed")
            frappe.throw(str(e))
    
    def send_document(self, document_id):
        """Send a document for signing"""
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/documents/{document_id}/send",
                headers=self.headers,
                json={},
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                frappe.throw(f"Failed to send document: {response.status_code} - {response.text}")
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
                frappe.throw(f"Failed to get document status: {response.status_code} - {response.text}")
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
                frappe.throw(f"Failed to download document: {response.status_code} - {response.text}")
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
    """Create and send document with placeholder-based field placement"""
    doc = frappe.get_doc(doctype, docname)
    api = DocumensoAPI()
    
    # Generate PDF
    html = frappe.get_print(
        doctype=doctype,
        name=docname,
        print_format=doc.requested_print_format,
        letterhead=doc.requested_letter_head
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
        
        recipient = api.add_recipient(document_id, recipient_data)
        recipient_id = recipient["id"]
        
        # Update signatory
        signatory.recipient_id = recipient_id
        signatory.signature_status = "Pending Review"
        
        # Add signature field using placeholder
        field_data = {
            "recipientId": recipient_id,
            "type": "SIGNATURE",
            "placeholder": signatory.placeholder or f"{{{{signature_{idx + 1}}}}}",
            "required": signatory.required
        }
        api.add_field(document_id, field_data)
        
        # Add date field next to signature
        date_field_data = {
            "recipientId": recipient_id,
            "type": "DATE",
            "placeholder": f"{{{{date_{idx + 1}}}}}",
            "required": True
        }
        api.add_field(document_id, date_field_data)
    
    doc.save()
    
    # Send document
    api.send_document(document_id)
    
    # Send notification emails
    for signatory in doc.signatory_detail:
        signing_link = f"{api.base_url}/sign/{document_id}"
        
        frappe.sendmail(
            recipients=[signatory.signatory_email],
            subject=f"Please sign: {doctype} {docname}",
            message=f"""
            <p>Dear {signatory.signatory_name},</p>
            <p>Please review and sign the document: {doctype} {docname}</p>
            <p><a href="{signing_link}" style="background: #22BC66; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Sign Document</a></p>
            <p>Thank you.</p>
            """,
            reference_doctype=doctype,
            reference_name=docname
        )
    
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
                    "PENDING": "Pending Review",
                    "SENT": "Pending Review",
                    "VIEWED": "Review In-Progress",
                    "SIGNED": "Completed",
                    "DECLINED": "Rejected"
                }
                signatory.signature_status = status_map.get(recipient["status"], recipient["status"])
                if recipient.get("signedAt"):
                    signatory.signed_at = recipient["signedAt"]
    
    doc.save()
    
    # If all signed, download the document
    if status_data.get("status") == "COMPLETED":
        signed_pdf = api.download_signed_document(doc.document_id)
        
        file_doc = frappe.new_doc("File")
        file_doc.file_name = f"{docname}_signed.pdf"
        file_doc.content = signed_pdf
        file_doc.attached_to_doctype = doctype
        file_doc.attached_to_name = docname
        file_doc.folder = "Home/Attachments"
        file_doc.is_private = 0
        file_doc.save(ignore_permissions=True)
        
        frappe.db.set_value(doctype, docname, "signed_document", file_doc.file_url)
        frappe.msgprint("Document has been signed and attached")
    
    return status_data


@frappe.whitelist()
def send_reminder(doctype, docname):
    """Send reminder to signatories"""
    doc = frappe.get_doc(doctype, docname)
    api = DocumensoAPI()
    
    for signatory in doc.signatory_detail:
        if signatory.signature_status in ["Pending Review", "Review In-Progress"]:
            signing_link = f"{api.base_url}/sign/{doc.document_id}"
            
            frappe.sendmail(
                recipients=[signatory.signatory_email],
                subject=f"Reminder: Please sign {doctype} {docname}",
                message=f"""
                <p>Dear {signatory.signatory_name},</p>
                <p>This is a reminder to sign the document: {doctype} {docname}</p>
                <p><a href="{signing_link}" style="background: #22BC66; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Sign Document</a></p>
                <p>Thank you.</p>
                """,
                reference_doctype=doctype,
                reference_name=docname
            )
    
    frappe.msgprint("Reminders sent successfully")


@frappe.whitelist()
def download_document_pdf(doctype, docname, signatory_details=None):
    """Download PDF for preview"""
    doc = frappe.get_doc(doctype, docname)
    
    if doc.signed_document:
        file_path = frappe.get_doc("File", {"file_url": doc.signed_document}).get_full_path()
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    else:
        html = frappe.get_print(
            doctype=doctype,
            name=docname,
            print_format=doc.requested_print_format,
            letterhead=doc.requested_letter_head
        )
        return base64.b64encode(get_pdf(html)).decode("utf-8")


@frappe.whitelist()
def fetch_documenso_authorized_signatory(doctype, docname):
    """Fetch authorized signatories from contacts and document owner"""
    doc = frappe.get_doc(doctype, docname)
    settings_doc = frappe.get_doc("Documenso Settings")
    
    # Clear existing signatories
    doc.signatory_detail = []
    
    # Add signatories based on settings
    signatory_index = 1
    
    for setting in settings_doc.authorized_signatory:
        if setting.permitted_doctype == doctype:
            if setting.signatory_type == "Contact":
                # Get contact from document
                contact = get_contact_from_document(doc)
                if contact:
                    doc.append("signatory_detail", {
                        "signatory_name": contact.get("name") or contact.get("full_name"),
                        "signatory_email": contact.get("email_id"),
                        "signing_order": signatory_index,
                        "required": setting.required,
                        "message": setting.message,
                        "placeholder": setting.placeholder or f"{{{{signature_{signatory_index}}}}}",
                        "signatory_type": "Customer/Supplier"
                    })
                    signatory_index += 1
            
            elif setting.signatory_type == "Document Owner":
                # Get document owner
                owner = frappe.get_doc("User", doc.owner)
                doc.append("signatory_detail", {
                    "signatory": doc.owner,
                    "signatory_name": owner.full_name,
                    "signatory_email": owner.email,
                    "signing_order": signatory_index,
                    "required": setting.required,
                    "message": setting.message,
                    "placeholder": setting.placeholder or f"{{{{signature_{signatory_index}}}}}",
                    "signatory_type": "Internal"
                })
                signatory_index += 1
            
            elif setting.signatory_type == "User" and setting.signatory:
                # Specific user
                user = frappe.get_doc("User", setting.signatory)
                doc.append("signatory_detail", {
                    "signatory": setting.signatory,
                    "signatory_name": user.full_name or setting.signatory_name,
                    "signatory_email": user.email or setting.signatory_email,
                    "signing_order": signatory_index,
                    "required": setting.required,
                    "message": setting.message,
                    "placeholder": setting.placeholder or f"{{{{signature_{signatory_index}}}}}",
                    "signatory_type": "Internal"
                })
                signatory_index += 1
    
    # Set print format and letter head
    for print_format in settings_doc.print_format:
        if print_format.permitted_doctype == doctype:
            doc.requested_print_format = print_format.print_format
            doc.requested_letter_head = print_format.letter_head
            break
    
    doc.save()
    frappe.msgprint("Signatories fetched successfully")


def get_contact_from_document(doc):
    """Get contact from document based on customer/supplier/employee"""
    contact = None
    
    # Try to get contact based on common link fields
    if hasattr(doc, "customer") and doc.customer:
        contact = get_primary_contact("Customer", doc.customer)
    elif hasattr(doc, "supplier") and doc.supplier:
        contact = get_primary_contact("Supplier", doc.supplier)
    elif hasattr(doc, "employee") and doc.employee:
        contact = get_primary_contact("Employee", doc.employee)
    elif hasattr(doc, "party_name") and doc.party_name:
        # For documents with party_type and party_name
        party_type = getattr(doc, "party_type", None)
        if party_type:
            contact = get_primary_contact(party_type, doc.party_name)
    
    return contact


def get_primary_contact(doctype, name):
    """Get primary contact for a party"""
    contacts = frappe.get_all(
        "Dynamic Link",
        filters={
            "link_doctype": doctype,
            "link_name": name,
            "parenttype": "Contact"
        },
        fields=["parent"]
    )
    
    if contacts:
        # Get the primary contact or first available
        for contact in contacts:
            contact_doc = frappe.get_doc("Contact", contact.parent)
            if contact_doc.is_primary_contact:
                return contact_doc.as_dict()
        
        # Return first contact if no primary found
        return frappe.get_doc("Contact", contacts[0].parent).as_dict()
    
    return None