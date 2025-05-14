# Copyright (c) 2024, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from documenso.documenso.utils.py.create_custom_fields import make_custom_fields
from documenso.documenso.utils.py.delete_custom_fields import delete_custom_fields


class DocumensoSettings(Document):
    def validate(self):
        # Validate API URL format
        if self.api_url and not self.api_url.startswith(('http://', 'https://')):
            frappe.throw("API URL must start with http:// or https://")
        
        # Remove trailing slash from API URL
        if self.api_url and self.api_url.endswith('/'):
            self.api_url = self.api_url[:-1]
    
    def on_update(self):
        # Handle doctype custom fields
        old_doc = self.get_doc_before_save()
        if old_doc:
            old_doctype_names = {d.doctype_name for d in old_doc.doctypes or []}
            new_doctype_names = {d.doctype_name for d in self.doctypes or []}
            
            removed_doctypes = old_doctype_names - new_doctype_names
            added_doctypes = new_doctype_names - old_doctype_names
            
            # Remove custom fields from removed doctypes
            for doctype in removed_doctypes:
                delete_custom_fields(doctype, "Documenso")
            
            # Add custom fields to new doctypes
            for doctype in added_doctypes:
                make_custom_fields(doctype, "documenso")
