app_name = "documenso"
app_title = "Documenso"
app_publisher = "Your Company"
app_description = "Integrating Documenso in ERPNext"
app_icon = "octicon octicon-file-code"
app_color = "blue"
app_email = "your-email@example.com"
app_license = "MIT"
app_version = "0.0.1"

# Includes in <head>
app_include_js = "/assets/documenso/js/documenso.bundle.js"

# Scheduled Tasks
scheduler_events = {
    "daily": [
        "documenso.documenso.utils.py.scheduler.check_pending_signatures"
    ],
    "hourly": [
        "documenso.documenso.utils.py.scheduler.sync_document_status"
    ]
}

required_apps = ["frappe", "erpnext"]

# Webhooks
webhook_events = {
    "on_method": "documenso.documenso.api.webhook.documenso_webhook"
}

# Website Route (for webhook endpoint)
website_route_rules = [
    {
        "from_route": "/api/webhooks/documenso",
        "to_route": "documenso.documenso.api.webhook.documenso_webhook"
    }
]