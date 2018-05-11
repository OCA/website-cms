import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo10-addons-oca-website-cms",
    description="Meta package for oca-website-cms Odoo addons",
    version=version,
    install_requires=[
        'odoo10-addon-cms_delete_content',
        'odoo10-addon-cms_delete_content_example',
        'odoo10-addon-cms_form',
        'odoo10-addon-cms_form_example',
        'odoo10-addon-cms_info',
        'odoo10-addon-cms_status_message',
        'odoo10-addon-cms_status_message_example',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
