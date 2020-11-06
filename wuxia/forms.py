def gen_form_item(id, name=None, item_class=None, placeholder=None,
                  required=False, item_type='text', autocomplete='off',
                  field_type='input', label='', options={}, value='',
                  selected_option=''):
    item = {
        'id': id,
        'name': name if name else id,
        'class': item_class,
        'placeholder': placeholder if placeholder else id,
        'required': required,
        'type': item_type,
        'value': value,
        'autocomplete': autocomplete,
        'field_type': field_type,
        'label': label,
        'options': options,
        'selected_option': selected_option,
    }

    return item


def gen_options(options, values=[]):
    option_dict = {}
    for idx, opt in enumerate(options):
        if values:
            option_dict[opt] = {
                'value': values[idx],
                'text': opt
            }
        else:
            option_dict[opt] = {
                'value': opt,
                'text': opt
            }
    print(option_dict)
    return option_dict
