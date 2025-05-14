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
    },
    
    deployment_type: function(frm) {
        if (frm.doc.deployment_type === 'Cloud') {
            frm.set_value('api_url', 'https://api.documenso.com');
        }
    }
});
