import codecs

def parse_params(params_file_path):
    with codecs.open(params_file_path, encoding='utf-8') as fparams:
        params = {}
        line_idx = 0
        for line in fparams:
            line_idx += 1
            line_strip = line.strip()
            if len(line_strip) == 0:
                continue
            sharp_position = line_strip.find('#')
            if sharp_position > 0:
                line_strip = line_strip[:sharp_position]
            if len(line_strip) == 0:
                continue
            equal_position = line_strip.find('=')
            colon_position = line_strip.find(':')
            assert ((equal_position>0 or colon_position>0) 
                    and (not (equal_position>0 and colon_position>0))), 'The format does not match <param>: <value> or <param>= <value> on line %d'%line_idx
            if equal_position>0:
                items = line_strip.split('=')
                assert len(items) == 2, 'The format does not match <param>: <value> or <param>= <value> on line %d'%line_idx
                param, value = items
                param = param.strip()
                value = value.strip()
                params[param] = value
            elif colon_position>0:
                items = line_strip.split(':')
                assert len(items) == 2, 'The format does not match <param>: <value> or <param>= <value> on line %d'%line_idx
                param, value = items
                param = param.strip()
                value = value.strip()
                params[param] = value
            return params
        return None
