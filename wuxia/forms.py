def gen_form_item(id, name=None, placeholder=None, required=False,
                  item_type='text', value='', autocomplete='off'):
    item = {
        'id': id,
        'name': name if name else id,
        'placeholder': placeholder if placeholder else id,
        'required': required,
        'type': item_type,
        'value': value,
        'autocomplete': autocomplete,
    }

    return item
