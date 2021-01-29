def gen_form_item(id, name=None, placeholder=None,
                  required=False, item_type='text', autocomplete='off',
                  field_type='input', label='', options={}, value='',
                  selected_option='', item_class='', label_class='',
                  field_class='', href=''):
    item = {
        'id': id,
        'name': name if name else id,
        'item_class': item_class,
        'label_class': label_class,
        'field_class': field_class,
        'placeholder': placeholder if placeholder else '',
        'required': required,
        'type': item_type,
        'value': value,
        'autocomplete': autocomplete,
        'field_type': field_type,
        'label': label,
        'options': options,
        'selected_option': selected_option,
        'href': href
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
