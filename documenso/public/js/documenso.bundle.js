// Copyright (c) 2024, Your Company and contributors
// For license information, please see license.txt

frappe.call({
    method: "frappe.client.get",
    args: {
        doctype: "Documenso Settings",
        name: "Documenso Settings"
    },
    callback: function(response) {
        let doctype_list = response.message["doctypes"] || [];
        doctype_list.forEach((element) => {
            let doctype_name = element.doctype_name;
            frappe.ui.form.on(doctype_name, {
                refresh: function(frm) {
                    // Only show buttons if not in new document
                    if (!frm.is_new()) {
                        // Request Sign button
                        frm.add_custom_button("Request Sign", function() {
                            frappe.confirm(
                                'Are you sure you want to send this document for signing?',
                                () => {
                                    frappe.call({
                                        method: "documenso.documenso.api.request_sign.send_signing_request",
                                        args: {
                                            docname: frm.doc.name,
                                            doctype: frm.doc.doctype
                                        },
                                        callback: (response) => {
                                            frm.reload_doc();
                                        }
                                    });
                                }
                            );
                        });
                        
                        // Fetch Signatories button
                        frm.add_custom_button("Fetch Signatories", function() {
                            frappe.confirm(
                                "This will clear the current Signatory Details. Are you sure you want to proceed?",
                                function() {
                                    frappe.call({
                                        method: "documenso.documenso.api.request_sign.fetch_authorized_signatories",
                                        args: {
                                            docname: frm.doc.name,
                                            doctype: frm.doc.doctype
                                        },
                                        callback: (response) => {
                                            frm.reload_doc();
                                            frappe.msgprint("Default signatory details fetched successfully");
                                        }
                                    });
                                }
                            );
                        });
                        
                        // Check Status button (only if document has been sent)
                        if (frm.doc.document_id) {
                            frm.add_custom_button("Check Status", function() {
                                frappe.call({
                                    method: "documenso.documenso.api.request_sign.check_signing_status",
                                    args: {
                                        docname: frm.doc.name,
                                        doctype: frm.doc.doctype
                                    },
                                    callback: (response) => {
                                        frm.reload_doc();
                                    }
                                });
                            });
                            
                            // Send Reminder button
                            frm.add_custom_button("Send Reminder", function() {
                                frappe.confirm(
                                    'Send reminder to all pending signatories?',
                                    () => {
                                        frappe.call({
                                            method: "documenso.documenso.api.documenso.send_reminder",
                                            args: {
                                                docname: frm.doc.name,
                                                doctype: frm.doc.doctype
                                            },
                                            callback: (response) => {
                                                frappe.msgprint("Reminders sent");
                                            }
                                        });
                                    }
                                );
                            });
                        }
                    }
                    
                    // Style the signatory detail table
                    if (frm.fields_dict['signatory_detail']) {
                        // Make the table read-only after signing request is sent
                        if (frm.doc.document_id) {
                            frm.fields_dict['signatory_detail'].grid.wrapper.find('.grid-add-row').hide();
                            frm.fields_dict['signatory_detail'].grid.static_rows = true;
                        }
                    }
                    
                    // Show status indicators
                    if (frm.doc.signatory_detail) {
                        frm.doc.signatory_detail.forEach(row => {
                            if (row.signature_status === 'Signed') {
                                frm.set_df_property('signatory_detail', 'read_only', 1);
                            }
                        });
                    }
                }
            });
            
            // Add events for signatory detail table
            frappe.ui.form.on('Documenso Signatory Detail', {
                before_signatory_detail_remove: function(frm, cdt, cdn) {
                    // Prevent deletion if document has been sent
                    if (frm.doc.document_id) {
                        frappe.msgprint(__('Cannot modify signatories after document has been sent for signing'));
                        return false;
                    }
                }
            });
        });
    }
});

// Global helper function for displaying signing status
frappe.documenso = {
    get_status_indicator: function(status) {
        const status_map = {
            'Not Initiated': { color: 'gray', label: 'Not Initiated' },
            'Pending': { color: 'orange', label: 'Pending' },
            'Viewed': { color: 'blue', label: 'Viewed' },
            'Signed': { color: 'green', label: 'Signed' },
            'Declined': { color: 'red', label: 'Declined' },
            'Failed': { color: 'red', label: 'Failed' }
        };
        
        return status_map[status] || { color: 'gray', label: status };
    }
};
