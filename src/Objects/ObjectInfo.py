class ObjectInfo:
    def __init__(self, name, x, y):
        self.updates = {
                'x' : x,
                'y' : y,
                'coord' : (x,y),
                'nme' : name,
                'swim' : False,
                'ismoving' : False,
                'isattacking' : False, 
                'canmove' : True,

                'action' : {
                        'type' : None,
                        'target' :None,
                        'x' : None,
                        'y' : None,
                    }
            }

        self.stats = {
                'dmg' : 10,
                'lifesteal' : 0,
                'poison' : 0,

                'crit' : 1.1,
                'chance' : 50,

                'mgcdamage' : 18,
                'maxmgc' : 500,
                'mgc' : 500,
                'mgcregen' : 90,
                'mgcregenbonus' : 1,
                'mgcctnr' : 0,
                'mgcheal' : 5,
                'mgcburn' : 0.1,

                'arm' : 0,
                'thorns' : 0,

                'hlth' : 100,
                'mhlth' : 100,
                'regens' : 60,
                'regencntr' : 0,
                'regenbonus' : 1,

                'atc' : 30,
                'ats' : 30,

                'ress' : 300,
                'rescntr' : 0,

                'hinderedspeedmult' : 1,

                'speed' : 100,
                'swmspeed' : 50,

                'killcount' : 0,

                'attackingdist' : 50,
                'trackingdist' : 800,

                'maxenergy' : 100,
                'energy' : 100,
                'energyregen' : 120,
                'energycntr' : 0,
                'energyregenbonus' : 10,

                'energyconsumption' : 20,
                'energyconsumptionrate' : 30,
                'energyconsumptionratecntr' : 0,
                'lowenergyspeed' : 0.5,
            }