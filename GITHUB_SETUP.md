# GitHub Setup Instructions

## After creating your GitHub repository, run these commands:

```bash
cd /Users/marcolin/Documents/Coding/Deyang/GoL

# Replace YOUR_USERNAME with your actual GitHub username
git remote add origin https://github.com/YOUR_USERNAME/game-of-life.git

# Push to GitHub
git push -u origin main
```

## Enable GitHub Pages

1. Go to your repo on GitHub: `https://github.com/YOUR_USERNAME/game-of-life`
2. Click **Settings** (top menu)
3. Click **Pages** (left sidebar)
4. Under "Build and deployment":
   - **Source**: Deploy from a branch
   - **Branch**: `main`
   - **Folder**: `/docs` ← IMPORTANT!
5. Click **Save**
6. Wait 1-2 minutes for deployment

## Access Your Live Site

After deployment completes, your Game of Life will be live at:
```
https://YOUR_USERNAME.github.io/game-of-life/
```

## Optional: Update Repository Link in HTML

Edit `docs/index.html` line ~112 to update the repo link:
```html
<a href="https://github.com/YOUR_USERNAME/game-of-life" target="_blank">View Repo</a>
```

Then commit and push:
```bash
git add docs/index.html
git commit -m "Update repository link"
git push
```

## Troubleshooting

### If push fails with authentication:
- Use GitHub personal access token (classic) instead of password
- Or set up SSH keys: https://docs.github.com/en/authentication

### If Pages doesn't work:
- Check Settings → Pages shows green checkmark
- Make sure you selected `/docs` folder (not root)
- Wait a few minutes for first deployment
- Check Actions tab for build status

### To update the site:
```bash
# After making changes to docs/
git add .
git commit -m "Your update message"
git push
# GitHub Pages will auto-redeploy in ~1 minute
```

