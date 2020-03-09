# Copyright 2019 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo.addons.cms_form.tests.utils import (
    fake_file_from_request,
    b64_as_stream,
)
from .common import TestWidgetCase, fake_form, fake_field

TEST_IMAGE_GIF = (
    'iVBORw0KGgoAAAANSUhEUgAAAA4AAAAPCAYAAADUFP50AAAABmJLR0QA/wD/AP+gvaeTAAAAC'
    'XBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH4wENCQc7YpV2jQAAAbtJREFUKM+dkr9rU3EUxT'
    '/3fb/vvfxoTKIJtlpoiZGkqQriFgsuipvQWdEi/j39N1zcXZRgFwc3h4JDIEqjtZXSGny/37s'
    'O0cEt9SwHLudwLude6fU7yn/A0aKgXK2RF1CvVeZDv8p6p0sYZWzcuEkaZly53KbVvkT5Qovm'
    'ko8Meqv68P42yUoXHe3ydmpoDndo7+9x++oPlu4+xk0Nw3tNXu6+Zuv5MziZ4ORiqXXXGcgxr'
    '/ZjACSPOJgeki1vwOGYnwl8OfhKmmWM9j7w7s0I6fU7miYJaMGt4QNWGh7jTx/5PD0iy4UkCv'
    'A8lzwHYx2kyElVkO71NW00GsxmM9IkJi8Ua12sNf+UkaYFrufAnyodAFVFVXE9H9/3sdagOlf'
    '85e2dHu5pxKOnd1grJcjm4Jr65SpFkREEIaVKhTgM8P0SURxTKfkEYUSeKdYz1DvLrB5PcJIs'
    'RwTCMEJEiMMQEOI4RoAwihERrOuAKvor5CS1WFVFRBY+/Nm3U87E4BhjyNw6FwkWMoqAAI4qH'
    'E3GbD15cb6X8z1LyYTMvjsU51jZSdIM09rEDd7P4xeE9Pod1TyjcCxm8UB+A5x0uaR5zMPmAA'
    'AAAElFTkSuQmCC'
)

TEST_IMAGE_JPG = (
    '/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMD'
    'AsKCwsNDhIQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGBIUFRT/2wBDAQMEBAUEBQkFBQkUDQsNFB'
    'QUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBT/wgARCAA'
    'KAAoDAREAAhEBAxEB/8QAFwAAAwEAAAAAAAAAAAAAAAAAAgMEB//EABkBAAIDAQAAAAAAAAAA'
    'AAAAAAMGAQIFCP/aAAwDAQACEAMQAAABz9M6UGapOvVB3f/EABkQAAMBAQEAAAAAAAAAAAAAA'
    'AECAwQRI//aAAgBAQABBQKYZ6UBSgPvtHNn/8QAJxEAAQIEAgsAAAAAAAAAAAAAAQIEAAMRIU'
    'FCBQYSFCIxUWFxsbL/2gAIAQMBAT8BdCW2bTOIitcSTyJtU9AbAiGLjbaSlVyjHt4jWBakuW6'
    'QbFM74jRyRuUm2VPqP//EAB8RAAIBAgcAAAAAAAAAAAAAAAABAgMEERIiIzJhsf/aAAgBAgEB'
    'PwGDzTWJUjrZbcW+16VXuSP/xAAcEAACAgIDAAAAAAAAAAAAAAABAgADESFxcrH/2gAIAQEAB'
    'j8CUKN8RlbTA4Ilcv7n2f/EABwQAQACAQUAAAAAAAAAAAAAAAEAESFBUXGBkf/aAAgBAQABPy'
    'G8BcDtiGrbbB1iAXhuzyAEKAwOU//aAAwDAQACAAMAAAAQpZ//xAAbEQEBAAMAAwAAAAAAAAA'
    'AAAABEQAhMUFR4f/aAAgBAwEBPxBh1D3QEEqNBAiklwkg1dtdjqhX2oXuPXKYLGWU8x5eZy75'
    'c//EAB8RAQABBAEFAAAAAAAAAAAAAAERACFBUWExgZGhsf/aAAgBAgEBPxBIIYTAHe3tnmozN'
    'uDfDHi1AYVyknUy/a//xAAYEAEBAQEBAAAAAAAAAAAAAAABESEAMf/aAAgBAQABPxAVEtAlQU'
    'RHUNG2bw1MmiKgmSI8QkJA4764GxsIAQA7/9k='
)


class TestWidgetBinary(TestWidgetCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].search([], limit=1)
        cls.form = fake_form(
            main_object=cls.partner
        )
        cls.maxDiff = None

    # TODO: we have only an image widget ATM -> add a file widget and test it
    def test_widget_binary_base(self):
        w_name, w_field = fake_field(
            'image',
            type='binary',
        )
        widget = self.get_widget(w_name, w_field, form=self.form,
                                 widget_model='cms.form.widget.image')
        node_items = self.to_xml_node(widget.render())
        self.assertEqual(len(node_items), 1)
        node_wrapper = node_items[0]
        expected_attrs = {
            'class': 'image-widget-wrapper',
        }
        self._test_element_attributes(
            node_wrapper, 'div', expected_attrs,
        )
        # no existing value so we get only the input
        self.assertEqual(len(node_wrapper.getchildren()), 1)
        node_input = node_wrapper.getchildren()[0]
        expected_attrs = {
            'type': 'file',
            'id': 'image',
            'name': 'image',
            'class': 'form-control',
            'capture': 'camera',
            'accept': 'image/*',
        }
        self._test_element_attributes(
            node_input, 'input', expected_attrs,
        )

    def test_widget_binary_load_from_record(self):
        w_name, w_field = fake_field(
            'image', type='binary',
        )
        widget = self.get_widget(w_name, w_field, form=self.form,
                                 widget_model='cms.form.widget.image')
        # test conversion
        self.assertEqual(widget.w_load(image=False), {})
        # set value on partner image
        self.partner.image = TEST_IMAGE_GIF
        self.assertEqual(widget.w_load(), {
            'value': 'data:image/png;base64,{}'.format(TEST_IMAGE_GIF),
            'raw_value': TEST_IMAGE_GIF,
            'mimetype': 'image/png',
            'from_request': False,
        })

    def test_widget_binary_load_from_request(self):
        w_name, w_field = fake_field(
            'image', type='binary',
        )
        widget = self.get_widget(w_name, w_field, form=self.form,
                                 widget_model='cms.form.widget.image')
        # test conversion
        self.assertEqual(widget.w_load(image=False), {})

        with b64_as_stream(TEST_IMAGE_JPG) as stream:
            req_image = fake_file_from_request(
                'image', stream=stream,
                filename='foo.jpg', content_type='image/jpeg'
            )
            self.assertEqual(widget.w_load(image=req_image), {
                'value': 'data:image/jpeg;base64,{}'.format(TEST_IMAGE_JPG),
                'raw_value': TEST_IMAGE_JPG,
                'mimetype': 'image/jpeg',
                'from_request': True,
            })

    def test_widget_binary_extract_string(self):
        w_name, w_field = fake_field(
            'image', type='binary',
        )
        widget = self.get_widget(w_name, w_field, form=self.form,
                                 widget_model='cms.form.widget.image')

        # no value in request -> None
        self.assertEqual(widget.w_extract(), None)
        # req value can come as string
        req_val = 'data:image/jpeg;base64,{}'.format(TEST_IMAGE_JPG)
        # value in request but no check flag -> None
        self.assertEqual(widget.w_extract(image=req_val), None)
        # value in request but keep flag is ON -> None
        self.assertEqual(
            widget.w_extract(image=req_val, image_keepcheck='yes'), None)
        # value in request but keep flag is ON -> None
        self.assertEqual(
            widget.w_extract(image=req_val, image_keepcheck='no'),
            TEST_IMAGE_JPG)

    def test_widget_binary_extract_filestorage(self):
        w_name, w_field = fake_field(
            'image', type='binary',
        )
        widget = self.get_widget(w_name, w_field, form=self.form,
                                 widget_model='cms.form.widget.image')

        # value in request but no check flag -> None
        with b64_as_stream(TEST_IMAGE_JPG) as stream:
            req_val = fake_file_from_request(
                'image', stream=stream,
                filename='foo.jpg', content_type='image/jpeg'
            )
            self.assertEqual(
                widget.w_extract(image=req_val, image_keepcheck='no'),
                TEST_IMAGE_JPG)

    def test_widget_binary_check_empty(self):
        w_name, w_field = fake_field(
            'image', type='binary',
        )
        widget = self.get_widget(w_name, w_field, form=self.form,
                                 widget_model='cms.form.widget.image')

        # no value at all -> empty
        self.assertIs(widget.w_check_empty_value(''), True)
        self.assertIs(widget.w_check_empty_value(False), True)
        # behavior w/ file value
        with b64_as_stream(TEST_IMAGE_JPG) as stream:
            req_val = fake_file_from_request(
                'image', stream=stream,
                content_type='image/jpeg'
            )
            # no filename -> empty
            self.assertIs(widget.w_check_empty_value(req_val), True)
            # no filename and keep flag -> empty, since we want to preserve
            self.assertIs(
                widget.w_check_empty_value(req_val, image_keepcheck='yes'),
                False
            )
            req_val = fake_file_from_request(
                'image', stream=stream,
                filename='foo.jpg', content_type='image/jpeg'
            )
            # got file w/ filename and no keep flag -> not empty
            self.assertIs(widget.w_check_empty_value(req_val), False)
            req_val = fake_file_from_request(
                'image', stream=stream,
                filename='foo.jpg', content_type='image/jpeg'
            )
            # got file w/ filename and yes keep flag -> not empty
            self.assertIs(
                widget.w_check_empty_value(req_val, image_keepcheck='yes'),
                False
            )
            # got file w/ filename and no keep flag -> not empty
            self.assertIs(
                widget.w_check_empty_value(req_val, image_keepcheck='no'),
                False
            )
            # got file w/ filename and yes keep flag -> not empty
            self.assertIs(
                widget.w_check_empty_value(req_val, image_keepcheck='yes'),
                False
            )
