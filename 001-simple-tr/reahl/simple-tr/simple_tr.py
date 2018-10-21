from __future__ import print_function, unicode_literals, absolute_import, division

from reahl.sqlalchemysupport import Session, Base, session_scoped
from reahl.webdeclarative.webdeclarative import UserSession


from reahl.web.fw import UserInterface, Widget
from reahl.web.bootstrap.ui import HTML5Page, TextNode, Div, H, P, FieldSet
from reahl.web.bootstrap.navbar import Navbar, ResponsiveLayout
from reahl.web.bootstrap.grid import Container
from reahl.web.bootstrap.forms import TextInput, Form, FormLayout, Button, ButtonLayout
from reahl.component.modelinterface import exposed, Field, EmailField, Action, Event
from reahl.sqlalchemysupport import Session, Base
from sqlalchemy import Column, Integer, UnicodeText
from sqlalchemy.orm import relationship


class TR(Base):
    __tablename__ = 'simple_tr_tr'

    id            = Column(Integer, primary_key=True)
    input_text    = Column(UnicodeText)
    separator     = Column(UnicodeText)
    joiner        = Column(UnicodeText)

    @exposed
    def fields(self, fields):
        fields.input_text = Field(label='Input Text', required=True)
        fields.separator  = Field(label='Separated by (Regular Expression)', required=True)
        fields.joiner     = Field(label='Join with (Character String)', required=True)

    def save(self):
        Session.add(self)

    @classmethod
    def has_session_data(cls):
        record = Session.query(__class__).order_by(TR.id.desc()).first()
        return record

    @exposed('save')
    def events(self, events):
        events.save = Event(label='Perform Tr', action=Action(self.save))


class MyPage(HTML5Page):
    def __init__(self, view):
        super(__class__, self).__init__(view)


        self.body.use_layout(Container())

        layout = ResponsiveLayout('md', colour_theme='dark', bg_scheme='primary')
        navbar = Navbar(view, css_id='my_nav').use_layout(layout)
        navbar.layout.set_brand_text('Simple TR')
        navbar.layout.add(TextNode(view, 'Translate from this to that.'))

        self.body.add_child(navbar)
        self.body.add_child(MyPanel(view))


class InputForm(Form):
    def __init__(self, view):
        super(__class__, self).__init__(view, 'address_form')

        inputs = self.add_child(FieldSet(view, legend_text='Enter data then click button'))
        inputs.use_layout(FormLayout())

        tr = TR(separator='\\s+', joiner='-')
        inputs.layout.add_input(TextInput(self, tr.fields.input_text))
        inputs.layout.add_input(TextInput(self, tr.fields.separator))
        inputs.layout.add_input(TextInput(self, tr.fields.joiner))
        self.tr = tr

        button = inputs.add_child(Button(self, tr.events.save))
        button.use_layout(ButtonLayout(style='primary'))


class MyPanel(Div):
    def __init__(self, view):
        super(__class__, self).__init__(view)

        my_form = InputForm(view)
        self.add_child(my_form)

        self.add_child(OutputBox(view, my_form))


class OutputBox(Widget):
    def __init__(self, view, form):
        super(__class__, self).__init__(view)
        tr = TR.has_session_data()
        if tr is not None:
            import re
            new_str = re.sub(tr.separator, tr.joiner, tr.input_text)
            self.add_child(P(view, text=new_str))

class MyUI(UserInterface):
    def assemble(self):

        home = self.define_view('/', title='x marksthe spot', page=MyPage.factory())
        self.define_transition(TR.events.save, home, home)
