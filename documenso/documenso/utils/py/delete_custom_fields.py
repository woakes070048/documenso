import frappe


def delete_custom_fields(doctype, module=None):
    """Delete custom fields for Documenso integration"""
    field_list = frappe.get_all(
        "Custom Field",
        filters={"dt": doctype, "module": module},
        pluck="name"
    )
    
    for field in field_list:
        frappe.delete_doc("Custom Field", field)
    
    # Also delete fields by fieldname pattern
    documenso_fields = frappe.get_all(
        "Custom Field",
        filters={
            "dt": doctype,
            "fieldname": ["like", "documenso%"]
        },
        pluck="name"
    )
    
    for field in documenso_fields:
        frappe.delete_doc("Custom Field", field)
    
    # Delete specific fields
    specific_fields = [
        "signed_document",
        "document_id", 
        "requested_print_format",
        "requested_letter_head",
        "signatory_detail"
    ]
    
    for fieldname in specific_fields:
        fields = frappe.get_all(
            "Custom Field",
            filters={"dt": doctype, "fieldname": fieldname},
            pluck="name"
        )
        for field in fields:
            frappe.delete_doc("Custom Field", field)
