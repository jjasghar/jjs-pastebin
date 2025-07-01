from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.util import ClassNotFound

from app import db
from app.models import Paste, User
from app.web.forms import PasteForm

web_bp = Blueprint("web", __name__)


def highlight_code(content, language):
    """Highlight code using Pygments"""
    try:
        if language == "text":
            lexer = guess_lexer(content)
        else:
            lexer = get_lexer_by_name(language)
        formatter = HtmlFormatter(cssclass="highlight", linenos=True)
        return highlight(content, lexer, formatter)
    except ClassNotFound:
        # Fallback to plain text
        lexer = get_lexer_by_name("text")
        formatter = HtmlFormatter(cssclass="highlight", linenos=True)
        return highlight(content, lexer, formatter)


def highlight_code_preview(content, language, max_length=120):
    """Generate a highlighted code preview for list views"""
    try:
        # Convert newlines to spaces and truncate content for single-line preview
        preview_content = (
            content.replace("\n", " ").replace("\r", " ").replace("\t", " ")
        )
        preview_content = " ".join(preview_content.split())  # Normalize whitespace
        preview_content = preview_content[:max_length]
        if len(content) > max_length:
            preview_content += "..."

        if language == "text":
            lexer = guess_lexer(preview_content)
        else:
            lexer = get_lexer_by_name(language)

        # Use a simple formatter without line numbers for previews
        formatter = HtmlFormatter(cssclass="highlight-preview", nowrap=True)
        return highlight(preview_content, lexer, formatter)
    except ClassNotFound:
        # Fallback to plain text with basic formatting
        lexer = get_lexer_by_name("text")
        formatter = HtmlFormatter(cssclass="highlight-preview", nowrap=True)
        return highlight(preview_content, lexer, formatter)


@web_bp.route("/")
def index():
    page = request.args.get("page", 1, type=int)
    per_page = 20

    # Get public pastes
    pastes = (
        Paste.query.filter_by(is_public=True)
        .order_by(Paste.created_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    # Add highlighted previews to each paste
    for paste in pastes.items:
        paste.highlighted_preview = highlight_code_preview(
            paste.content, paste.language
        )

    return render_template("index.html", pastes=pastes)


@web_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_paste():
    form = PasteForm()
    if form.validate_on_submit():
        # Handle boolean field explicitly by checking raw form data
        raw_is_public = request.form.get("is_public", "").lower()
        if raw_is_public in ("false", "f", "0", ""):
            is_public = False
        else:
            is_public = bool(form.is_public.data)

        paste = Paste(
            title=form.title.data or "Untitled",
            content=form.content.data,
            language=form.language.data,
            is_public=is_public,
            user_id=current_user.id,
        )
        db.session.add(paste)
        db.session.commit()
        flash("Paste created successfully!", "success")
        return redirect(url_for("web.view_paste", unique_id=paste.unique_id))

    return render_template("create_paste.html", title="Create Paste", form=form)


@web_bp.route("/paste/<unique_id>")
def view_paste(unique_id):
    paste = Paste.query.filter_by(unique_id=unique_id).first_or_404()

    # Check if user can view this paste
    if not paste.is_public:
        if not current_user.is_authenticated or (
            current_user.id != paste.user_id and not current_user.is_superuser
        ):
            # Return 404 for private pastes to unauthorized users
            from flask import abort

            abort(404)

    # Increment view count
    paste.increment_views()

    # Highlight the code
    highlighted_content = highlight_code(paste.content, paste.language)

    return render_template(
        "view_paste.html", paste=paste, highlighted_content=highlighted_content
    )


@web_bp.route("/paste/<unique_id>/raw")
def raw_paste(unique_id):
    paste = Paste.query.filter_by(unique_id=unique_id).first_or_404()

    # Check if user can view this paste
    if not paste.is_public:
        if not current_user.is_authenticated or (
            current_user.id != paste.user_id and not current_user.is_superuser
        ):
            return "This paste is private.", 403

    return paste.content, 200, {"Content-Type": "text/plain; charset=utf-8"}


@web_bp.route("/paste/<unique_id>/edit", methods=["GET", "POST"])
@login_required
def edit_paste(unique_id):
    paste = Paste.query.filter_by(unique_id=unique_id).first_or_404()

    # Check if user can edit this paste
    if current_user.id != paste.user_id and not current_user.is_superuser:
        flash("You can only edit your own pastes.", "error")
        return redirect(url_for("web.view_paste", unique_id=unique_id))

    form = PasteForm(obj=paste)
    if form.validate_on_submit():
        # Handle boolean field explicitly by checking raw form data
        raw_is_public = request.form.get("is_public", "").lower()
        if raw_is_public in ("false", "f", "0", ""):
            is_public = False
        else:
            is_public = bool(form.is_public.data)

        paste.title = form.title.data
        paste.content = form.content.data
        paste.language = form.language.data
        paste.is_public = is_public
        db.session.commit()
        flash("Paste updated successfully!", "success")
        return redirect(url_for("web.view_paste", unique_id=unique_id))

    return render_template(
        "edit_paste.html", title="Edit Paste", form=form, paste=paste
    )


@web_bp.route("/paste/<unique_id>/delete", methods=["POST"])
@login_required
def delete_paste(unique_id):
    paste = Paste.query.filter_by(unique_id=unique_id).first_or_404()

    # Check if user can delete this paste
    if current_user.id != paste.user_id and not current_user.is_superuser:
        flash("You can only delete your own pastes.", "error")
        return redirect(url_for("web.view_paste", unique_id=unique_id))

    db.session.delete(paste)
    db.session.commit()
    flash("Paste deleted successfully!", "success")
    return redirect(url_for("web.index"))


@web_bp.route("/user/<username>")
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get("page", 1, type=int)
    per_page = 20

    # Get user's public pastes (or all if viewing own profile)
    query = user.pastes
    if not current_user.is_authenticated or current_user.id != user.id:
        query = query.filter_by(is_public=True)

    pastes = query.order_by(Paste.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template("user_profile.html", user=user, pastes=pastes)


@web_bp.route("/api-docs")
def api_docs():
    """API Documentation page"""
    return render_template("api_docs.html", title="API Documentation")


@web_bp.route("/cli-tools")
def cli_tools_docs():
    """CLI Tools Documentation page"""
    return render_template("cli_tools_docs.html", title="CLI Tools")


@web_bp.route("/language/<language>")
def language_filter(language):
    """Filter pastes by programming language"""
    page = request.args.get("page", 1, type=int)
    per_page = 20

    # Get public pastes for the specific language
    pastes = (
        Paste.query.filter_by(is_public=True, language=language)
        .order_by(Paste.created_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    # Add highlighted previews to each paste
    for paste in pastes.items:
        paste.highlighted_preview = highlight_code_preview(
            paste.content, paste.language
        )

    return render_template(
        "language_filter.html",
        pastes=pastes,
        language=language,
        title=f"{language.title()} Pastes",
    )
