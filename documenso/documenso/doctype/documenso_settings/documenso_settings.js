// Copyright (c) 2024, Your Company and contributors
// For license information, please see license.txt

frappe.ui.form.on('Documenso Settings', {
    refresh: function(frm) {
        if (!frm.doc.__islocal) {
            frm.add_custom_button(__('Test Connection'), function() {
                frappe.call({
                    method: 'documenso.documenso.api.documenso.test_connection',
                    callback: function(r) {
                        if (r.message && r.message.success) {
                            frappe.msgprint(__('Connection successful!'));
                        } else {
                            frappe.msgprint(__('Connection failed. Please check your credentials.'));
                        }
                    }
                });
            });
        }
        
        // Add help text about placeholders
        frm.set_df_property('authorized_signatory', 'description', 
            'Add placeholders like {{signature_1}}, {{signature_2}} in your print formats. These will be automatically detected for signature placement.');
    },
    
    deployment_type: function(frm) {
        if (frm.doc.deployment_type === 'Cloud') {
            frm.set_value('api_url', 'https://app.documenso.com');
        }
    }
});

frappe.ui.form.on("Documenso Authorized Signatory", {
    signatory_type: function(frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        
        if (row.signatory_type === "Contact") {
            frappe.model.set_value(cdt, cdn, {
                "signatory": "",
                "signatory_name": "Will be fetched from contact",
                "signatory_email": "Will be fetched from contact"
            });
        } else if (row.signatory_type === "Document Owner") {
            frappe.model.set_value(cdt, cdn, {
                "signatory": "",
                "signatory_name": "Document Owner",
                "signatory_email": "Will be fetched from document"
            });
        }
    },
    
    placeholder: function(frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        if (!row.placeholder) {
            // Auto-generate placeholder based on order
            var order = row.signing_order || 1;
            frappe.model.set_value(cdt, cdn, "placeholder", `{{signature_${order}}}`);
        }
    }
});