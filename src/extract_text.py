# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
from flask_se import app
from flask_se_theses import get_text
from se_models import Thesis, db

db.app = app
db.init_app(app)

thesises = Thesis.query.all()

for thesis in thesises:
    if thesis.text_uri is not None:
        file_name = "static/thesis/texts/" + thesis.text_uri
        if (
            file_name[file_name.rfind(".") + 1 :] == "pdf"
            or file_name[file_name.rfind(".") + 1 :] == "doc"
        ):
            thesis.text = get_text(file_name)
            db.session.commit()
