# Creating GitHub Issues
You have permission to create GitHub issues using the `gh issue create` command.

To create an issue:
```bash
gh issue create \
  --title "Issue title" \
  --body "Issue description" \
  --assignee username \
  --label label1 \
  --label label2
```

Example:
```bash
gh issue create \
  --title "Add support for new chart type" \
  --body "We need to add support for the new chart type..." \
  --label enhancement
```

When creating issues:
1. Use clear, descriptive titles
2. Provide detailed descriptions with context
3. Add appropriate labels (bug, enhancement, documentation, etc.)
4. Reference related issues or PRs when relevant
5. Include code snippets or examples when applicable
