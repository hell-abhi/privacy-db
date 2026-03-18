# Contributing to Privacy DB

Thanks for helping build the world's most transparent app permissions database!

## How to add an app

### Option 1: Open an issue (easiest)

1. Go to [Issues → New Issue](../../issues/new?template=scan-request.yml)
2. Paste the Google Play Store URL or package name
3. We'll scan it and add the JSON file

### Option 2: Submit a PR (for contributors)

1. **Fork** this repo
2. **Run the scanner:**
   ```bash
   cd scripts
   python3 scan.py <package_name_or_play_store_url> > ../apps/<package_name>.json
   ```
3. **Verify** the JSON looks correct (open it, check permissions are populated)
4. **Commit** with message: `Add <app_name> (<package_name>)`
5. **Open a PR**

### Requirements

- Python 3.7+
- No dependencies — uses only stdlib (`urllib`, `json`, `re`)
- The scanner fetches the public Play Store page and parses the embedded data

### What we scan

- App metadata (name, category, rating, downloads)
- All requested permissions, grouped by type
- Data safety declarations (shared/collected data, encryption, deletion)

### What we DON'T scan

- We don't install the app
- We don't decompile APKs
- We don't access any private data
- All data comes from the publicly visible Play Store listing

### Updating existing apps

Apps get updated and permissions change. To refresh an app's data:

```bash
python3 scripts/scan.py com.whatsapp > apps/com.whatsapp.json
```

Include `Update <app_name>` in your commit message.

### Naming convention

Files are named by package name exactly as it appears on the Play Store:
```
apps/com.whatsapp.json
apps/com.instagram.android.json
```
