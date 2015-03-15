# Adapted from http://stackoverflow.com/questions/110803/dirty-fields-in-django

from django.db.models.signals import post_save
from django.db.models.fields.related import ManyToManyField


class DirtyFieldsMixin(object):
    check_relationship = False

    def __init__(self, *args, **kwargs):
        super(DirtyFieldsMixin, self).__init__(*args, **kwargs)
        post_save.connect(
            reset_state, sender=self.__class__,
            dispatch_uid='{name}-DirtyFieldsMixin-sweeper'.format(
                name=self.__class__.__name__))
        reset_state(sender=self.__class__, instance=self)

    def _as_dict(self):
        all_field = {}

        for field in self._meta.local_fields:
            if not field.rel:
                all_field[field.name] = getattr(self, field.name)

        return all_field

    def get_dirty_fields(self, check_relationship=None):
        if check_relationship is None:
            check_relationship = self.check_relationship
        if check_relationship:
            # We want to check every field, including foreign keys and
            # one-to-one fields,
            new_state = entire_model_to_dict(self)
        else:
            new_state = self._as_dict()
        all_modify_field = {}

        for key, value in new_state.iteritems():
            original_value = self._original_state[key]
            if value != original_value:
                all_modify_field[key] = original_value

        return all_modify_field

    def is_dirty(self, check_relationship=None, fieldslist=None):
        if check_relationship is None:
            check_relationship = self.check_relationship
        # in order to be dirty we need to have been saved at least once, so we
        # check for a primary key and we need our dirty fields to not be empty
        if not self.pk:
            return True
        df = self.get_dirty_fields(check_relationship=check_relationship)
        if fieldslist:
            return bool([k for k in df if k in fieldslist])
        else:
            return bool(df)


class DirtyFieldsWithRelationshipChecksMixin(DirtyFieldsMixin):
    check_relationship = True


def reset_state(sender, instance, **kwargs):
    instance._original_state = entire_model_to_dict(instance)


def entire_model_to_dict(instance, fields=None, exclude=None):
    opts = instance._meta
    data = {}
    for f in opts.concrete_fields + opts.virtual_fields:
        if fields and f.name not in fields:
            continue
        if exclude and f.name in exclude:
            continue
        data[f.name] = f.value_from_object(instance)
    return data
