def gen_form_item(id, name=None, placeholder=None, required=False,
                  item_type='text', value='', autocomplete='off',
                  field_type='input', label='', options={},
                  selected_option=''):
    item = {
        'id': id,
        'name': name if name else id,
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
