# Security concepts of goya-core
## Branch protection and code review
- The repository is protected with the CODEOWNERS model. 
    - Merging directly to master is possible only for Admins (but discouraged if more reviewers are available)
    - Every contributor can make a branch and pull request.
    - Only CODEOWNERS can approve a pull request. 
    - Every contributor can merge an approved pull request.

## Code security
- Static code scanning will be performed via Sonarcloud scanner.
- External dependency vulnerabilities will be scanned via Github DependaBot.

## Secrets/tokens security
- All tokens in production will be kept in an encrypted secure store (AWS Parameter Store).
- All tokens in test will be kept only locally and not be hardcoded or transferred to source code repository.

## Database Queries to avoid SQL injection
- All database queries are to be built using Django ORM model. No direct queries are to be used - EVER.

## Content requests are authorized
- All requests for content (parameters or pages) need to be authorized in the backend - by validating that the requesting users can receive back the information.

## Content Sanitization
- Content will be sanitized via libraries which eliminate malicious content before it reaches the content consumer.

## AWS Setup
The AWS setup needs to conform to the following criteria
- Minimal privileges
- Properly secured components (both services and database)

## To be defined
- Privacy
- Vulnerability Scanning
- Community Pentests
- Responsible Disclosure
