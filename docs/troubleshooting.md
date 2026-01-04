# Troubleshooting Guide

This guide covers common issues you might encounter when using the YAML to Lens Dashboard Compiler.

## Common CLI Errors

### Directory 'inputs' does not exist

**Error Message:**

```text
Invalid value for '--input-dir': Directory 'inputs' does not exist.
```

**Cause:**
The CLI looks for an `inputs` directory by default, but it hasn't been created yet.

**Solution:**
Create the directory manually before running the command:

```bash
mkdir inputs
```

Or specify a different input directory using the `--input-dir` flag:

```bash
uv run kb-dashboard compile --input-dir my-dashboards
```

### Connection Refused

**Error Message:**

```text
aiohttp.client_exceptions.ClientConnectorError: Cannot connect to host localhost:5601 ssl:default [Connection refused]
```

**Cause:**
The compiler cannot reach the Kibana instance. This usually means:

1. Kibana is not running.
2. Kibana is running on a different host or port.
3. You are running inside Docker and trying to access `localhost`.

**Solution:**

- Ensure Kibana is up and running.
- If using Docker, use `host.docker.internal` instead of `localhost` to access the host machine's network.
- Check the `--kibana-url` parameter.

### SSL Certificate Verification Failed

**Error Message:**

```text
[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self signed certificate
```

**Cause:**
You are connecting to a Kibana instance that uses a self-signed SSL certificate (common in development environments).

**Solution:**
Use the `--kibana-no-ssl-verify` flag to disable certificate verification:

```bash
uv run kb-dashboard compile --upload --kibana-no-ssl-verify
```

### Authentication Failed (401)

**Error Message:**

```text
401 Unauthorized
```

**Cause:**
The username/password or API key provided is incorrect or missing.

**Solution:**

- Verify your credentials.
- Ensure you are providing either (`--kibana-username` AND `--kibana-password`) OR `--kibana-api-key`.
- Check environment variables `KIBANA_USERNAME`, `KIBANA_PASSWORD`, or `KIBANA_API_KEY`.

### Permission Denied (403)

**Error Message:**

```text
403 Forbidden
```

**Cause:**
The user or API key has insufficient permissions to create or modify Saved Objects in Kibana.

**Solution:**
Ensure the user has the `Stack Management > Saved Objects Management` privilege or the `kibana_admin` role.

## Compilation Issues

### Invalid YAML Syntax

**Error Message:**

```text
yaml.scanner.ScannerError: mapping values are not allowed here
```

**Cause:**
Your YAML file has syntax errors, such as incorrect indentation or improper use of colons.

**Solution:**
Use a YAML validator or check your file's indentation. Ensure that lists start with `-` and key-value pairs are separated by `:`.

### Missing Required Field

**Error Message:**

```text
pydantic_core._pydantic_core.ValidationError: 1 validation error for DashboardConfig
```

**Cause:**
A required field (e.g., `panels`, `title`) is missing from your configuration.

**Solution:**
Check the error details to identify the missing field. Refer to the [Dashboard Configuration](dashboard/dashboard.md) documentation for required fields.
