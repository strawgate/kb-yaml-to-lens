# GitHub Scripts Makefile
# Helper commands for GitHub workflow automation (used by Claude Code Action)

.PHONY: help get-review-threads resolve-review-thread get-latest-review check-latest-review get-comments-since minimize-outdated-comments check-repo-activity

help:
	@echo "GitHub Workflow Helper Commands:"
	@echo ""
	@echo "PR Review Management:"
	@echo "  get-review-threads <owner> <repo> <pr>           - Get open review threads"
	@echo "  resolve-review-thread <owner> <repo> <pr> <id>   - Resolve a review thread"
	@echo "  get-latest-review <owner> <repo> <pr>            - Get latest review"
	@echo "  check-latest-review <owner> <repo> <pr>          - Check if latest review is approved"
	@echo ""
	@echo "Comment Management:"
	@echo "  get-comments-since <owner> <repo> <issue> <time> - Get comments since timestamp"
	@echo "  minimize-outdated-comments <owner> <repo> <pr>   - Minimize outdated bot comments"
	@echo ""
	@echo "Repository:"
	@echo "  check-repo-activity <owner> <repo>               - Check recent repo activity"
	@echo ""

get-review-threads:
	@./gh-get-review-threads.sh $(filter-out $@,$(MAKECMDGOALS))

resolve-review-thread:
	@./gh-resolve-review-thread.sh $(filter-out $@,$(MAKECMDGOALS))

get-latest-review:
	@./gh-get-latest-review.sh $(filter-out $@,$(MAKECMDGOALS))

check-latest-review:
	@./gh-check-latest-review.sh $(filter-out $@,$(MAKECMDGOALS))

get-comments-since:
	@./gh-get-comments-since.sh $(filter-out $@,$(MAKECMDGOALS))

minimize-outdated-comments:
	@./gh-minimize-outdated-comments.sh $(filter-out $@,$(MAKECMDGOALS))

check-repo-activity:
	@./gh-check-repo-activity.sh $(filter-out $@,$(MAKECMDGOALS))

# Prevent make from trying to build targets passed as arguments
%:
	@:
