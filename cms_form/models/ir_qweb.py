# -*- coding: utf-8 -*-
import ast

from odoo import models

# TODO: Remove file in v11
# Include this fix https://github.com/odoo/odoo/commit/27ff895dfd92619d496f67c8b11cb76277bf62d2."""  # noqa
# Backported to OCB here https://github.com/OCA/OCB/pull/654


class IRQweb(models.AbstractModel):
    _inherit = "ir.qweb"

    def _compile_directive_call(self, el, options):
        """Barely copied from odoo master (v11)."""
        tmpl = el.attrib.pop('t-call')
        _values = self._make_name('values_copy')
        call_options = el.attrib.pop('t-call-options', None)
        nsmap = options.get('nsmap')

        _values = self._make_name('values_copy')

        content = [
            # values_copy = values.copy()
            ast.Assign(
                targets=[ast.Name(id=_values, ctx=ast.Store())],
                value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id='values', ctx=ast.Load()),
                        attr='copy',
                        ctx=ast.Load()
                    ),
                    args=[], keywords=[],
                    starargs=None, kwargs=None
                )
            )
        ]

        body = self._compile_directive_content(el, options)
        if body:
            def_name = self._create_def(options, body, prefix='body_call_content', lineno=el.sourceline)  # noqa

            # call_content = []
            content.append(
                ast.Assign(
                    targets=[ast.Name(id='call_content', ctx=ast.Store())],
                    value=ast.List(elts=[], ctx=ast.Load())
                )
            )
            # body_call_content(self, call_content.append, values, options)
            content.append(
                ast.Expr(self._call_def(
                    def_name,
                    append=ast.Attribute(
                        value=ast.Name(id='call_content', ctx=ast.Load()),
                        attr='append',
                        ctx=ast.Load()
                    ),
                    values=_values
                ))
            )
            # values_copy[0] = call_content
            content.append(
                ast.Assign(
                    targets=[ast.Subscript(
                        value=ast.Name(id=_values, ctx=ast.Load()),
                        slice=ast.Index(ast.Num(0)),
                        ctx=ast.Store()
                    )],
                    value=ast.Name(id='call_content', ctx=ast.Load())
                )
            )
        else:
            # values_copy[0] = []
            content.append(
                ast.Assign(
                    targets=[ast.Subscript(
                        value=ast.Name(id=_values, ctx=ast.Load()),
                        slice=ast.Index(ast.Num(0)),
                        ctx=ast.Store()
                    )],
                    value=ast.List(elts=[], ctx=ast.Load())
                )
            )

        if nsmap or call_options:
            # copy the original dict of options to pass to the callee
            name_options = self._make_name('options')
            content.append(
                # options_ = options.copy()
                ast.Assign(
                    targets=[ast.Name(id=name_options, ctx=ast.Store())],
                    value=ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id='options', ctx=ast.Load()),
                            attr='copy',
                            ctx=ast.Load()
                        ),
                        args=[], keywords=[], starargs=None, kwargs=None
                    )
                )
            )

            if call_options:
                # update this dict with the content of `t-call-options`
                content.extend([
                    # options_.update(template options)
                    ast.Expr(ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id=name_options, ctx=ast.Load()),
                            attr='update',
                            ctx=ast.Load()
                        ),
                        args=[self._compile_expr(call_options)],
                        keywords=[], starargs=None, kwargs=None
                    ))
                ])

            if nsmap:
                # update this dict with the current nsmap so that the callee know # noqa
                # if he outputting the xmlns attributes is relevenat or not

                # make the nsmap an ast dict
                keys = []
                values = []
                for key, value in options['nsmap'].items():
                    if isinstance(key, basestring):
                        keys.append(ast.Str(s=key))
                    elif key is None:
                        keys.append(ast.Name(id='None', ctx=ast.Load()))
                    values.append(ast.Str(s=value))

                # {'nsmap': {None: 'xmlns def'}}
                nsmap_ast_dict = ast.Dict(
                    keys=[ast.Str(s='nsmap')],
                    values=[ast.Dict(keys=keys, values=values)]
                )

                # options_.update(nsmap_ast_dict)
                content.append(
                    ast.Expr(ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id=name_options, ctx=ast.Load()),
                            attr='update',
                            ctx=ast.Load()
                        ),
                        args=[nsmap_ast_dict],
                        keywords=[], starargs=None, kwargs=None
                    ))
                )
        else:
            name_options = 'options'

        # self.compile($tmpl, options)(self, append, values_copy)
        content.append(
            ast.Expr(ast.Call(
                func=ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id='self', ctx=ast.Load()),
                        attr='compile',
                        ctx=ast.Load()
                    ),
                    args=[
                        self._compile_format(str(tmpl)),
                        ast.Name(id=name_options, ctx=ast.Load()),
                    ],
                    keywords=[], starargs=None, kwargs=None
                ),
                args=[
                    ast.Name(id='self', ctx=ast.Load()),
                    ast.Name(id='append', ctx=ast.Load()),
                    ast.Name(id=_values, ctx=ast.Load())
                ],
                keywords=[], starargs=None, kwargs=None
            ))
        )
        return content
