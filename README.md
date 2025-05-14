# Documenso Integration for ERPNext

This app integrates Documenso digital signing capabilities into ERPNext. It allows you to electronically sign documents such as Invoices or Purchase Orders using Documenso's API.

## Features

- Configure Documenso credentials (self-hosted or cloud)
- Enable any doctype for e-signatures
- Manage authorized signatories
- Track signature status
- Email-based signing workflow
- Webhook support for real-time updates

## Installation

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO
bench --site <site-name> install-app documenso
bench --site <site-name> migrate
```

## Configuration

1. Go to Documenso Settings
2. Add your API credentials (cloud or self-hosted)
3. Configure authorized signatories
4. Enable doctypes for signing
5. Set up print formats

## API Configuration

For cloud deployment:
- API URL: `https://app.documenso.com`
- Get your API key from: https://app.documenso.com/settings/api-tokens

For self-hosted:
- API URL: Your instance URL (e.g., `https://your-domain.com`)
- API key from your self-hosted instance

Note: Do not include `/api/v1` in the URL - the app will add it automatically.

## Webhook Configuration

To receive real-time updates when documents are signed:

1. In your Documenso instance, set up webhooks to point to:
   - Cloud: `https://your-erpnext-domain.com/api/webhooks/documenso`
   - Self-hosted: `https://your-erpnext-domain.com/api/webhooks/documenso`

2. Configure the webhook secret in Documenso Settings

3. Enable the following webhook events in Documenso:
   - `document.completed`
   - `document.signed`
   - `recipient.signed`

## Usage

1. Open any enabled document
2. Click "Fetch Signatories" to populate default signers
3. Click "Request Sign" to send for signing
4. Track signature progress
5. Signed documents are automatically attached

## Troubleshooting

### Connection Issues
- Verify your API URL doesn't have trailing slashes
- Check API key is correct and has proper permissions
- For self-hosted, ensure your instance is accessible

### Webhook Issues
- Check webhook URL is accessible from Documenso
- Verify webhook secret matches in both systems
- Check server logs for webhook errors

## License

MIT