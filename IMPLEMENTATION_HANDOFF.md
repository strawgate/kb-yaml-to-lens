# Implementation Handoff for @copilot

## Summary

I've completed the planning phase for the workflow automation requested in issue #106. Since I cannot modify workflow files (only @copilot has those permissions), I'm handing off the implementation with complete specifications.

## What I've Done

✅ **Created comprehensive plan**: `WORKFLOW_AUTOMATION_PLAN.md`
- Full workflow specifications with complete YAML
- Concurrency strategy to prevent infinite loops
- Safety mechanisms and monitoring guidance
- Success metrics and rollback plans

## What Needs Implementation

@copilot - Please implement these two workflow files exactly as specified in `WORKFLOW_AUTOMATION_PLAN.md`:

### 1. `.github/workflows/claude-on-coderabbit-feedback.yml`

**Purpose**: Automatically respond to CodeRabbit reviews with code fixes

**Key sections to copy from plan**:
- Trigger: `pull_request_review: types: [submitted]`
- Condition: Only for `coderabbitai[bot]` reviews
- Concurrency: `group: claude-coderabbit-${{ github.event.pull_request.number }}`
- Prompt: Complete prompt is in the plan (search for "Set CodeRabbit response prompt")
- Complete YAML specification is in the plan under "Workflow Structure"

### 2. `.github/workflows/claude-on-test-failure.yml`

**Purpose**: Analyze test failures and suggest fixes

**Key sections to copy from plan**:
- Trigger: `workflow_run` on "Run Tests" completion
- Condition: Only for PR test failures
- Concurrency: `group: claude-test-failure-${{ github.event.workflow_run.head_branch }}`
- Prompt: Complete prompt is in the plan (search for "Set analysis prompt")
- Complete YAML specification is in the plan under "Workflow Structure"

## Implementation Steps

1. **Copy YAML from plan**: Both complete workflow files are in `WORKFLOW_AUTOMATION_PLAN.md`
2. **Create workflow files**:
   - `.github/workflows/claude-on-coderabbit-feedback.yml`
   - `.github/workflows/claude-on-test-failure.yml`
3. **Optional: Update AGENTS.md**: Add documentation about the new workflows
4. **Test**:
   - CodeRabbit workflow: Create a draft PR, have CodeRabbit review it, verify Claude responds
   - Test failure workflow: Create a PR with a failing test, verify Claude analyzes it

## Safety Mechanisms Already Included

✅ Per-PR/branch concurrency controls
✅ `cancel-in-progress: true` prevents queue buildup
✅ Bot commit filtering (CodeRabbit ignores bot commits)
✅ Single action per trigger
✅ No cross-workflow triggering
✅ 30-minute timeout (add to both workflows)

## Verification Checklist

After implementation, verify:
- [ ] CodeRabbit workflow only triggers on coderabbitai[bot] reviews
- [ ] Test failure workflow only triggers on PR test failures (not main branch)
- [ ] Concurrency groups work (check Actions dashboard)
- [ ] No infinite loops observed
- [ ] Comments/changes are appropriate

## Rollback If Needed

If issues arise:
```yaml
jobs:
  job-name:
    if: false  # Temporarily disable
```

## Questions?

The complete plan with rationale, alternatives considered, and detailed specifications is in `WORKFLOW_AUTOMATION_PLAN.md`. Everything needed for implementation is there.

---

**Ready for @copilot to implement! 🚀**
