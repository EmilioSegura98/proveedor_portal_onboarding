from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def create(self, vals):
        partner = super().create(vals)
        proveedor_tag = self.env.ref('base.res_partner_category_supplier', raise_if_not_found=False)

        if proveedor_tag and proveedor_tag.id in vals.get('category_id', []):
            partner._invite_as_portal_user()
        return partner

    def _invite_as_portal_user(self):
        portal_group = self.env.ref('base.group_portal')

        if not self.user_ids and self.email:
            user = self.env['res.users'].sudo().create({
                'name': self.name,
                'login': self.email,
                'email': self.email,
                'partner_id': self.id,
                'groups_id': [(6, 0, [portal_group.id])]
            })
            user.action_reset_password()

        self._trigger_marketing_and_documents()

    def _trigger_marketing_and_documents(self):
        # 1. Enviar correo de bienvenida
        template = self.env.ref('proveedor_portal_onboarding.email_template_bienvenida_proveedor', raise_if_not_found=False)
        if template:
            self.message_post_with_template(template.id)

        # 2. Crear solicitud de firma
        template_sign = self.env['sign.template'].browse(3)
        if template_sign:
            self.env['sign.request'].create({
                'template_id': 3,
                'request_item_ids': [(0, 0, {
                    'partner_id': self.id,
                    'role_id': template_sign.sign_item_ids[0].role_id.id,
                })],
                'reference': f'Solicitud Firma Proveedor {self.name}',
            })

        # 3. Crear solicitudes de documentos
        self._crear_solicitudes_documentos()

    def _crear_solicitudes_documentos(self):
        documentos_requeridos = [
            {
                'name': 'INE (Representante Legal)',
                'folder_id': 12,
                'description': 'Documento de identificación oficial del representante legal'
            },
            {
                'name': 'Carátula de Estado de Cuenta',
                'folder_id': 13,
                'description': 'Carátula de estado de cuenta (máximo 3 meses de antigüedad)'
            },
            {
                'name': 'Constancia de Situación Fiscal',
                'folder_id': 15,
                'description': 'Constancia de situación fiscal (máximo 3 meses de antigüedad)'
            },
            {
                'name': 'Comprobante de Domicilio',
                'folder_id': 16,
                'description': 'Comprobante de domicilio del proveedor (máximo 3 meses)'
            }
        ]

        DocumentRequest = self.env['documents.request']  # asegúrate de tener este modelo
        for doc in documentos_requeridos:
            DocumentRequest.create({
                'name': doc['name'],
                'partner_id': self.id,
                'folder_id': doc['folder_id'],
                'description': doc['description'],
            })
