# Troubleshooting Guide

This guide addresses common issues you might encounter when using the Dashboard Compiler CLI and VS Code extension.

## CLI & Compilation Issues

### Connection Refused

**Error:** `Connection refused` or `Failed to connect to host`

**Possible Causes:**

- Kibana is not running.
- The Kibana URL is incorrect.
- Firewall rules are blocking the connection.

**Solutions:**

1. **Verify Kibana is running:**

   ```bash
   curl http://localhost:5601/api/status
   ```

2. **Check the Kibana URL:**
   Ensure you are using the correct protocol (`http` vs `https`) and port.

   ```bash
   kb-dashboard compile --upload --kibana-url http://localhost:5601
   ```

3. **Check Network:**
   If using Docker, ensure you are using `http://host.docker.internal:5601` to access the host's localhost.

### Authentication Failed

**Error:** `401 Unauthorized` or `Authentication failed`

**Possible Causes:**

- Incorrect username or password.
- Expired or invalid API key.
- User lacks necessary permissions.

**Solutions:**

1. **Verify Credentials:**
   Double-check your username and password.

   ```bash
   # Using basic auth
   export KIBANA_USERNAME=elastic
   export KIBANA_PASSWORD=changeme
   ```

2. **Check API Key:**
   Ensure the API key was copied correctly and hasn't expired.

   ```bash
   # Using API key
   export KIBANA_API_KEY="your-base64-encoded-key"
   ```

3. **Check Permissions:**
   The user needs permissions to write to Saved Objects in Kibana.

### Upload Errors

**Error:** `400 Bad Request` or specific validation errors during upload

**Possible Causes:**

- The compiled NDJSON is invalid (rare).
- You are trying to overwrite a protected object.
- Kibana version incompatibility.

**Solutions:**

1. **Check Logs:**
   Look at the Kibana server logs for detailed error messages.
2. **Use `--no-overwrite`:**
   If you want to preserve existing objects, use the `--no-overwrite` flag.

   ```bash
   kb-dashboard compile --upload --no-overwrite
   ```

3. **Validate Input:**
   Ensure your YAML input is valid. Run the compiler without uploading to check for local errors.

   ```bash
   kb-dashboard compile
   ```

### "Port Already In Use" (VS Code Extension)

**Error:** `Error: listen EADDRINUSE: address already in use :::5601` (or similar)

**Possible Causes:**

- Another instance of the extension or a local Kibana server is using the port.

**Solutions:**

1. **Kill the Process:**
   Find the process using the port and kill it.

   ```bash
   lsof -i :5601
   kill -9 <PID>
   ```

## Common YAML Errors

### "Field is required"

**Error:** `pydantic_core.ValidationError: 1 validation error for Dashboard ... Field required [type=missing, ...]`

**Solution:**
Check your YAML indentation and ensure all required fields are present. For example, a dashboard must have a `panels` list.

### "Invalid Panel Type"

**Error:** `Input should be a valid dictionary or instance of ...`

**Solution:**
Ensure you are using a supported panel type (e.g., `lens`, `markdown`, `text`, `visualization`). Check spelling and indentation.

## Getting Help

If you continue to experience issues:

1. Check the [GitHub Issues](https://github.com/strawgate/kb-yaml-to-lens/issues) to see if others have reported the same problem.
2. Enable verbose logging (if available) to get more details.
3. Open a new issue with your YAML configuration (sanitized) and the error message.
