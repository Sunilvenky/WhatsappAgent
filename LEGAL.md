# WhatsApp Agent — Legal & Compliance Notes (PR1)

## Important:
- The Playwright connector (experimental) interacts with WhatsApp Web. Use it only with test accounts and non-production phone numbers. DO NOT use this connector in production or with real customers.
- For production deployments, migrate to the official WhatsApp Business Cloud API or an approved BSP.
- Keep all cryptographic secrets and API keys out of source control. Use .env files and secret stores.

## Required opt-in proof artifacts (persist at time of opt-in):
- timestamp (ISO8601)
- IP address of user
- source (page URL, campaign id)
- exact copy of consent / opt-in message
- user identifier (email/phone) and opt-in method (checkbox, reply keyword, form)

## STOP/UNSUBSCRIBE policy:
Any inbound message matching STOP/UNSUBSCRIBE (case-insensitive, trimmed) must:
- Immediately add the contact to suppression list.
- Cease outbound messages to that contact.
- Store an audit log entry with timestamp, source, and raw inbound message.
- Expose API to query suppressed status.

## Migration recommendation checklist for production:
- Business verification completed with Facebook/Meta.
- Phone number registered with WhatsApp Business API or BSP.
- Template messages approved (if sending notifications).
- Follow 24-hour messaging window rules for user-initiated replies.
- Implement proper opt-in proof retention and export capabilities.

## Experimental connector disclaimer:
- Playwright-based connectors may break if WhatsApp Web UI changes.
- Do not use Playwright connector with high-volume messaging.
- Use only on ephemeral test accounts for local dev and QA.