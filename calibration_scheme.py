[
    {"name": "rabi", "substitutions": [{"name": "uncond_pi2",
                                        "repl": {"PULSE": "unconditional_pi2_pulse",
                                                 "TYPE":  "unconditional pi/2 pulse"}},
                                       {"name": "uncond_pi",
                                        "repl": {"PULSE": "unconditional_pi_pulse",
                                                 "TYPE":  "unconditional pi pulse"}},
                                       {"name": "cond_pi",
                                        "repl": {"PULSE": "conditional_pi_pulse",
                                                 "TYPE":  "conditional pi pulse"}}]},
    {"name": "spectro_qubit", "substitutions": [{"name": "coarse",
                                                 "repl": {"TYPE": "coarse"}},
                                                {"name": "fine",
                                                 "repl": {"TYPE": "fine"}}]}
]
