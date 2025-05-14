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
                            frappe.call({
                                method: "documenso.documenso.api.request_sign.send_email_request",
                                args: {
                                    docname: frm.doc.name,
                                    doctype: frm.doc.doctype
                                },
                                callback: (response) => {
                                    frappe.msgprint("Document sent for signing with smart field placement");
                                    frm.reload_doc();
                                }
                            });
                        });
                        
                        // Fetch Sign info button
                        frm.add_custom_button("Fetch Sign info", function() {
                            frappe.confirm(
                                "This will clear the current Signatory Details. Are you sure you want to proceed?",
                                function() {
                                    frappe.call({
                                        method: "documenso.documenso.api.documenso.fetch_documenso_authorized_signatory",
                                        args: {
                                            docname: frm.doc.name,
                                            doctype: frm.doc.doctype
                                        },
                                        callback: (response) => {
                                            frappe.msgprint("Default Signatory details fetched successfully");
                                            frm.reload_doc();
                                        }
                                    });
                                }
                            );
                        });
                        
                        // Check Status button (only if document has been sent)
                        if (frm.doc.document_id) {
                            frm.add_custom_button("Check Status", function() {
                                frappe.call({
                                    method: "documenso.documenso.api.documenso.check_document_status",
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
                        
                        // Add placeholder info
                        if (frm.fields_dict['signatory_detail']) {
                            frm.set_df_property('signatory_detail', 'description', 
                                'Add {{signature_1}}, {{signature_2}} etc. in your print format for automatic signature placement');
                        }
                    }
                }
            });
            
            // Add events for signatory detail table
            frappe.ui.form.on('Documenso Signatory Detail', {
                place_sign: function(frm, cdt, cdn) {
                    var row = locals[cdt][cdn];
                    if (row.sign_position == "Customize") {
                        frappe.set_route('documenso-template-builder');
                    }
                }
            });
        });
    }
});