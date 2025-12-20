# Instructions for GitHub Copilot: Implementing GHCR Workflow

This document provides complete instructions for GitHub Copilot to implement the GHCR-based Kibana fixture generator workflow.

## Context

The Kibana fixture generator currently requires building a Docker image that bootstraps Kibana from source, which takes 15-30 minutes. This is problematic for CI/CD pipelines. The solution is to:

1. Pre-build Docker images with bootstrapped Kibana
2. Publish them to GitHub Container Registry (GHCR)
3. Use these cached images in CI and local development
4. Automate weekly builds to keep images up-to-date

## Files Created by Claude

Claude has created the following files that need to be integrated:

1. **`fixture-generator/Dockerfile.ghcr`** - Optimized Dockerfile for GHCR builds
2. **`fixture-generator/docker-compose.ghcr.yml`** - Docker Compose config using GHCR images
3. **`fixture-generator/GHCR.md`** - Complete documentation for GHCR usage
4. **`.github/workflows/build-kibana-fixture-image.yml.template`** - Template for the workflow

## Tasks for GitHub Copilot

### Task 1: Create GitHub Actions Workflow

**File to create:** `.github/workflows/build-kibana-fixture-image.yml`

**Source:** Use the content from `.github/workflows/build-kibana-fixture-image.yml.template` (already created by Claude)

**Instructions:**
1. Copy the template file content
2. Create the actual workflow file at `.github/workflows/build-kibana-fixture-image.yml`
3. Ensure all syntax is valid for GitHub Actions
4. Verify permissions are correct (needs `packages: write` for GHCR)

**Key features to verify:**
- Workflow dispatch with inputs for `kibana_version` and `force_rebuild`
- Scheduled run (weekly on Mondays)
- Trigger on push to main when Dockerfile changes
- Check if image exists before building (skip if exists and not force rebuild)
- Build and push to GHCR with proper tagging
- Test image after build to verify LensConfigBuilder is available

### Task 2: Verify Docker Files

**Files to verify:**
- `fixture-generator/Dockerfile.ghcr` (created by Claude)
- `fixture-generator/docker-compose.ghcr.yml` (created by Claude)

**Verification checklist:**
- [ ] Dockerfile.ghcr has correct GHCR labels
- [ ] Dockerfile.ghcr bootstraps Kibana correctly
- [ ] docker-compose.ghcr.yml references correct GHCR image path
- [ ] docker-compose.ghcr.yml has local-build profile as fallback

### Task 3: Update Documentation

**Files already updated by Claude:**
- `fixture-generator/README.md` - Updated Quick Start section
- `fixture-generator/GHCR.md` - New comprehensive GHCR guide

**Additional documentation to verify:**
- [ ] README.md clearly explains GHCR option
- [ ] GHCR.md covers all use cases
- [ ] Links between documentation files work

### Task 4: Test the Complete Workflow

**Manual testing steps:**

1. **Test workflow dispatch:**
   ```bash
   # Go to GitHub Actions → "Build Kibana Fixture Generator Image"
   # Click "Run workflow"
   # Select kibana_version: "main"
   # Leave force_rebuild: false
   # Click "Run workflow"
   # Verify build completes successfully
   ```

2. **Test GHCR image usage:**
   ```bash
   cd fixture-generator
   
   # Pull image from GHCR
   docker pull ghcr.io/strawgate/kb-yaml-to-lens/kibana-fixture-generator:main
   
   # Test with docker-compose
   docker-compose -f docker-compose.ghcr.yml run generator node examples/metric-basic.js
   
   # Verify output is generated
   ls -la output/
   ```

3. **Test image verification:**
   ```bash
   # Verify LensConfigBuilder is available
   docker run --rm ghcr.io/strawgate/kb-yaml-to-lens/kibana-fixture-generator:main \
     node -e "require('@kbn/lens-embeddable-utils/config_builder'); console.log('✓ Verified')"
   ```

4. **Test scheduled workflow logic:**
   - Check that workflow is scheduled for Mondays at 2 AM UTC
   - Verify it will skip building if image exists
   - Verify force_rebuild overrides the check

## Expected Outcomes

After implementation:

1. **Workflow available:** GitHub Actions shows "Build Kibana Fixture Generator Image" workflow
2. **Manual trigger works:** Can trigger workflow with custom Kibana versions
3. **Images in GHCR:** Built images appear at `ghcr.io/strawgate/kb-yaml-to-lens/kibana-fixture-generator`
4. **Fast fixture generation:** Using GHCR images avoids 15-30 min build time
5. **Weekly updates:** Latest Kibana version automatically built weekly
6. **Documentation complete:** Clear instructions for all use cases

## Common Issues and Solutions

### Issue 1: Permission Denied for GHCR

**Solution:** Ensure workflow has `packages: write` permission:

```yaml
permissions:
  contents: read
  packages: write
```

### Issue 2: Docker Buildx Not Available

**Solution:** Add buildx setup step:

```yaml
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3
```

### Issue 3: Image Check Fails

**Solution:** Use proper Docker manifest inspect command:

```bash
docker manifest inspect $IMAGE_NAME > /dev/null 2>&1
```

### Issue 4: Build Timeout

**Solution:** GitHub Actions provides sufficient resources, but verify:
- Kibana version is valid
- Node version matches Kibana requirement
- Bootstrap command includes `--allow-root`

## Integration with Existing CI

The fixture generator can now be used in existing CI pipelines:

```yaml
# Example: Use in test workflow
jobs:
  test-with-fixtures:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Generate test fixtures
        run: |
          cd fixture-generator
          docker-compose -f docker-compose.ghcr.yml run generator
      
      - name: Run Python tests with fixtures
        run: |
          uv run pytest test/
```

## Rollout Plan

1. **Phase 1: Build initial image**
   - Manually trigger workflow to build `main` version
   - Verify image builds successfully
   - Test image locally

2. **Phase 2: Update developer documentation**
   - Ensure GHCR.md is linked from main README
   - Add GHCR option to CONTRIBUTING.md if applicable
   - Update any CI documentation

3. **Phase 3: Switch default to GHCR**
   - Update main docker-compose.yml to use GHCR by default
   - Keep local build as fallback option
   - Monitor for issues

4. **Phase 4: Enable scheduled builds**
   - Verify weekly scheduled builds work
   - Monitor GHCR for image accumulation
   - Set retention policy for old images

## Success Criteria

- [ ] Workflow file created and valid
- [ ] Manual workflow dispatch builds image successfully
- [ ] Image appears in GHCR
- [ ] Image works for fixture generation
- [ ] LensConfigBuilder is available in image
- [ ] Documentation is complete and accurate
- [ ] Scheduled builds are configured
- [ ] Force rebuild option works
- [ ] Image size is reasonable (~8-10GB)
- [ ] CI timeout issues are resolved

## Reference Links

- GitHub Container Registry: https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry
- Docker build-push-action: https://github.com/docker/build-push-action
- GitHub Actions schedule: https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#schedule
- Docker manifest inspect: https://docs.docker.com/engine/reference/commandline/manifest_inspect/
