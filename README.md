# Privacy DB

A community-driven database of app permissions and privacy data, scraped from Google Play Store listings.

## What's in here?

The `apps/` directory contains JSON files for popular Android apps, each showing:

- **Permissions** — grouped by category (Camera, Location, Contacts, etc.) with individual permission descriptions
- **Data Safety** — what data the app shares with third parties, what it collects, encryption status, deletion options
- **Metadata** — app name, category, rating, download count
- **Scan date** — when the data was last fetched

## Why?

Most people don't check what an app requests before installing it. This database makes that data accessible, searchable, and version-controlled — so you can see what permissions an app has *before* you install it, and track how they change over time.

Used by the [Take Control](https://github.com/hell-abhi/take-control) Android app.

## Browse the data

Each file is named by package name:
```
apps/com.whatsapp.json
apps/com.instagram.android.json
apps/com.google.android.gm.json
```

## Add an app

**Option 1: Open an issue**

Create a [new issue](../../issues/new?template=scan-request.yml) with the Play Store URL or package name. We'll scan it and add it.

**Option 2: Run the scanner yourself**

```bash
cd scripts
python3 scan.py com.example.app > ../apps/com.example.app.json
```

Then open a PR with the new JSON file.

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## Data format

```json
{
  "package_name": "com.whatsapp",
  "app_name": "WhatsApp Messenger",
  "category": "Communication",
  "rating": 4.22,
  "downloads": 10000000000,
  "permissions": [
    {
      "group": "Contacts",
      "permissions": [
        "find accounts on the device",
        "read your contacts",
        "modify your contacts"
      ]
    }
  ],
  "total_permissions": 25,
  "data_safety": {
    "shared": "No data shared with third parties",
    "collected": "This app may collect these data types",
    "encrypted": true,
    "deletable": true
  },
  "scanned_at": "2026-03-19T10:00:00Z",
  "source": "Google Play Store"
}
```

## License

Data is sourced from publicly available Google Play Store listings. This project is for educational and research purposes.
