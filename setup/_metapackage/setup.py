import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo11-addons-oca-website-cms",
    description="Meta package for oca-website-cms Odoo addons",
    version=version,
    install_requires=[
        'odoo11-addon-cms_account_form',
        'odoo11-addon-cms_delete_content',
        'odoo11-addon-cms_delete_content_example',
        'odoo11-addon-cms_form',
        'odoo11-addon-cms_form_example',
        'odoo11-addon-cms_info',
        'odoo11-addon-cms_notification',
        'odoo11-addon-cms_status_message',
        'odoo11-addon-cms_status_message_example',
        'odoo11-addon-cms_toolbar',
        'odoo11-addon-cms_toolbar_example',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
