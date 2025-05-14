import frappe
from frappe import _
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def make_custom_fields(doctype, module=None):
    """Create custom fields for Documenso integration"""
    custom_fields = {
        doctype: [
            dict(
                fieldname="documenso_tab",
                label="Documenso",
                fieldtype="Tab Break",
                insert_after=frappe.get_meta(doctype).fields[-1].fieldname,
                print_hide=1,
                read_only=1,
                module=module,
            ),
            dict(
                fieldname="documenso_sb_1",
                fieldtype="Section Break",
                insert_after="documenso_tab",
                print_hide=1,
                module=module,
            ),
            dict(
                fieldname="signed_document",
                label="Signed Document",
                fieldtype="Attach",
                insert_after="documenso_sb_1",
                read_only=1,
                module=module,
            ),
            dict(
                fieldname="documenso_cb",
                fieldtype="Column Break",
                insert_after="signed_document",
                module=module,
            ),
            dict(
                fieldname="document_id",
                label="Document ID",
                fieldtype="Data",
                insert_after="documenso_cb",
                read_only=1,
                module=module,
            ),
            dict(
                fieldname="requested_print_format",
                label="Requested Print Format",
                fieldtype="Link",
                options="Print Format",
                insert_after="document_id",
                read_only=1,
                module=module,
            ),
            dict(
                fieldname="requested_letter_head",
                label="Requested Letter Head",
                fieldtype="Link",
                options="Letter Head",
                insert_after="requested_print_format",
                read_only=1,
                module=module,
            ),
            dict(
                fieldname="documenso_sb_2",
                fieldtype="Section Break",
                insert_after="requested_letter_head",
                print_hide=1,
                module=module,
            ),
            dict(
                fieldname="signatory_detail",
                label="Signatory Details",
                fieldtype="Table",
                insert_after="documenso_sb_2",
                options="Documenso Signatory Detail",
                read_only=1,
                module=module,
            ),
        ]
    }
    
    create_custom_fields(custom_fields)
