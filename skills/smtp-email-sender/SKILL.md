---
name: smtp-email-sender
description: Send emails via SMTP with support for plain text, HTML, and attachments. Configurable through environment variables or direct parameters.
version: 1.0.0
author: clone
tags:
  - email
  - smtp
  - communication
allowed_tools:
  - code_execution_tool
license: MIT
compatibility: clone
---

# smtp-email-sender

## Overview
This skill provides reliable email sending capabilities using Python's smtplib. It is designed to be flexible and secure, supporting various SMTP configurations.

## Features
- Plain text and HTML email bodies
- File attachments
- CC, BCC, and Reply-To headers
- TLS and SSL encryption
- Configuration via environment variables or function parameters
- Detailed error reporting

## Configuration
Set the following environment variables (or pass them as parameters):

- `SMTP_HOST`: SMTP server hostname (required)
- `SMTP_PORT`: Port number (default: 587)
- `SMTP_USERNAME`: Authentication username (required)
- `SMTP_PASSWORD`: Authentication password/app password (required)
- `SMTP_USE_TLS`: `true` for TLS, `false` for SSL/none (default: true)
- `DEFAULT_SENDER_EMAIL`: Default From address (required)

## Usage

Call the skill by using the code execution tool to run the send_email.py script, or import it as a module:

```python
from scripts.send_email import send_email

result = send_email(
    to_emails=['recipient@example.com'],
    subject='Hello',
    body='Plain text message',
    html_body='<p>HTML version</p>',  # optional
    attachments=['/path/to/file.pdf'],  # optional list
    cc=['copy@example.com'],  # optional
    bcc=['hidden@example.com'],  # optional
    reply_to='reply@example.com',  # optional
    # Optional overrides for environment config:
    # smtp_host='smtp.example.com',
    # smtp_port=587,
    # smtp_username='user',
    # smtp_password='pass',
    # use_tls=True,
    # from_email='sender@example.com'
)

print(result)
```

The function returns a dictionary with keys: `success` (bool) and `message` (str). On success, it may also include `recipients` and `subject`.

## Standalone Execution
You can also run the script directly from the command line for testing:

```bash
python scripts/send_email.py <to_email> <subject> <body> [html_body]
```

## Security Notes
- Never commit credentials to version control
- Use app-specific passwords (e.g., Gmail App Passwords)
- Enable two-factor authentication
- Store secrets in environment variables or a secure secrets manager

## Files
- `scripts/send_email.py` - Main implementation
- `SKILL.md` - This documentation
