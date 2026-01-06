# Publishing the VS Code Extension

## Overview

The extension is automatically published to OpenVSX when a new version tag is pushed. This enables installation in Cursor and other VS Code forks that use the OpenVSX marketplace.

## Prerequisites (One-time Setup)

These steps must be completed by a repository maintainer before the automated publishing workflow can function:

### 1. Create Eclipse Foundation Account

1. Register at [Eclipse Foundation account portal](https://accounts.eclipse.org/user/register)
2. **Critical:** Fill in the GitHub Username field with the same GitHub account used to access open-vsx.org
3. Verify your email address

### 2. Configure OpenVSX Account

1. Visit [open-vsx.org](https://open-vsx.org/)
2. Log in via GitHub authentication (using the same account from step 1)
3. Navigate to profile settings
4. Complete Eclipse login process
5. Review and accept the Publisher Agreement

### 3. Generate Access Token

1. In profile settings, navigate to Access Tokens section
2. Generate a new token for GitHub Actions use
3. **Important:** Copy and save the token immediately (it won't be displayed again)

### 4. Create Namespace

```bash
npx ovsx create-namespace strawgate -p <your-token>
```

### 5. Configure GitHub Secret

1. Navigate to repository Settings → Secrets and variables → Actions
2. Create new repository secret: `OPEN_VSX_TOKEN`
3. Paste the access token from step 3

## Publishing a New Version

The extension is automatically published when a new version tag is pushed:

1. Update version in `package.json`:

   ```bash
   cd vscode-extension
   # Edit package.json to bump version
   ```

2. Commit changes:

   ```bash
   git add package.json
   git commit -m "chore: bump extension version to 0.1.1"
   ```

3. Create and push a tag:

   ```bash
   git tag -a vscode-v0.1.1 -m "VS Code Extension v0.1.1"
   git push origin vscode-v0.1.1
   ```

4. GitHub Actions will automatically build and publish to OpenVSX
   - Monitor the workflow at: [Actions](https://github.com/strawgate/kb-yaml-to-lens/actions)

## Manual Publishing (if needed)

If automated publishing fails or you need to publish manually:

```bash
cd vscode-extension
npm run package  # Creates .vsix file
npx ovsx publish -p $OPEN_VSX_TOKEN
```

## Verification

After publishing, verify the extension appears at: [OpenVSX Extension Page](https://open-vsx.org/extension/strawgate/kb-dashboard-compiler)

## Troubleshooting

### Publishing fails with authentication error

- Verify `OPEN_VSX_TOKEN` secret is set correctly in repository settings
- Ensure the token hasn't expired
- Check that the namespace `strawgate` exists in OpenVSX

### Extension not appearing in search

- Check that the extension was successfully published (view workflow logs)
- Wait a few minutes for OpenVSX indexing to complete
- Verify extension metadata in `package.json` is correct

## Future Enhancement

Consider publishing to both OpenVSX and VS Code Marketplace using the same workflow:

```yaml
- name: Publish to VS Code Marketplace
  uses: HaaLeo/publish-vscode-extension@v2
  with:
    pat: ${{ secrets.VSCODE_MARKETPLACE_TOKEN }}
    registryUrl: https://marketplace.visualstudio.com
    packagePath: ./vscode-extension
```

## Resources

- [OpenVSX Publishing Guide](https://github.com/eclipse/openvsx/wiki/Publishing-Extensions)
- [HaaLeo Publish Extension Action](https://github.com/marketplace/actions/publish-vs-code-extension)
- [OpenVSX Registry](https://open-vsx.org/)
