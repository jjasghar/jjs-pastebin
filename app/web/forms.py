from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length

# Common programming languages for syntax highlighting
LANGUAGES = [
    ('text', 'Plain Text'),
    ('python', 'Python'),
    ('javascript', 'JavaScript'),
    ('html', 'HTML'),
    ('css', 'CSS'),
    ('json', 'JSON'),
    ('xml', 'XML'),
    ('sql', 'SQL'),
    ('bash', 'Bash/Shell'),
    ('c', 'C'),
    ('cpp', 'C++'),
    ('java', 'Java'),
    ('php', 'PHP'),
    ('ruby', 'Ruby'),
    ('go', 'Go'),
    ('rust', 'Rust'),
    ('typescript', 'TypeScript'),
    ('yaml', 'YAML'),
    ('markdown', 'Markdown'),
    ('dockerfile', 'Dockerfile'),
]

class PasteForm(FlaskForm):
    title = StringField('Title', validators=[
        DataRequired(), 
        Length(max=200, message='Title must be less than 200 characters')
    ])
    content = TextAreaField('Content', validators=[DataRequired()], render_kw={
        'rows': 20, 
        'placeholder': 'Paste your code or text here...'
    })
    language = SelectField('Language', choices=LANGUAGES, default='text')
    is_public = BooleanField('Public', default=True, false_values=('false', ''))
    submit = SubmitField('Create Paste') 