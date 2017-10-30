import setuptools

setuptools.setup(
    setup_requires=['setuptools-odoo'],
    odoo_addon={'odoo_version_override': '10.0'},
    include_package_data=True,
    package_data={'': ['*', ]}
)
