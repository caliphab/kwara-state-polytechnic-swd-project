"""Public academic calendar and administrator-only Excel imports."""
from datetime import date, datetime
from io import BytesIO
from flask import Blueprint, abort, flash, redirect, render_template, request, send_file, url_for
from flask_login import current_user, login_required
from openpyxl import Workbook, load_workbook
from openpyxl.utils.exceptions import InvalidFileException
from sqlalchemy.exc import SQLAlchemyError
from extensions import db
from app.models import AcademicCalendarEvent, UserRole

calendar_bp = Blueprint('calendar', __name__)
HEADERS = ['title', 'start_date', 'end_date', 'category', 'description']
MAX_ROWS = 1000


def require_admin():
    if current_user.role != UserRole.ADMIN:
        abort(403)


def parse_date(value, row_number, column):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return datetime.strptime(value.strip(), '%Y-%m-%d').date()
        except ValueError:
            pass
    raise ValueError(f'Row {row_number}: {column} must be a real Excel date or YYYY-MM-DD.')


def parse_sheet(upload):
    if not upload.filename or not upload.filename.lower().endswith('.xlsx'):
        raise ValueError('Please upload an Excel .xlsx spreadsheet.')
    try:
        book = load_workbook(upload.stream, read_only=True, data_only=True)
    except (InvalidFileException, ValueError, OSError, KeyError, EOFError, TypeError, RuntimeError) as exc:
        raise ValueError('Could not read the Excel workbook. Upload a valid .xlsx file.') from exc
    try:
        sheet = book.active
        rows = sheet.iter_rows(values_only=True)
        header_row = next(rows, None)
        if not header_row:
            raise ValueError('The Excel file is empty.')
        headers = [str(v).strip().lower().replace(' ', '_') if v is not None else '' for v in header_row]
        if len(headers) != len(set(headers)):
            raise ValueError('The Excel file contains duplicate column headers.')
        missing = [h for h in HEADERS[:2] if h not in headers]
        if missing:
            raise ValueError('Missing required columns: ' + ', '.join(missing))
        mapped = []
        for number, values in enumerate(rows, start=2):
            if not any(v is not None and str(v).strip() for v in values):
                continue
            if len(mapped) >= MAX_ROWS:
                raise ValueError(f'Too many events: maximum {MAX_ROWS} nonempty rows per upload.')
            entry = {h: (values[i] if i < len(values) else None) for i, h in enumerate(headers) if h}
            title = str(entry.get('title') or '').strip()
            if not title or len(title) > 180:
                raise ValueError(f'Row {number}: title is required (maximum 180 characters).')
            start = parse_date(entry.get('start_date'), number, 'start_date')
            end = parse_date(entry.get('end_date') or entry.get('start_date'), number, 'end_date')
            if end < start:
                raise ValueError(f'Row {number}: end_date cannot precede start_date.')
            category = str(entry.get('category') or 'Academic').strip()
            if len(category) > 60:
                raise ValueError(f'Row {number}: category is too long (maximum 60 characters).')
            description = str(entry.get('description') or '').strip()
            if len(description) > 2000:
                raise ValueError(f'Row {number}: description must be 2000 characters or fewer.')
            mapped.append(dict(title=title, start_date=start, end_date=end,
                               category=category, description=description))
        if not mapped:
            raise ValueError('No academic calendar events were found in the spreadsheet.')
        return mapped
    finally:
        book.close()


@calendar_bp.route('/calendar')
def view_calendar():
    sessions = [s[0] for s in db.session.query(AcademicCalendarEvent.session).distinct().order_by(AcademicCalendarEvent.session.desc()).all()]
    selected_session = request.args.get('session', '').strip()
    if selected_session not in sessions:
        selected_session = sessions[0] if sessions else '2026/2027'
    selected_semester = request.args.get('semester', 'All').strip()
    if selected_semester not in {'All', 'First', 'Second'}:
        selected_semester = 'All'
    query = AcademicCalendarEvent.query.filter_by(session=selected_session)
    if selected_semester != 'All':
        query = query.filter_by(semester=selected_semester)
    events = query.order_by(AcademicCalendarEvent.start_date, AcademicCalendarEvent.title).all()
    return render_template('calendar.html', events=events, sessions=sessions,
                           selected_session=selected_session, selected_semester=selected_semester)


@calendar_bp.route('/calendar/template')
@login_required
def download_template():
    require_admin()
    wb = Workbook()
    ws = wb.active
    ws.title = 'Academic Calendar'
    ws.append(HEADERS)
    ws.append(['Resumption and registration', date(2026, 11, 30), date(2026, 12, 4), 'Registration',
               'Example only. Replace with approved institutional dates.'])
    for cell in ws[2][1:3]:
        cell.number_format = 'yyyy-mm-dd'
    for column, width in {'A': 38, 'B': 18, 'C': 18, 'D': 22, 'E': 70}.items():
        ws.column_dimensions[column].width = width
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return send_file(output, as_attachment=True, download_name='academic_calendar_template.xlsx',
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


@calendar_bp.route('/admin/calendar/upload', methods=['POST'])
@login_required
def upload_calendar():
    require_admin()
    session = request.form.get('session', '').strip()
    semester = request.form.get('semester', '').strip()
    if not (len(session) == 9 and session[:4].isdigit() and session[4] == '/' and
            session[5:].isdigit() and int(session[5:]) == int(session[:4]) + 1):
        flash('Academic session must use the YYYY/YYYY format, e.g. 2026/2027.', 'danger')
        return redirect(url_for('page.dashboard'))
    if semester not in {'First', 'Second'}:
        flash('Select a valid semester.', 'danger')
        return redirect(url_for('page.dashboard'))
    file = request.files.get('calendar_file')
    if not file:
        flash('Choose an Excel .xlsx file before uploading.', 'danger')
        return redirect(url_for('page.dashboard'))
    try:
        entries = parse_sheet(file)
    except ValueError as exc:
        flash(str(exc), 'danger')
        return redirect(url_for('page.dashboard'))
    # Full replacement applies ONLY to the selected session and semester.
    try:
        AcademicCalendarEvent.query.filter_by(session=session, semester=semester).delete(synchronize_session=False)
        for entry in entries:
            db.session.add(AcademicCalendarEvent(**entry, session=session, semester=semester,
                                                created_by=current_user.id))
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        flash('Calendar import failed. No previous calendar entries were changed.', 'danger')
        return redirect(url_for('page.dashboard'))
    flash(f'Published {len(entries)} events for {session}, {semester} Semester. Previous events for this selection were replaced.', 'success')
    return redirect(url_for('calendar.view_calendar', session=session, semester=semester))
