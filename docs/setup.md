# MySQL AI Agent - Setup Guide

## 1. MySQL Requirements

The application connects to an existing MySQL server running on the Ubuntu host.

The application must never use the MySQL root account or an administrator account.

A dedicated, read-only MySQL account is required.

## 2. Create the Application Database User

Connect to MySQL as an administrator:

```bash
mysql -u root -p
```

Create a dedicated user:

```sql
CREATE USER 'ai_agent'@'127.0.0.1'
IDENTIFIED BY 'REPLACE_WITH_A_STRONG_PASSWORD';
```

Grant read-only access to the application database:

```sql
GRANT SELECT ON `REPLACE_WITH_DATABASE_NAME`.*
TO 'ai_agent'@'127.0.0.1';
```

Verify the permissions:

```sql
SHOW GRANTS FOR 'ai_agent'@'127.0.0.1';
```

The account should have SELECT permission only.

## 3. Application Credentials

Database credentials belong in the project's `.env` file.

Never commit `.env` or place real credentials in this documentation.

## 4. Network Configuration

Local development uses Docker host networking.

The application connects to MySQL using:

- Host: 127.0.0.1
- Port: 3306

MySQL remains installed and running on the Ubuntu host.

## 5. Verify Database Access

Test the dedicated account:

```bash
mysql -h 127.0.0.1 -P 3306 -u ai_agent -p radius
```

Verify the selected database:

```sql
SELECT DATABASE();
```

List available tables:

```sql
SHOW TABLES;
```

Verify account permissions:

```sql
SHOW GRANTS FOR 'ai_agent'@'127.0.0.1';
```

Expected permissions:

- USAGE on global scope.
- SELECT on `radius` only.

The database account must not have INSERT, UPDATE, DELETE, or administrative privileges.

## 6. Docker and Python Database Configuration

### Environment Variables

The application uses a `.env` file containing:

- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`

The `.env` file must never be committed to version control or copied into the Docker image.

### Docker Networking

Local development uses Docker host networking:

```yaml
network_mode: host
```

The application connects to the existing Ubuntu MySQL server using:

- Host: `127.0.0.1`
- Port: `3306`

MySQL remains on the Ubuntu host.

### Verify the Application Connection

Build and run the application:

```bash
sudo docker compose up --build
```

The application should successfully report:

- Database: `radius`
- Account: `ai_agent@127.0.0.1`

The connection must be closed after use.