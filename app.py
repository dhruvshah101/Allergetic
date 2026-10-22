"""Allergetic: a local, single-person allergy record built with Flask."""
import io
import json
import secrets
import sqlite3
from datetime import datetime
from pathlib import Path

from flask import Flask, abort, flash, redirect, render_template, request, send_file, session, url_for


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        DATABASE=str(Path(app.instance_path) / 'allergetic.sqlite'),
        MAX_CONTENT_LENGTH=64 * 1024,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
    )
    if test_config:
        app.config.update(test_config)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    if not app.config.get('SECRET_KEY'):
        secret_file = Path(app.instance_path) / 'secret.key'
        if not secret_file.exists():
            secret_file.write_text(secrets.token_hex(32))
            secret_file.chmod(0o600)
        app.config['SECRET_KEY'] = secret_file.read_text()

    def connect():
        db = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
        return db

    with connect() as db:
        db.execute('CREATE TABLE IF NOT EXISTS profile (id INTEGER PRIMARY KEY CHECK(id=1), name TEXT NOT NULL, status TEXT NOT NULL, allergies TEXT NOT NULL, updated TEXT NOT NULL)')

    def read_profile():
        with connect() as db:
            row = db.execute('SELECT * FROM profile WHERE id=1').fetchone()
        if not row:
            return None
        record = dict(row)
        record['allergies'] = json.loads(record['allergies'])
        return record

    @app.before_request
    def csrf_protection():
        if 'csrf_token' not in session:
            session['csrf_token'] = secrets.token_hex(32)
        if request.method == 'POST':
            token = request.form.get('csrf_token', '')
            if not secrets.compare_digest(token, session['csrf_token']):
                abort(400, description='This form expired. Reload the page and try again.')

    @app.after_request
    def private_responses(response):
        response.headers['Cache-Control'] = 'no-store'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Referrer-Policy'] = 'same-origin'
        return response

    @app.route('/', methods=['GET', 'POST'])
    def index():
        profile = read_profile()
        draft = profile or {'name': '', 'status': 'unsure', 'allergies': []}
        errors = []
        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            status = request.form.get('status', '')
            allergens = request.form.getlist('allergen')
            reactions = request.form.getlist('reaction')
            entries = []
            if not name or len(name) > 80:
                errors.append('Enter a name between 1 and 80 characters.')
            if status not in {'yes', 'no', 'unsure'}:
                errors.append('Choose your allergy status.')
            if status == 'yes':
                if len(allergens) > 30:
                    errors.append('Please limit your record to 30 allergy entries.')
                seen = set()
                for i, raw in enumerate(allergens[:30]):
                    allergen = raw.strip()
                    reaction = reactions[i].strip() if i < len(reactions) else ''
                    entries.append({'allergen': allergen, 'reaction': reaction})
                    if not allergen or len(allergen) > 100:
                        errors.append(f'Entry {i + 1}: enter an allergen between 1 and 100 characters.')
                    if len(reaction) > 300:
                        errors.append(f'Entry {i + 1}: keep the reaction under 301 characters.')
                    if allergen.casefold() in seen:
                        errors.append(f'Entry {i + 1}: this allergen is already listed.')
                    seen.add(allergen.casefold())
                if not entries:
                    errors.append('Add at least one allergen, or select a different status.')
            draft = {'name': name, 'status': status, 'allergies': entries}
            if not errors:
                updated = datetime.now().astimezone().strftime('%b %d, %Y at %I:%M %p %Z')
                with connect() as db:
                    db.execute('INSERT OR REPLACE INTO profile VALUES (1, ?, ?, ?, ?)',
                               (name, status, json.dumps(entries), updated))
                flash('Your record is saved. Your allergy card is ready.')
                return redirect(url_for('index', _anchor='saved-card'))
        return render_template('index.html', profile=profile, draft=draft, errors=errors), 422 if errors else 200

    @app.get('/card')
    def card():
        profile = read_profile()
        if not profile:
            return redirect(url_for('index'))
        return render_template('card.html', profile=profile)

    @app.get('/download')
    def download():
        profile = read_profile()
        if not profile:
            abort(404)
        lines = ['ALLERGETIC — PERSONAL ALLERGY RECORD', f"Name: {profile['name']}",
                 f"Updated: {profile['updated']}", 'Source: Self-reported; not independently verified', '']
        if profile['status'] == 'yes':
            for entry in profile['allergies']:
                lines.extend([f"Allergen: {entry['allergen']}", f"Reported reaction: {entry['reaction'] or 'Not recorded'}", ''])
        else:
            lines.append('No known allergies reported.' if profile['status'] == 'no' else 'Allergy status is unknown / unsure.')
        lines.extend(['', 'This record communicates reported information.', 'It does not determine whether a food or medicine is safe.'])
        return send_file(io.BytesIO(('\n'.join(lines) + '\n').encode('utf-8')),
                         mimetype='text/plain; charset=utf-8', as_attachment=True,
                         download_name='allergetic-record.txt')

    @app.post('/reset')
    def reset():
        with connect() as db:
            db.execute('DELETE FROM profile')
        flash('Your saved record has been deleted.')
        return redirect(url_for('index'))

    return app


if __name__ == '__main__':
    create_app().run(host='127.0.0.1', port=5000, debug=False)
