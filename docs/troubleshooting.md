# Troubleshooting

This guide addresses common issues you might encounter when using the Kibana Dashboard Compiler.

## Common Errors

### 1. `FileNotFoundError: No such file or directory: 'inputs'`

**Problem:**
The compiler cannot find the default input directory.

**Solution:**
Ensure you have created the `inputs` directory or specified the correct path using the `--input-dir` flag.

```bash
mkdir inputs
# Or specify a different directory
uv run kb-dashboard compile --input-dir my-dashboards
```

### 2. `ConnectionRefusedError` or `ClientConnectorError`

**Problem:**
The compiler cannot connect to Kibana to upload dashboards or take screenshots.

**Solution:**
- Ensure Kibana is running and accessible.
- Verify the `--kibana-url` is correct (default is `http://localhost:5601`).
- If running in Docker, you might need to use `http://host.docker.internal:5601` to access Kibana running on the host machine.

### 3. `ValueError: Unexpected response from Kibana (status 401)`

**Problem:**
Authentication failed when trying to upload dashboards or take screenshots.

**Solution:**
Provide valid credentials using command-line flags or environment variables:

- **Basic Auth:** `--kibana-username elastic --kibana-password changeme`
- **API Key:** `--kibana-api-key <your-api-key>`

### 4. `ValueError: Input should be a valid dictionary or instance of ...`

**Problem:**
Your YAML configuration has a syntax error or is missing required fields.

**Solution:**
- Check your YAML indentation.
- Verify that required fields (like `type` for certain panels) are present.
- Use a YAML validator to ensure the file is syntactically correct.

## Debugging

To get more detailed error messages, you can run the command with the `RUST_BACKTRACE=1` environment variable if you encounter low-level errors, though Python stack traces are usually sufficient.

For verbose output during execution, standard Python errors will be printed to stderr.

## Still Stuck?

If you're still having trouble:

1.  Check the [Issues](https://github.com/strawgate/kb-yaml-to-lens/issues) on GitHub.
2.  Review the [examples](examples/index.md) to compare with your configuration.
