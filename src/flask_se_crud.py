# SPDX-License-Identifier: Apache-2.0

import csv
import io
from contextlib import suppress

from flask import Response, abort, redirect, render_template, request, url_for
from flask_wtf import FlaskForm
from sqlalchemy import inspect
from wtforms import (
    BooleanField,
    HiddenField,
    IntegerField,
    StringField,
    SubmitField,
    TextAreaField,
)

from se_models import db


class CrudView:
    model = None
    endpoint = ""
    name = ""
    can_delete = True
    can_create = True
    can_edit = True
    can_export = True
    column_list = None
    column_labels = None
    column_choices = None
    column_formatters = None
    form_columns = None
    form_overrides = None
    form_args = None
    form_widget_args = None
    form_extra_fields = None
    column_display_pk = False

    def __init__(self, app, model, endpoint, name=None):
        self.model = model
        self.endpoint = endpoint
        self.name = name or (model.__name__ if model else endpoint)
        if model:
            self._register_routes(app)

    def _register_routes(self, app):
        app.add_url_rule(
            f"/admin/{self.endpoint}/",
            endpoint=f"{self.endpoint}.index_view",
            view_func=self.index_view,
            methods=["GET"],
        )
        app.add_url_rule(
            f"/admin/{self.endpoint}/new/",
            endpoint=f"{self.endpoint}.create_view",
            view_func=self.create_view,
            methods=["GET", "POST"],
        )
        app.add_url_rule(
            f"/admin/{self.endpoint}/edit/",
            endpoint=f"{self.endpoint}.edit_view",
            view_func=self.edit_view,
            methods=["GET", "POST"],
        )
        app.add_url_rule(
            f"/admin/{self.endpoint}/delete/",
            endpoint=f"{self.endpoint}.delete_view",
            view_func=self.delete_view,
            methods=["POST"],
        )
        app.add_url_rule(
            f"/admin/{self.endpoint}/details/",
            endpoint=f"{self.endpoint}.details_view",
            view_func=self.details_view,
            methods=["GET"],
        )
        app.add_url_rule(
            f"/admin/{self.endpoint}/action/",
            endpoint=f"{self.endpoint}.action_view",
            view_func=self.action_view,
            methods=["POST"],
        )
        app.add_url_rule(
            f"/admin/{self.endpoint}/export/<export_type>/",
            endpoint=f"{self.endpoint}.export",
            view_func=self.export_view,
            methods=["GET"],
        )

    def _get_columns(self):
        mapper = inspect(self.model)
        all_cols = [c.key for c in mapper.columns]
        rel_cols = [r.key for r in mapper.relationships]
        if self.column_list:
            return self.column_list
        return all_cols + rel_cols

    def _get_form_columns(self):
        mapper = inspect(self.model)
        all_cols = [c.key for c in mapper.columns if c.key != mapper.primary_key[0].key]
        if self.form_columns:
            return self.form_columns
        return all_cols

    def _get_pk(self):
        return inspect(self.model).primary_key[0].key

    def _get_obj(self, id):
        pk = self._get_pk()
        return self.model.query.filter_by(**{pk: id}).first()

    def _list_query(self):
        return self.model.query

    def _count_query(self):
        return self._list_query()

    def index_view(self):
        page = request.args.get("page", 1, type=int)
        page_size = request.args.get("page_size", 20, type=int)
        sort = request.args.get("sort", self._get_pk(), type=str)
        desc = request.args.get("desc", 0, type=int)
        query = self._list_query()
        sort_col = getattr(self.model, sort, None)
        order = None
        if sort_col is not None:
            with suppress(Exception):
                order = sort_col.desc() if desc else sort_col.asc()
        if order is not None:
            query = query.order_by(order)
        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()
        columns = self._get_columns()
        labels = self.column_labels or {}
        choices = self.column_choices or {}
        pk = self._get_pk()
        return render_template(
            "admin/list.html",
            items=items,
            columns=columns,
            labels=labels,
            choices=choices,
            column_formatters=self.column_formatters or {},
            column_display_pk=self.column_display_pk,
            pk=pk,
            endpoint=self.endpoint,
            name=self.name,
            page=page,
            page_size=page_size,
            total=total,
            can_create=self.can_create,
            can_delete=self.can_delete,
            can_edit=self.can_edit,
            can_export=self.can_export,
            sort=sort,
            desc=desc,
        )

    def create_view(self):
        if not self.can_create:
            abort(404)
        form = self._build_form()
        if form.validate_on_submit():
            obj = self.model() if self.model is not None else None
            if obj is None:
                abort(500)
            self._populate_obj(obj, form)
            db.session.add(obj)
            db.session.commit()
            return redirect(url_for(f"{self.endpoint}.index_view"))
        return render_template(
            "admin/form.html", form=form, endpoint=self.endpoint, name=self.name, is_edit=False
        )

    def edit_view(self):
        if not self.can_edit:
            abort(404)
        self._get_pk()
        obj_id = request.args.get("id", type=int)
        obj = self._get_obj(obj_id)
        if not obj:
            abort(404)
        self.on_form_prefill(obj, obj_id)
        form = self._build_form(obj)
        if form.validate_on_submit():
            self.on_model_change(form, obj, False)
            self._populate_obj(obj, form)
            db.session.commit()
            return redirect(url_for(f"{self.endpoint}.index_view"))
        return render_template(
            "admin/form.html", form=form, endpoint=self.endpoint, name=self.name, is_edit=True
        )

    def delete_view(self):
        if not self.can_delete:
            abort(404)
        self._get_pk()
        obj_id = request.form.get("id", type=int)
        obj = self._get_obj(obj_id)
        if obj:
            db.session.delete(obj)
            db.session.commit()
        return redirect(url_for(f"{self.endpoint}.index_view"))

    def details_view(self):
        self._get_pk()
        obj_id = request.args.get("id", type=int)
        obj = self._get_obj(obj_id)
        if not obj:
            abort(404)
        columns = self._get_columns()
        labels = self.column_labels or {}
        return render_template(
            "admin/details.html",
            obj=obj,
            columns=columns,
            labels=labels,
            endpoint=self.endpoint,
            name=self.name,
        )

    def action_view(self):
        ids = request.form.getlist("id", type=int)
        action = request.form.get("action", "delete")
        if action == "delete":
            for obj_id in ids:
                obj = self._get_obj(obj_id)
                if obj:
                    db.session.delete(obj)
            db.session.commit()
        return redirect(url_for(f"{self.endpoint}.index_view"))

    def export_view(self, export_type):
        if export_type != "csv":
            abort(404)

        out = io.StringIO()
        writer = csv.writer(out)
        cols = self._get_columns()
        labels = self.column_labels or {}
        writer.writerow([labels.get(c, c) for c in cols])
        for obj in self._list_query().all():
            writer.writerow([getattr(obj, c, "") for c in cols])

        return Response(
            out.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment;filename={self.endpoint}.csv"},
        )

    def _build_form(self, obj=None):
        class _AdminForm(FlaskForm):
            pass

        pk = self._get_pk()
        if obj:
            setattr(_AdminForm, pk, HiddenField(default=getattr(obj, pk)))

        mapper = inspect(self.model)
        form_cols = self._get_form_columns()

        if self.form_extra_fields:
            for name in self.form_extra_fields:
                if name not in form_cols:
                    form_cols.append(name)

        for col_key in form_cols:
            col = mapper.columns.get(col_key)
            default = getattr(obj, col_key, None) if obj else None
            label = (self.column_labels or {}).get(col_key, col_key)

            if self.form_overrides and col_key in self.form_overrides:
                field_cls = self.form_overrides[col_key]
            elif col is None:
                continue
            elif isinstance(col.type, db.Text if hasattr(db, "Text") else type(None)):
                field_cls = TextAreaField
            elif isinstance(col.type, db.Integer if hasattr(db, "Integer") else type(None)):
                field_cls = IntegerField
            elif isinstance(col.type, db.Boolean if hasattr(db, "Boolean") else type(None)):
                field_cls = BooleanField
            elif isinstance(col.type, db.String if hasattr(db, "String") else type(None)):
                field_cls = StringField
            else:
                field_cls = StringField

            kwargs = {"label": label, "default": default}

            if self.form_args and col_key in self.form_args:
                kwargs.update(self.form_args[col_key])

            if self.form_widget_args and col_key in self.form_widget_args:
                kwargs["render_kw"] = self.form_widget_args[col_key]

            if col is not None and not col.nullable and col_key != pk and not col.default:
                pass

            setattr(_AdminForm, col_key, field_cls(**kwargs))

        _AdminForm.submit = SubmitField("Save")
        return _AdminForm(request.form if request.method == "POST" else None)

    def _populate_obj(self, obj, form):
        mapper = inspect(self.model)
        for col_key in self._get_form_columns():
            if hasattr(form, col_key):
                val = getattr(form, col_key).data
                col = mapper.columns.get(col_key)
                if col is not None:
                    setattr(obj, col_key, val)

    def on_form_prefill(self, obj, obj_id):
        pass

    def on_model_change(self, form, model, is_created):
        pass
