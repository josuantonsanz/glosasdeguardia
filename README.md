

# How to copy this project to your github

- Create a new empty repository
- Download all the data in this one to a folder. 
- In that folder, execute the following commands:

```
git init
edit .gitignore to add 'content/'
git add .
git commit -m "first commit"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
```

# How to run the build

- Use uv to install the dependencies: `uv sync`
- Run the build: `uv run python build.py`
- Commit the changes: `git add .` and `git commit -m "<your message>"`
- Push the changes: `git push origin main`

# How to set up Github pages

- Go to the settings of your repository
- Click on "Pages"
- In "Source", click "GitHub Actions"
- Then, click "Configure" in "Static HTML
- Change "path" to "public"
- Click on "Save"