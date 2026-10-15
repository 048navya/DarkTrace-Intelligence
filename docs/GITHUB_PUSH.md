# Push this package to your existing repository

The ZIP has no Git history or credentials. Keep your current repository history:

1. Clone `https://github.com/Dark-Web-Threat-Actor-De-anonymization/SIH.git` into a new local folder, or use your existing clean clone.
2. Create a branch: `git switch -c integrate-dashboard`.
3. Extract the ZIP elsewhere. Copy the **contents** of its `darktrace-github-ready` folder into your repository root, replacing matching source files. Do not copy it as an extra nested project folder. Preserve your existing `.git`, private `.env` and corpus files.
4. The original repository tracked `node_modules`. Stop tracking that directory with `git rm -r --cached --ignore-unmatch node_modules`. This keeps installed files on disk; `.gitignore` prevents re-adding them.
5. Follow `docs/QUICKSTART.md`, then inspect `git diff` and `git status`. Confirm `.env`, `.dev.vars`, keys, database files and private corpus are absent from the staged changes.
6. Commit and push:

```sh
git add .
git commit -m "Integrate analyst dashboard and PostgreSQL evidence bridge"
git push -u origin integrate-dashboard
```

Open a pull request from this branch to `main` in GitHub. This package was not pushed to your GitHub account automatically.

The historical README is preserved under `docs/ORIGINAL_REPOSITORY_README.md`. The new root README is the current description. Do not use the historical claims as evidence of validated capabilities.
