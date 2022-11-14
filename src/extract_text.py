import requests
from flask_se import app
from se_models import db, Thesis
from flask_se_theses import get_text

db.app = app
db.init_app(app)

thesises = Thesis.query.all()

for thesis in thesises:
    if thesis.old_text_uri is not None:
        thesis_pdf = requests.get(thesis.old_text_uri, stream=True)
        file_name = 'texts/' + thesis.old_text_uri[thesis.old_text_uri.rfind('/') + 1:]
        open(file_name, 'wb').write(thesis_pdf.content)
        thesis.text = get_text(file_name)

db.session.commit()


