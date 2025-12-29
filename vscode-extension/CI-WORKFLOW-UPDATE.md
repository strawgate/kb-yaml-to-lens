# CI Workflow Update for E2E Tests

Due to GitHub App permissions, the CI workflow file couldn't be updated automatically. Please add the following job to `.github/workflows/test-vscode-extension.yml`:

## Add this job after the `test-typescript` job

```yaml
  test-e2e:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]

    steps:
    - name: Checkout repository
      uses: actions/checkout@v4

    - name: Set up Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '20'
        cache: 'npm'
        cache-dependency-path: vscode-extension/package-lock.json

    - name: Setup Python Environment
      uses: ./.github/actions/setup-python-env

    - name: Install dependencies
      working-directory: vscode-extension
      run: npm ci

    - name: Compile extension
      working-directory: vscode-extension
      run: npm run compile

    - name: Setup display (Linux)
      if: runner.os == 'Linux'
      run: |
        sudo apt-get update
        sudo apt-get install -y xvfb
        export DISPLAY=':99.0'
        Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &

    - name: Run E2E tests
      working-directory: vscode-extension
      run: npm run test:e2e
      env:
        DISPLAY: ':99.0'
```

## Where to add it

The complete workflow file should look like this:

```yaml
name: Test VSCode Extension

on:
  push:
    branches: [ main ]
    paths:
      - 'vscode-extension/**'
      - '.github/workflows/test-vscode-extension.yml'
  pull_request:
    branches: [ main ]
    paths:
      - 'vscode-extension/**'
      - '.github/workflows/test-vscode-extension.yml'

permissions:
  contents: read

jobs:
  test-python-scripts:
    # ... existing job ...

  test-typescript:
    # ... existing job ...

  test-e2e:
    # ... NEW JOB (paste the code above) ...
```

## Notes

- The e2e tests will run on all three major platforms (Linux, Windows, macOS)
- Xvfb is used on Linux for headless display support
- The tests require both Node.js and Python environments
- Tests are only triggered when files in `vscode-extension/` change
