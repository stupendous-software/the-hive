#!/usr/bin/env python3
"""
SMTP Email Sender Script

This script provides a function to send emails via SMTP with support for:
- Plain text and HTML content
- File attachments
- CC, BCC, Reply-To headers
- TLS/SSL encryption
- Custom SMTP configuration via parameters or environment variables
"""

import os
import ssl
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import List, Optional, Dict, Any


def _get_smtp_config() -> Dict[str, Any]:
    """Read SMTP configuration from environment variables."""
    return {
        'host': os.getenv('SMTP_HOST'),
        'port': int(os.getenv('SMTP_PORT', '587')) if os.getenv('SMTP_PORT') else 587,
        'username': os.getenv('SMTP_USERNAME'),
        'password': os.getenv('SMTP_PASSWORD'),
        'use_tls': os.getenv('SMTP_USE_TLS', 'true').lower() == 'true',
        'default_sender': os.getenv('DEFAULT_SENDER_EMAIL')
    }


def send_email(
    to_emails: List[str],
    subject: str,
    body: str,
    html_body: Optional[str] = None,
    attachments: List[str] = None,
    cc: List[str] = None,
    bcc: List[str] = None,
    reply_to: Optional[str] = None,
    smtp_host: Optional[str] = None,
    smtp_port: Optional[int] = None,
    smtp_username: Optional[str] = None,
    smtp_password: Optional[str] = None,
    use_tls: Optional[bool] = None,
    from_email: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send an email via SMTP.
    
    Parameters:
        to_emails: List of recipient email addresses
        subject: Email subject
        body: Plain text body
        html_body: Optional HTML body (if provided, creates multipart/alternative)
        attachments: List of file paths to attach
        cc: List of CC recipients
        bcc: List of BCC recipients
        reply_to: Reply-To header address
        smtp_host: SMTP server hostname (overrides env)
        smtp_port: SMTP port (overrides env)
        smtp_username: SMTP username (overrides env)
        smtp_password: SMTP password (overrides env)
        use_tls: Use TLS (overrides env)
        from_email: From email address (overrides env)
    
    Returns:
        Dict with keys: success (bool), message (str)
    """
    
    # Merge with environment configuration
    env_config = _get_smtp_config()
    host = smtp_host or env_config['host']
    port = smtp_port or env_config['port']
    username = smtp_username if smtp_username is not None else env_config['username']
    password = smtp_password if smtp_password is not None else env_config['password']
    default_sender = from_email or env_config['default_sender']
    
    if use_tls is None:
        use_tls = env_config['use_tls']
    
    # Validate required fields
    if not host:
        return {'success': False, 'message': 'SMTP host not configured. Set SMTP_HOST environment variable or provide smtp_host parameter.'}
    if not default_sender:
        return {'success': False, 'message': 'From email not configured. Set DEFAULT_SENDER_EMAIL environment variable or provide from_email parameter.'}
    
    # Only require credentials for ports that typically need authentication (587 TLS, 465 SSL
    # or if use_tls is explicitly enabled). Port 25 often allows unauthenticated sending.
    auth_required = (port in [465, 587]) or (use_tls and port != 25)
    if auth_required and (username is None or password is None or username == '' or password == ''):
        return {'success': False, 'message': f'SMTP server on port {port} requires authentication. Set SMTP_USERNAME and SMTP_PASSWORD environment variables or provide parameters.'}
    
    # Build message
    if html_body:
        msg = MIMEMultipart('alternative')
        # Plain text part
        text_part = MIMEText(body, 'plain', 'utf-8')
        msg.attach(text_part)
        # HTML part
        html_part = MIMEText(html_body, 'html', 'utf-8')
        msg.attach(html_part)
    else:
        msg = MIMEText(body, 'plain', 'utf-8')
    
    # Set headers
    msg['Subject'] = subject
    msg['From'] = default_sender
    msg['To'] = ', '.join(to_emails)
    if cc:
        msg['Cc'] = ', '.join(cc)
    if reply_to:
        msg['Reply-To'] = reply_to
    
    # Handle attachments
    if attachments:
        # Convert to MIMEMultipart if we haven't already (no html_body)
        if not html_body:
            msg = MIMEMultipart()
            # Re-attach the original text body
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            # Reset headers that got cleared
            msg['Subject'] = subject
            msg['From'] = default_sender
            msg['To'] = ', '.join(to_emails)
            if cc:
                msg['Cc'] = ', '.join(cc)
            if reply_to:
                msg['Reply-To'] = reply_to
        
        for file_path in attachments:
            path = Path(file_path)
            if not path.exists():
                return {'success': False, 'message': f'Attachment not found: {file_path}'}
            
            with open(path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename={path.name}',
            )
            msg.attach(part)
    
    # Collect all recipients for SMTP sendmail
    all_recipients = to_emails.copy()
    if cc:
        all_recipients.extend(cc)
    if bcc:
        all_recipients.extend(bcc)
    
    try:
        # Connect to SMTP server
        if use_tls and port == 587:
            server = smtplib.SMTP(host, port)
            server.starttls(context=ssl.create_default_context())
        elif not use_tls and port == 465:
            server = smtplib.SMTP_SSL(host, port, context=ssl.create_default_context())
        else:
            server = smtplib.SMTP(host, port)
            if use_tls:
                server.starttls(context=ssl.create_default_context())
        
        # Only login if we have credentials
        if auth_required and username and password:
            server.login(username, password)
        
        server.sendmail(default_sender, all_recipients, msg.as_string())
        server.quit()
        
        return {
            'success': True,
            'message': f'Email sent successfully to {len(all_recipients)} recipient(s)',
            'recipients': all_recipients,
            'subject': subject
        }
    
    except smtplib.SMTPAuthenticationError as e:
        return {'success': False, 'message': f'SMTP authentication failed: {str(e)}'}
    except Exception as e:
        return {'success': False, 'message': f'Failed to send email: {str(e)}'}


if __name__ == '__main__':
    # Simple test when run directly
    import sys
    
    if len(sys.argv) < 4:
        print('Usage: send_email.py <to> <subject> <body> [html_body]')
        sys.exit(1)
    
    result = send_email(
        to_emails=[sys.argv[1]],
        subject=sys.argv[2],
        body=sys.argv[3],
        html_body=sys.argv[4] if len(sys.argv) > 4 else None
    )
    print(result)
