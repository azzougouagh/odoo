# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, tools, api

class MrpReport(models.Model):
    _name = "mrp.report"
    _description = "Mrp productions Statistics"
    _auto = False
    _rec_name = 'date'
    _order = 'date desc'

    name = fields.Char('order Reference', readonly=True)
    date = fields.Datetime('Date Order', readonly=True)
    product_uom = fields.Many2one('product.uom', 'Unit of Measure', readonly=True)

    product_consumed_id = fields.Many2one('product.product', 'Consumed product', readonly=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True)
    user_id = fields.Many2one('res.users', 'Responsible', readonly=True)
    qty_consumed = fields.Float("Qty", readonly=True)
    product_tmpl_id = fields.Many2one('product.template', 'Product Template', readonly=True)
    categ_id = fields.Many2one('product.category', 'Product Category', readonly=True)
    nbr = fields.Integer('# of Lines', readonly=True)
    state = fields.Selection([
        ('confirmed', 'Confirmed'),
        ('planned', 'Planned'),
        ('progress', 'In Progress'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')], string='State',
        copy=False, default='confirmed', track_visibility='onchange')

    def hada_test(self):
        print('this is my branch')
    # def _select(self):
    #     select_str = """
    #          SELECT min(l.id) as id,
    #                 l.product_id as product_consumed_id,
    #     """
    #     return select_str

    # def _from(self):
    #     from_str = """
    #             stock_move l
    #     """

    #     return from_str



    # @api.model_cr
    # def init(self):
    #     self._table = "mrp_report"
    #     tools.drop_view_if_exists(self.env.cr, self._table)
    #     self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s FROM  "%s  )""" % (self._table, self._select(), self._from()))

    def _select(self):
        select_str = """
             SELECT min(l.id) as id,
                    l.product_id as product_consumed_id,
                    t.uom_id as product_uom,
                    sum(l.product_uom_qty / u.factor * u2.factor) as qty_consumed,
                    count(*) as nbr,
                    s.name as name,
                    s.date_planned_start as date,
                    s.state as state,
                    s.user_id as user_id,
                    s.company_id as company_id,
                    t.categ_id as categ_id,
                    p.product_tmpl_id
        """
        return select_str

    def _from(self):
        from_str = """stock_move l
                      join mrp_production s on (l.raw_material_production_id=s.id)
                        left join product_product p on (l.product_id=p.id)
                            left join product_template t on (p.product_tmpl_id=t.id)
                    left join product_uom u on (u.id=l.product_uom)
                    left join product_uom u2 on (u2.id=t.uom_id)
        """

        return from_str

    def _group_by(self):
        group_by_str = """
            GROUP BY l.product_id,
                    l.raw_material_production_id,
                    t.uom_id,
                    t.categ_id,
                    s.name,
                    s.date_planned_start,
                    s.user_id,
                    s.state,
                    s.company_id,
                    p.product_tmpl_id
        """
        return group_by_str

    @api.model_cr
    def init(self):
        self._table = "mrp_report"
        tools.drop_view_if_exists(self.env.cr, self._table)
        sql_request = ("""CREATE or REPLACE VIEW %s as (%s FROM  %s  %s )""" % (self._table, self._select(), self._from(), self._group_by()))
        self.env.cr.execute(sql_request)
