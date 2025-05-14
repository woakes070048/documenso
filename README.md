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
```

## Configuration

1. Go to Documenso Settings
2. Add your API credentials (cloud or self-hosted)
3. Configure authorized signatories
4. Enable doctypes for signing
5. Set up print formats

## Usage

1. Open any enabled document
2. Click "Fetch Signatories" to populate default signers
3. Click "Request Sign" to send for signing
4. Track signature progress
5. Signed documents are automatically attached

## API Configuration

For cloud deployment:
- API URL: `https://api.documenso.com`
- Get your API key from: https://app.documenso.com/settings/api

For self-hosted:
- API URL: Your instance URL (e.g., `https://your-domain.com`)
- API key from your self-hosted instance

## License

MIT
