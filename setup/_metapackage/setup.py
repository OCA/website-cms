import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo13-addons-oca-website-cms",
    description="Meta package for oca-website-cms Odoo addons",
    version=version,
    install_requires=[
        'odoo13-addon-cms_delete_content',
        'odoo13-addon-cms_delete_content_example',
        'odoo13-addon-cms_form',
        'odoo13-addon-cms_form_example',
        'odoo13-addon-cms_info',
        'odoo13-addon-cms_status_message',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 13.0',
    ]
)
