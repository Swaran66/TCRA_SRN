"""
The tcra fragility_rehab module contains function to perform
the workflow of read, discretize, initial, and transient
simulation for the given .inp file.

"""

class DamageProbabilityCalculator:
    """ This is Damage Probability Analysis class. This class estimates probabilities of various damage states.
    Parameters
    -------------------
    inp_file_name: building invetory, failure state keys that defines failure.
    """
    def __init__(self, failure_state_keys):
        self.failure_state_keys = failure_state_keys

    def calc_probability_failure_value(self, ds_sample):
        """Calculate the probability of failure given a sample of damage states.
        Parameters
        ----------
        ki : float or int or list, optional
            If given as float or int, set the value as wavespeed
            for all pipe; If given as list set the corresponding
            value to each pipe, by default 1200.
        dt : str or list, optional
            The list of pipe to define wavespeed,
            by default all pipe in the network.
        """
        count = 0
        func = {}
        for sample, state in ds_sample.items():
            if state in self.failure_state_keys:
                func[sample] = "0"
                count += 1
            else:
                func[sample] = "1"
        if len(ds_sample):
            return func, count / len(ds_sample)
        else:
            return func, np.nan

    def sample_damage_interval(self, bldg_result, damage_interval_keys, num_samples, seed):
        """Sample damage intervals for the given building results.
                Parameters
        ----------
        ki : float or int or list, optional
            If given as float or int, set the value as wavespeed
            for all pipe; If given as list set the corresponding
            value to each pipe, by default 1200.
        dt : str or list, optional
            The list of pipe to define wavespeed,
            by default all pipe in the network.
        """
        ki = []
        dt = []
        for i in range(len(bldg_result)):
            ds = {}
            dmg_row = bldg_result.iloc[i:i+1]
            random_generator = np.random.RandomState(seed)
            for j in range(num_samples):
                # each sample should have a unique seed
                rnd_num = random_generator.uniform(0, 1)
                prob_val = 0
                flag = True
                for ds_name in damage_interval_keys:
                    if rnd_num < prob_val + dmg_row[ds_name].values[0]:
                        ds[f'sample_{j}'] = ds_name
                        flag = False
                        break
                    else:
                        prob_val += dmg_row[ds_name].values[0]
                if flag:
                    print("Cannot determine MC damage state!")
                    break
            dt.append(self.calc_probability_failure_value(ds)[1])
            ki.append(dmg_row['id'].iloc[0])
        return dt, ki


class HurricaneParameters:
    """ This is Damage Probability Analysis class. This class estimates probabilities of various damage states.
    Parameters
    -------------------
    inp_file_name: building invetory, failure state keys that defines failure.
    """
    
    def __init__(self, data):
        self.data = data

    def estimate_parameters(self):
        # Initialize lists for parameters
        self.Lat = []          # Latitude
        self.Long = []         # Longitude
        self.CP = []           # Central Pressure (millibar)
        self.Δp = []           # Central Pressure Difference (millibar)
        self.Rmax = []         # Radius to max wind speed (km)
        self.B = []            # Holland Parameter
        self.ρ = []            # Air density
        self.Ω = []            # Earth's angular velocity (rad/s)

        # Calculate parameters for each row in data
        for _, row in self.data.iterrows():
            Lat = row['Lat']
            Long = row['Long']
            CP = row['CP']
            Δp = 1013 - CP
            Rmax = np.exp(2.556 - 0.000050255 * (Δp ** 2) + 0.042243032 * Lat)
            B = 1.881 - 0.00557 * Rmax - 0.01097 * Lat

            self.Lat.append(Lat)
            self.Long.append(Long)
            self.CP.append(CP)
            self.Δp.append(Δp)
            self.Rmax.append(Rmax)
            self.B.append(B)
            self.ρ.append(1.15)
            self.Ω.append(0.00007292)

        # Create a DataFrame from calculated parameters
        track = {
            'Lat': self.Lat,
            'Long': self.Long,
            'CP': self.CP,
            'Δp': self.Δp,
            'Rmax': self.Rmax,
            'B': self.B,
            'ρ': self.ρ,
            'Ω': self.Ω
        }

        df_track = pd.DataFrame(track)
        return df_track

    def calculate_wind_speeds(self, df_track, blg):
        Vmph = []

        # Calculate gradient wind speed for each hurricane data point
        for _, hurricane_row in df_track.iterrows():
            Lat_HE = np.radians(hurricane_row['Lat'])
            Long_HE = np.radians(hurricane_row['Long'])
            ρ = hurricane_row['ρ']
            B = hurricane_row['B']
            Rmax = hurricane_row['Rmax'] * 1000
            CP = hurricane_row['CP']
            Δp = hurricane_row['Δp'] * 100

            Vmph1 = []
            Vmph.append(Vmph1)

            # Calculate wind speed for each building
            for _, building_row in blg.iterrows():
                Lat = building_row['y']
                Long = building_row['x']
                Lat_rad = np.radians(Lat)
                Long_rad = np.radians(Long)
                delLat = Lat_HE - Lat_rad
                delLong = Long_HE - Long_rad

                a = np.sin(delLat / 2)**2 + np.cos(Lat_HE) * np.cos(Lat_rad) * np.sin(delLong / 2)**2
                rr = 2 * 6373 * np.arcsin(np.sqrt(a))
                r = rr * 1000  # Distance from hurricane eye to building

                f = 2 * 0.000073 * np.sin(Lat_rad)  # Coriolis parameter
                Vg = np.sqrt((((Rmax / r)**B) * ((B * Δp * np.exp(-(Rmax / r)**B)) / ρ)) + ((r**2) * (f**2) * 0.25)) - (r * f / 2)
                V = Vg * 2.2369362920544  # m/s to mph

                Vmph1.append(V)

        VG1 = pd.DataFrame(Vmph)
        VG = VG1 * 1.287 * 1.61  # Convert gradient wind speed to gust wind speed
        Vg=VG1.T

        V3s = Vg.max(axis=1) * 0.86 * 1.287  # Use coefficient 0.8-0.86 depending on hurricane intensity
        V3 = list(blg.id)
        vv = list(V3s.values)
        pf = {'ind': V3, 'mph': vv}
        nn = pd.DataFrame(pf)

        bldg_wind = blg.merge(nn, left_on='id', right_on='ind')
        return bldg_wind, VG
