# Allergetic Allergy Docket

**A personal allergy docket that makes allergy information easier to communicate.**

Allergetic is a beginner-friendly web application built with Python and Flask. Users can create a personal allergy record, add reaction notes, and generate a readable card to bring to appointments or show during conversations.

## Why I built this

Communicating allergies isn't always easy, especially for people who find spoken communication difficult, especially as an individual with severe allergies to all types of peanuts and tree nutsInspired by the idea of an immunization docket, this project explores how a simple digital record can help people organize and communicate their reported allergies.

The project began as a Python command-line program that asked for a name and allergies. It has grown into a web application with an HTML/CSS frontend, interactive forms, and local database storage.

## Features

- Create and edit a personal allergy record.
- Select known allergies, no known allergies, or an unsure status.
- Add multiple allergens with optional reaction notes.
- Remove entries and detect duplicate allergens.
- Save information locally with SQLite.
- View a readable allergy card.
- Print the card or save it as a PDF through the browser's print dialog.
- Download the record as a text file.
- Use the interface on desktop and mobile screens.
- Delete the saved record from the app.

## Built with

| Technology | Purpose |
| --- | --- |
| Python / Flask | Routes, validation, and application logic |
| HTML / Jinja | Page structure and displaying saved information |
| CSS | Responsive design and print styling |
| JavaScript | Dynamic allergy fields and browser interactions |
| SQLite | Local record storage |
| Python unittest | Backend tests |

## Getting started

### Requirements

- Python 3.10 or newer
- pip
- A web browser

### 1. Download the project

Download this repository using **Code → Download ZIP**, extract it, and open a terminal in the folder containing `app.py`.

### 2. Create a virtual environment

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (Command Prompt):**

```bat
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Start the app

```bash
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

Keep the terminal running while using the app. Press **Ctrl+C** to stop the server.

> If the page won't open, check that the server is running and that the terminal shows no errors. Opening an HTML file directly will not run the Flask application.

## How to use it

1. Enter a name. Use fictional information while developing or testing.
2. Choose an allergy status.
3. If you select **Yes, I do**, enter each allergen separately and optionally describe a reaction.
4. Click **Save my record** to update the saved allergy card.
5. Use **View & print** or **Download .txt** to create a copy.
6. Edit the form and save again whenever you want to update the record.

The card displays the **last saved information**, not unsaved changes in the form. Selecting **None known** or **I'm unsure** and saving clears the previous allergy entries from the current record.

## Project structure

```text
allergetic/
├── app.py                  # Flask routes, validation, storage, and exports
├── requirements.txt        # Python dependencies
├── test_app.py             # Backend tests
├── README.md
├── templates/
│   ├── base.html           # Shared page layout
│   ├── index.html          # Record form and saved card
│   ├── _card.html          # Reusable card template
│   └── card.html           # Print-friendly card page
└── static/
    ├── style.css           # Responsive and print styles
    └── app.js              # Interactive form behavior
```

On first run, the app also creates an `instance/` folder for its local database and session secret. This folder is excluded from Git.

## How it works

The browser submits the form to Flask. Python validates the name, allergy status, and entries, then saves the record in SQLite. Flask renders the HTML templates with the saved information. JavaScript manages adding and removing form fields; validation also happens on the server.

## Running tests

From the project folder, with the virtual environment activated:

```bash
python -m unittest -v
```

The tests cover saving and updating records, exports, invalid input, allergy status changes, form token protection, HTML escaping, and deletion.

## Current scope and privacy

Allergetic is a **local, single-person learning prototype**. It has no accounts: everyone accessing the same running app instance sees the same saved record.

- Records are self-reported and are not independently verified.
- The app does not diagnose allergies or determine whether a food or medicine is safe.
- The SQLite database is not encrypted.
- The development server runs on `127.0.0.1`; this version should not be exposed publicly as-is.
- Deleting a record in the app does not remove previously downloaded or printed copies.
- Do not upload real allergy records, the `instance/` folder, or secrets to GitHub.

The included `.gitignore` excludes `instance/`, `.venv/`, and Python cache files. GitHub stores the source code; GitHub Pages cannot run this Flask backend.

## What this project explores

- Turning a command-line program into a web application
- Connecting HTML forms to Python routes
- Validating and storing user input
- Using templates to reuse interface components
- Building responsive layouts and printable pages
- Testing application behavior

## Future improvements

These are ideas for future work, not features currently implemented:

- Separate user accounts and private records
- Clearer distinction between reported and clinician-verified information
- Record history and update tracking
- Additional language support
- More accessibility testing with users
- A deployment setup with appropriate authentication and data protection
