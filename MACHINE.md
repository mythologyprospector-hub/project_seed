# Permanent Machine Context

This file records stable operational facts used across projects.

These facts are **machine context, not project architecture**.

## Primary development machine

Hostname:

```text
mythos1
```

Common human name:

```text
Bucky
```

Primary local project root:

```text
~/projects
```

Every project repository is normally cloned as:

```text
~/projects/<repo-name>
```

Do not substitute:

```text
~/<repo-name>
```

unless the actual machine state explicitly says otherwise.

## Organs

When Organs is installed on the machine, its installation/runtime location is:

```text
/srv/organs
```

This is not the normal Git clone location.

## Bash prompt and repository status helpers

Bucky's interactive Bash configuration in `~/.bashrc` provides operational signals that assistants should understand and use. These are machine-wide shell conveniences, not project dependencies.

- **Timestamp:** the prompt shows the time (`HH:MM:SS`). `HISTTIMEFORMAT='%F %T  '` adds date and time when displaying shell history.
- **Command history persistence:** the prompt hook runs `history -a` after each command, appending new history entries to the history file. History is a useful diagnostic trail, not guaranteed complete evidence of everything that happened.
- **Exit status:** after a non-zero command result, the next prompt displays a red `✗` followed by the exit code, such as `✗1`. The prompt hook captures `$?` before running other commands so the original result is retained.
- **Location:** the prompt displays the current user, host, and working directory. In supported Xterm/Rxvt terminals, the window title is also updated with the user, host, and directory.
- **Git context:** inside a Git repository, the prompt displays the current branch. If HEAD is detached, it falls back to a short commit hash. A trailing `*` means `git status --porcelain` reported changes (including untracked files); it is a reminder to inspect and preserve the work, not a complete description of the changes. Outside a Git repository, no Git suffix is shown.
- **`pstatus` command:** inside a Git repository, `pstatus` prints the current branch, short-form working-tree changes, and the latest commit with its relative age. Outside a repository, it reports `Not a git repo`.

### How to use these signals safely

Before changing a repository, use the prompt and `pstatus` as quick orientation, then inspect the actual Git state and relevant files. A clean-looking prompt or empty `pstatus` output does not replace checking the branch, untracked files, relevant diffs, or project instructions when those details matter.

If the prompt shows `*`, do not reset, clean, overwrite, or otherwise discard changes merely to make the checkout tidy. Inspect first and preserve anything whose purpose is not understood.

If a red `✗` and exit code appear, treat the preceding command as failed and inspect its output before assuming the intended operation succeeded. A zero exit code is useful evidence, but does not by itself prove the intended outcome.

These details describe the `~/.bashrc` configuration supplied by the owner. If the live configuration changes, inspect it and update this record rather than assuming every machine or future installation has the same prompt customization.

## Git routine

The human does not reliably remember routine `git switch` / `git pull` sequences.

When asking the human to update a normal main-branch checkout, provide the complete sequence:

```bash
cd ~/projects/<repo-name>
git switch main
git pull --ff-only origin main
```

If a feature branch is intended, provide the exact branch command instead.

## Machine boundary

Do not infer additional filesystem paths, services, ports, devices, or configuration from this document.

If a machine detail matters and is not documented here, inspect the actual machine state.

Do not move project architecture into machine documentation merely because the architecture happens to run on this machine.
