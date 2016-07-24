from recurrence.fields import RecurrenceField
from django.db.models import fields

import re
import recurrence

class MoneypatchedRecurrenceField(RecurrenceField):
    strip_time = re.compile(r'T\d{6}')

    def to_python(self, value):
        if value is None or isinstance(value, recurrence.Recurrence):
            return value
        value = self.strip_time.sub('', value)  # HACKS
        return recurrence.deserialize(value)