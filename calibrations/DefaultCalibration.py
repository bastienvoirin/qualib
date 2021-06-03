import re

class DefaultCalibration:
    """
    Default meas.ini file generator from Exopy template and assumptions file
    A placeholder must have the format '$param' or '$section/param' where
    <section> and <param> are alphanumeric strings ('a'-'z', 'A'-'Z', '0'-'9', '_')
    """
    def __init__(self, template, assumptions, calib_id, calib_name, substitutions):
        keys = re.findall(r'\$[a-zA-Z_/]+', template, re.MULTILINE) # placeholders
        splt = [key[1:].split('/') for key in keys] # strip leading '$' and split at '/'
        
        # handle substitutions
        for i, key in enumerate(splt):
            for j, part in enumerate(key):
                if part in substitutions:
                    splt[i][j] = substitutions[part]
        for src, dst in substitutions.items():
            template = template.replace(src, dst)
        
        # handle placeholders
        for i, key in enumerate(splt):
                val = 'MISSING_ASSUMPTION'
                if key[0] in assumptions.keys():
                    # $section/parameter
                    if len(key) > 1:
                        if key[1] in assumptions[key[0]].keys():
                            val = str(assumptions[key[0]][key[1]])
                        else:
                            raise Exception(f'Missing assumption "{"/".join(key)}"')
                    # $parameter
                    else:
                        val = str(assumptions[key[0]])
                else:
                    raise Exception('Missing assumption "{}"'.format('/'.join(key)))
                token = keys[i]
                if token == '$filename':
                    val = f'{calib_id:03d}_{calib_name}.h5'
                print(f'    {token} = {val}')
                template = template.replace(token, val)
            
        with open(f'calibrations/{calib_name}/{calib_name}.meas.ini', 'w') as f:
            f.write(template)
            
        self.keys = keys # list of placeholders
        self.result = {}
        self.calib_id = calib_id
        self.calib_name = calib_name