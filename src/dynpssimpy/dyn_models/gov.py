from dynpssimpy.dyn_models.blocks import *


class GOV:
    def connections(self):
        return [
            {
                'input': 'input',
                'source': {
                    'container': 'gen',
                    'mdl': '*',
                    'id': self.par['gen'],
                },
                'output': 'speed',
            },
            {
                'output': 'output',
                'destination': {
                    'container': 'gen',
                    'mdl': '*',
                    'id': self.par['gen'],
                },
                'input': 'P_m',
            }
        ]



class TGOV1(DAEModel, GOV):
    def add_blocks(self):
        p = self.par
        self.droop = Gain(K=1/p['R'])
        self.time_constant_lim = TimeConstantLims(T=p['T_1'], V_min=p['V_min'], V_max=p['V_max'])
        self.lead_lag = LeadLag(T_1=p['T_2'], T_2=p['T_3'])
        self.damping_gain = Gain(K=p['D_t'])

        self.droop.input = lambda x, v: -self.input(x, v) + self.int_par['bias']
        self.time_constant_lim.input = lambda x, v: self.droop.output(x, v)
        self.lead_lag.input = lambda x, v: self.time_constant_lim.output(x, v)
        self.damping_gain.input = lambda x, v: self.input(x, v)

        self.output = lambda x, v: self.lead_lag.output(x, v) - self.damping_gain.output(x, v)

    def int_par_list(self):
        return ['bias']

    def init_from_connections(self, x0, v0, output_0):
        p = self.par
        self.int_par['bias'] = self.droop.initialize(
            x0, v0, self.time_constant_lim.initialize(
                x0, v0, self.lead_lag.initialize(x0, v0, output_0['output'])
            )
        )