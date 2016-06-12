import re
import colour
from datetime import datetime
from flask.ext.restplus.fields import Raw, Nested, List


EMAIL_REGEX = re.compile(r'\S+@\S+\.\S+')
URI_REGEX = re.compile(r'(http|https|ftp)://\S+\.\S+')


class CustomField(Raw):
    """
    Custom Field base class with validate feature
    """
    __schema_type__ = 'string'
    validation_error = 'Validation of %s field failed'

    def __init__(self, *args, **kwargs):
        super(CustomField, self).__init__(**kwargs)
        # custom params
        self.positive = kwargs.get('positive', True)

    def format(self, value):
        """
        format the text in database for output
        works only for GET requests
        """
        if not self.validate(value):
            print 'Validation of field with value \"%s\" (%s) failed' % (
                value, str(self.__class__.__name__))
            # raise MarshallingError
            # disabling for development purposes as the server crashes when
            # exception is raised. can be enabled when the project is mature
        if self.__schema_type__ == 'string':
            return unicode(value)
        else:
            return value

    def validate_empty(self):
        """
        Return when value is empty or null
        """
        if self.required:
            self.validation_error = 'Required field %s. Cannot be null or empty'
            return False
        else:
            return True

    def validate(self, value):
        """
        Validate the value. return True if valid
        """
        pass


class Email(CustomField):
    """
    Email field
    """
    __schema_format__ = 'email'
    __schema_example__ = 'email@domain.com'

    def validate(self, value):
        if not value:
            return self.validate_empty()
        if not EMAIL_REGEX.match(value):
            self.validation_error = 'Invalid Email in %s'
            return False
        return True


class Uri(CustomField):
    """
    URI (link) field
    """
    __schema_format__ = 'uri'
    __schema_example__ = 'http://website.com'

    def validate(self, value):
        if not value:
            return self.validate_empty()
        if not URI_REGEX.match(value):
            self.validation_error = 'Invalid Url in %s'
            return False
        return True


class ImageUri(Uri):
    """
    Image URL (url ends with image.ext) field
    """
    __schema_example__ = 'http://website.com/image.ext'


class Color(CustomField):
    """
    Color (or colour) field
    """
    __schema_format__ = 'color'
    __schema_example__ = 'green'

    def validate(self, value):
        if not value:
            return self.validate_empty()
        try:
            # using the same colour package used by sqlalchemy and wtforms
            colour.Color(value)
        except Exception:
            self.validation_error = 'Invalid Color in %s'
            return False
        return True


class DateTime(CustomField):
    """
    Custom DateTime field
    """
    __schema_format__ = 'date-time'
    __schema_example__ = '2016-06-06 11:22:33'
    dt_format = '%Y-%m-%d %H:%M:%S'

    def to_str(self, value):
        return None if not value \
            else unicode(value.strftime(self.dt_format))

    def from_str(self, value):
        return None if not value \
            else datetime.strptime(value, self.dt_format)

    def format(self, value):
        return self.to_str(value)

    def validate(self, value):
        if not value:
            return self.validate_empty()
        try:
            if value.__class__.__name__ in ['unicode', 'str']:
                self.from_str(value)
            else:
                self.to_str(value)
        except Exception:
            self.validation_error = 'Incorrect format of datetime used in %s field. Should be YYYY-MM-DD HH:MM:SS'
            return False
        return True


class String(CustomField):
    """
    Custom String Field
    """
    def validate(self, value):
        if not value:
            return self.validate_empty()
        if value.__class__.__name__ in ['unicode', 'str']:
            return True
        else:
            self.validation_error = '%s should be a String'
            return False


class Integer(CustomField):
    """
    Custom Integer Field
    Args:
        :positive - accept only positive numbers, True by default
    """
    __schema_type__ = 'integer'
    __schema_format__ = 'int'
    __schema_example__ = 0

    def validate(self, value):
        if value is None:
            return self.validate_empty()
        if type(value) != int:
            self.validation_error = '%s should be an Integer'
            return False
        if self.positive and value < 0:
            self.validation_error = '%s should be a positive Integer'
            return False
        return True


class Float(CustomField):
    """
    Custom Float Field
    """
    __schema_type__ = 'number'
    __schema_format__ = 'float'
    __schema_example__ = 0.0

    def validate(self, value):
        if value is None:
            return self.validate_empty()
        try:
            float(value)
            return True
        except Exception:
            self.validation_error = '%s should be a Number'
            return False
