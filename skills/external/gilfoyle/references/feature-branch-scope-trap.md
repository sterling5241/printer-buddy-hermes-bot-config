# Feature branch scope mismatch, and resolving the branch to review

When asked to review a feature-named branch (e.g., `cc2-dsi`), verify the diff actually contains the claimed feature before reviewing it.

1. Check `git diff <merge-base>..HEAD`. If it is empty, the branch head may be the baseline or the work may be squashed. Use `git diff HEAD~1..HEAD` as the fallback scope.
2. Search the diff for the expected driver, binding, or algorithm name. If it is missing, report the mismatch as the first finding, not as a hidden assumption.
3. Review the actual changed code, not the branch name or ticket description.

This prevents a review of a feature that was never committed.

## Resolving a branch that no longer exists on the remote

- `git ls-remote origin | grep <name>` returns nothing: the branch was deleted or renamed.
- Query the PR list: `curl -s "https://api.github.com/repos/<owner>/<repo>/pulls?state=all&per_page=50"` and match `head.ref`. Note `base.ref` too; a PR based on `main` is not automatically on `nightly`.
- Fetch the PR head: `git fetch origin refs/pull/<N>/head:refs/remotes/origin/pr<N>`. The ref survives branch deletion.
- Record the PR number, state (open, closed, merged), and head SHA in the scope line.

## Diverged reference (the reference moved after the fork)

- Find the fork point with `git merge-base <branch> <reference>` and count the reference's later commits with `git rev-list --count <fork>..<reference>`.
- Use `reference...branch` (three-dot) for the branch's own delta. A two-dot diff lists every reference commit since the fork in reverse, so newer reference features appear as deletions by the branch.
- Check whether the branch tip is already an ancestor of the reference: `git merge-base --is-ancestor <branch-tip> <reference>`. If it is, the change landed earlier, and the review question is whether later reference commits removed it.
- Compare the same path on both sides with `git diff <tip> <reference> -- <path>` to see how far the content has drifted. A one-file difference means the branch is effectively already in the reference.
- State in the verdict which side is the target: a merge into the current reference, or a re-review of content that is already there.
