import requests
from flask_se import app
from se_models import db, Thesis
from flask_se_theses import get_text

db.app = app
db.init_app(app)

thesises = Thesis.query.all()

for thesis in thesises:
    if thesis.text_uri is not None:
        file_name = 'static/thesis/texts/' + thesis.text_uri
        if file_name[file_name.rfind('.') + 1:] == 'pdf' or file_name[file_name.rfind('.') + 1:] == 'doc':
            thesis.text = get_text(file_name)
            db.session.commit()


