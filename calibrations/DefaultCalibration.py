import re

class DefaultCalibration:
    """
    Default meas.ini file generator from Exopy template and assumptions file
    A placeholder must have the format '$param' or '$section/param' where
    <section> and <param> are alphanumeric strings ('a'-'z', 'A'-'Z', '0'-'9', '_')
    """
    def __init__(self, template, assumptions, calib_id, calib_name, substitutions):
        keys = re.findall(r'\$[a-zA-Z_/]+', template, re.MULTILINE) # placeholders
        paths = [key[1:].split('/') for key in keys] # strip leading '$' and split at '/'
        
        # handle substitutions
        for i, key in enumerate(paths):
            for j, part in enumerate(key):
                if part in substitutions:
                    paths[i][j] = substitutions[part]
        for src, dst in substitutions.items():
            template = template.replace(src, dst)
        
        # handle placeholders
        for key in paths:
                val = 'MISSING_ASSUMPTION'
                if key[0] in assumptions.keys():
                    if len(key) > 1:
                        if key[1] in assumptions[key[0]].keys():
                            val = str(assumptions[key[0]][key[1]])
                        else:
                            raise Exception('Missing assumption "{}"'.format('/'.join(key)))
                    else:
                        val = str(assumptions[key[0]])
                else:
                    raise Exception('Missing assumption "{}"'.format('/'.join(key)))
                token = '$'+'/'.join(key)
                if token == '$filename':
                    val = '{:03d}_{}.h5'.format(calib_id, calib_name)
                print('    {} = {}'.format(token, val))
                template = template.replace(token, val)
            
        with open('calibrations/{}/{}.meas.ini'.format(calib_name, calib_name), 'w') as f:
            f.write(template)
            
        self.keys = keys
        self.result = {}
        self.calib_id = calib_id
        self.calib_name = calib_name