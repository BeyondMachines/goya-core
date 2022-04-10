# Coding Standard of goya-core

## Documenting code
Use Django docstrings to build and review documentation
https://www.geeksforgeeks.org/python-docstrings/

## Self-checks of code quality
Run a flake8 linter and clean up the errors before making a commit. 
```
flake8 --ignore=E501,F401
```

## Definiton of done
Code is done when it's ready to be used by a customer. Everything else is work in progress.
Make a PR to merge to `main`/`master` only when your code is ready to be consumed by a user. 

## How do you (reasonably) know it's ready to be used by a customer?
- Code quality and Security scans are passing (linters and code scans)
- The code runs as originally planned (happy path).
- You've used the code in at least three ways you didn't plan to use and it didn't break (unhappy path).
- You know you won't have to come back to the code in a day to fix something (technical debt resolved).
- You are confident someone else won't have to come back to the code to fix a mess your code made.


## Pull Request (code change) standard
### Make small changes via commits and Pull Requests
Don't change a bunch of files and a bunch of features in a single commit. 
If you do that it's impossible for people to properly review what you did.

### Always commit only the file(s) needed for the code change
Never use `git add .` to a commit. Only commit the files that you changed for a particular effort.

### Make it easy for people to understand what you did
In the commit message and in the Pull Request description summarize the type of commit.
`feat:` The new feature you're adding to a particular application
`fix:` A bug fix
`style:` Feature and updates related to styling
`refactor:` Refactoring a specific section of the codebase
`test:` Everything related to testing
`docs:` Everything related to documentation
`chore:` Regular code maintenance