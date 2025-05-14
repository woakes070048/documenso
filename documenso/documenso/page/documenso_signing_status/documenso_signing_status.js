frappe.pages['documenso_signing_status'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Documenso Signing Status',
        single_column: true
    });

    // Add refresh button
    page.add_button('Refresh', function() {
        frappe.show_alert('Refreshing status...', 5);
        // Refresh logic here
    });

    // Create page content
    $(wrapper).find('.page-content').html(`
        <div class="documenso-status-page">
            <h3>Document Signing Status</h3>
            <p>Monitor the status of documents sent for signing.</p>
            <div id="status-container"></div>
        </div>
    `);
}
