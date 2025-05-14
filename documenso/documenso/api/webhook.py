import frappe
import hmac
import hashlib
from frappe import _


@frappe.whitelist(allow_guest=True)
def documenso_webhook():
    """Handle Documenso webhooks"""
    # Get the request data
    data = frappe.request.get_json()
    
    # Verify webhook signature if webhook secret is configured
    settings = frappe.get_doc("Documenso Settings")
    webhook_secret = settings.get_password("webhook_secret")
    
    if webhook_secret:
        signature = frappe.request.headers.get("X-Documenso-Signature")
        if not signature:
            frappe.throw("Missing webhook signature", frappe.AuthenticationError)
        
        # Calculate expected signature
        payload = frappe.request.get_data()
        expected_signature = hmac.new(
            webhook_secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected_signature):
            frappe.throw("Invalid webhook signature", frappe.AuthenticationError)
    
    # Handle the webhook
    response = handle_webhook(data)
    
    frappe.response["type"] = "json"
    frappe.response["data"] = response


def handle_webhook(data):
    """Handle Documenso webhook events"""
    try:
        event_type = data.get("type") or data.get("event")
        payload = data.get("data") or data
        
        if event_type == "document.completed":
            handle_document_completed(payload)
        elif event_type == "signature.completed" or event_type == "recipient.signed":
            handle_signature_completed(payload)
        
        return {"status": "success"}
    except Exception as e:
        frappe.log_error(str(e), "Documenso Webhook Error")
        return {"status": "error", "message": str(e)}


def handle_document_completed(payload):
    """Handle document completed event"""
    document_id = payload.get("documentId") or payload.get("id")
    
    if not document_id:
        frappe.log_error("No document ID in webhook payload", "Documenso Webhook Error")
        return
    
    # Find the document and update status
    filters = {"document_id": document_id}
    for doctype in frappe.get_all("Documenso Doctype", pluck="doctype_name"):
        docs = frappe.get_all(doctype, filters=filters, limit=1)
        if docs:
            doc = frappe.get_doc(doctype, docs[0].name)
            
            # Update all signatories to completed
            for signatory in doc.signatory_detail:
                if signatory.signature_status != "Completed":
                    signatory.signature_status = "Completed"
                    signatory.signed_at = frappe.utils.now()
            
            doc.save()
            
            # Check and download signed document
            from documenso.documenso.api.documenso import check_document_status
            check_document_status(doctype, docs[0].name)
            break


def handle_signature_completed(payload):
    """Handle signature completed event"""
    document_id = payload.get("documentId") or payload.get("id")
    recipient_email = payload.get("recipientEmail") or payload.get("email")
    
    if not document_id:
        frappe.log_error("No document ID in webhook payload", "Documenso Webhook Error")
        return
    
    # Update recipient status
    filters = {"document_id": document_id}
    for doctype in frappe.get_all("Documenso Doctype", pluck="doctype_name"):
        docs = frappe.get_all(doctype, filters=filters, limit=1)
        if docs:
            doc = frappe.get_doc(doctype, docs[0].name)
            updated = False
            
            for signatory in doc.signatory_detail:
                if signatory.signatory_email == recipient_email:
                    signatory.signature_status = "Completed"
                    signatory.signed_at = frappe.utils.now()
                    updated = True
                    break
            
            if updated:
                doc.save()
                
                # Check if all signatures are complete
                all_signed = all(s.signature_status == "Completed" for s in doc.signatory_detail)
                if all_signed:
                    # Download signed document
                    from documenso.documenso.api.documenso import check_document_status
                    check_document_status(doctype, docs[0].name)
            break