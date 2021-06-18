from ..default import DefaultCalibration, DefaultJupyterReport
import json
import re

class Calibration(DefaultCalibration):
    def __init__(self, log, template, assumptions, calib_id, calib_name, subs_name, subs_misc, timestamp):
        self.log = log
        self.pre = ''.join([calib_name, '_'+subs_name if subs_name else '', ':'])
        keys = re.findall(r'\$[a-zA-Z0-9_/]+', template, re.MULTILINE) # Placeholders
        
        # Handle substitutions
        self.log.info(f'{self.pre} Handling "qualib/calibrations/{calib_name}/{calib_name}_template.meas.ini" substitutions')
        for i, key in enumerate(keys):
            for src, dst in subs_misc.items():
                keys[i] = keys[i].replace(src, dst)
        for src, dst in subs_misc.items():
            template = template.replace(src, dst)
        
        ####################################
        # Calibration-specific

        sweep_width = assumptions['spectro_qubit'][f'{subs_misc["TYPE"]}_sweep_width']
        sweep_npoints = assumptions['spectro_qubit'][f'{subs_misc["TYPE"]}_npoints']
        new_keys = []
        for key in keys:
            if 'SWEEP_STEP' in key:
                template = template.replace(key, f'{sweep_width/(sweep_npoints-1):.4f}')
            elif 'SWEEP_HALF_WIDTH' in key:
                template = template.replace(key, str(sweep_width/2))
            else:
                new_keys.append(key)
        keys = new_keys

        # Calibration-specific
        ####################################
            
        # Handle placeholders
        self.log.info(f'{self.pre} Handling "qualib/calibrations/{calib_name}/{calib_name}_template.meas.ini" placeholders')
        for key in keys:
            splt = key[1:].split('/') # Strip leading '$' and split at '/'
            val = 'MISSING_ASSUMPTION'
            assert splt[0] in assumptions.keys(), f'Missing assumption "{key[1:]}"'
            if len(splt) > 1: # $section/parameter
                assert splt[1] in assumptions[splt[0]].keys(), f'Missing assumption "{key[1:]}"'
                val = str(assumptions[splt[0]][splt[1]])
            else: # $parameter
                val = str(assumptions[splt[0]])
            if key == '$filename':
                val = f'{timestamp}_{calib_id:03d}_{calib_name}{"_"+subs_name if subs_name else ""}.h5'
            #print(f'    {key} = {val}')
            template = template.replace(key, val)
            
        meas_path = f'qualib/calibrations/{calib_name}/{calib_name}.meas.ini'
        self.log.info(f'{self.pre} Generating "{meas_path}"')
        with open(meas_path, 'w') as f:
            f.write(template)
            
        self.keys = keys
        self.results = {}
        self.calib_id = calib_id
        self.calib_name = calib_name

    def pre_process():
        pass

    def process(self, calib_name, calib_id, subs_name, subs_misc, report_filename, timestamp, assumptions):
        """
        Analyze and report the current calibration
        """
        repl = {
            'PULSE_LENGTH': str(assumptions['spectro_qubit'][f'{subs_name}_pulse_length']),
            'PULSE_AMP': str(assumptions['spectro_qubit'][f'{subs_name}_pulse_amp'])
        }
        cells = self.pre_process(calib_name, calib_id, subs_name, subs_misc, timestamp, assumptions, repl)
        
        assumptions['qubit']['freq'] = self.results['freq']
        
        repl = {
            '§TYPE§': subs_misc['TYPE'],
            '§FREQ§': f'{self.results["freq"]:f}',
        }
        return cells

    def post_process(calib_name, report_filename, cells):
        repl = {
            '§TYPE§': subs_misc['TYPE'],
            '§FREQ§': f'{self.results["freq"]:f}',
        }
        super().post_process(calib_name, report_filename, cells)