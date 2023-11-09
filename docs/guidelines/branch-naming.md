# Branch Naming Best Practices

### TL;DR
- Keep it short and concise, but make sure to include relevant key words.
- Use category words to easily identify the type of the task.
- Include ID of related issues to help tracking of progress.
- Keep the same name conventions for the whole project.

  ----

1. Use seperators. Use `/` after category and `-` between words.
2. Start branch name with category word.
  * `feature/` used for developing new features.
  * `bugfix/` used for bugs in the code. Example: `bugfix/header-styling`
  * `hotfix/` used for quickly fixing critical issues, usually with a temporary solution. Example: `hotfix/critical-security-issue`
  * `docs/` used to write, update or fix documentation. Example: `docs/api-endpoints`
  * `release/` used for preparing new production release. Example: `release/v1.0.1`
  * `test/` for developing tests. Example: `test/data-input`
    * Preferably tests should be developed alongside features.
  * `exploration/` used for exploring a topic or functionality. Example: `explore/mulit-agent-system-input`
3. Use ID of related issue. Example: `feature/123-xes-export`
4. Avoid using numbers only.
5. Avoid long branch names and comlicated words. Keep it concise and short for better readability.
6. Be consistent with branch naming.
