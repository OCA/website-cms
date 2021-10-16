import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo9-addons-oca-website-cms",
    description="Meta package for oca-website-cms Odoo addons",
    version=version,
    install_requires=[
        'odoo9-addon-cms_delete_content',
        'odoo9-addon-cms_form',
        'odoo9-addon-cms_form_example',
        'odoo9-addon-cms_notification',
        'odoo9-addon-cms_status_message',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 9.0',
    ]
)
