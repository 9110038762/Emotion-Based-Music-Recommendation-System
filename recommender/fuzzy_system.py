import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64

class EmotionFuzzySystem:
    def __init__(self):
        # 1. Define Antecedents (Inputs: 0.0 to 10.0)
        self.valence_in = ctrl.Antecedent(np.arange(0, 10.1, 0.1), 'valence_in')
        self.arousal_in = ctrl.Antecedent(np.arange(0, 10.1, 0.1), 'arousal_in')

        # 2. Define Consequents (Outputs: 0.0 to 1.0)
        self.valence_out = ctrl.Consequent(np.arange(0, 1.01, 0.01), 'valence_out')
        self.energy_out = ctrl.Consequent(np.arange(0, 1.01, 0.01), 'energy_out')
        self.dance_out = ctrl.Consequent(np.arange(0, 1.01, 0.01), 'dance_out')
        self.tempo_out = ctrl.Consequent(np.arange(0, 1.01, 0.01), 'tempo_out')

        # 3. Setup Membership Functions (Triangular)
        # Inputs: User Valence (Sad -> Happy)
        self.valence_in['low'] = fuzz.trimf(self.valence_in.universe, [0, 0, 5])
        self.valence_in['medium'] = fuzz.trimf(self.valence_in.universe, [2.5, 5, 7.5])
        self.valence_in['high'] = fuzz.trimf(self.valence_in.universe, [5, 10, 10])

        # Inputs: User Arousal (Calm/Sleepy -> Energetic/Tense)
        self.arousal_in['low'] = fuzz.trimf(self.arousal_in.universe, [0, 0, 5])
        self.arousal_in['medium'] = fuzz.trimf(self.arousal_in.universe, [2.5, 5, 7.5])
        self.arousal_in['high'] = fuzz.trimf(self.arousal_in.universe, [5, 10, 10])

        # Outputs: Track Valence
        self.valence_out['low'] = fuzz.trimf(self.valence_out.universe, [0, 0, 0.5])
        self.valence_out['medium'] = fuzz.trimf(self.valence_out.universe, [0.25, 0.5, 0.75])
        self.valence_out['high'] = fuzz.trimf(self.valence_out.universe, [0.5, 1.0, 1.0])

        # Outputs: Track Energy
        self.energy_out['low'] = fuzz.trimf(self.energy_out.universe, [0, 0, 0.5])
        self.energy_out['medium'] = fuzz.trimf(self.energy_out.universe, [0.25, 0.5, 0.75])
        self.energy_out['high'] = fuzz.trimf(self.energy_out.universe, [0.5, 1.0, 1.0])

        # Outputs: Track Danceability
        self.dance_out['low'] = fuzz.trimf(self.dance_out.universe, [0, 0, 0.5])
        self.dance_out['medium'] = fuzz.trimf(self.dance_out.universe, [0.25, 0.5, 0.75])
        self.dance_out['high'] = fuzz.trimf(self.dance_out.universe, [0.5, 1.0, 1.0])

        # Outputs: Track Tempo (Normalized)
        self.tempo_out['low'] = fuzz.trimf(self.tempo_out.universe, [0, 0, 0.5])
        self.tempo_out['medium'] = fuzz.trimf(self.tempo_out.universe, [0.25, 0.5, 0.75])
        self.tempo_out['high'] = fuzz.trimf(self.tempo_out.universe, [0.5, 1.0, 1.0])

        # 4. Define Rules
        self.rules = self._create_rules()

        # 5. Create Control System & Simulator
        self.system = ctrl.ControlSystem(self.rules)
        self.simulator = ctrl.ControlSystemSimulation(self.system)

    def _create_rules(self):
        """
        Creates 9 rules representing all combinations of Valence (Low, Med, High)
        and Arousal (Low, Med, High).
        """
        # R1: Low Valence + Low Arousal (Sad/Lethargic) -> L Valence, L Energy, L Dance, L Tempo
        r1 = ctrl.Rule(self.valence_in['low'] & self.arousal_in['low'],
                       (self.valence_out['low'], self.energy_out['low'], self.dance_out['low'], self.tempo_out['low']))
        
        # R2: Low Valence + Med Arousal (Gloomy/Heavy) -> L Valence, M Energy, L Dance, M Tempo
        r2 = ctrl.Rule(self.valence_in['low'] & self.arousal_in['medium'],
                       (self.valence_out['low'], self.energy_out['medium'], self.dance_out['low'], self.tempo_out['medium']))
        
        # R3: Low Valence + High Arousal (Angry/Tense) -> L Valence, H Energy, M Dance, H Tempo
        r3 = ctrl.Rule(self.valence_in['low'] & self.arousal_in['high'],
                       (self.valence_out['low'], self.energy_out['high'], self.dance_out['medium'], self.tempo_out['high']))
        
        # R4: Med Valence + Low Arousal (Mellow/Nostalgic) -> M Valence, L Energy, L Dance, L Tempo
        r4 = ctrl.Rule(self.valence_in['medium'] & self.arousal_in['low'],
                       (self.valence_out['medium'], self.energy_out['low'], self.dance_out['low'], self.tempo_out['low']))
        
        # R5: Med Valence + Med Arousal (Neutral/Balanced) -> M Valence, M Energy, M Dance, M Tempo
        r5 = ctrl.Rule(self.valence_in['medium'] & self.arousal_in['medium'],
                       (self.valence_out['medium'], self.energy_out['medium'], self.dance_out['medium'], self.tempo_out['medium']))
        
        # R6: Med Valence + High Arousal (Alert/Driving) -> M Valence, H Energy, M Dance, H Tempo
        r6 = ctrl.Rule(self.valence_in['medium'] & self.arousal_in['high'],
                       (self.valence_out['medium'], self.energy_out['high'], self.dance_out['medium'], self.tempo_out['high']))
        
        # R7: High Valence + Low Arousal (Calm/Peaceful) -> H Valence, L Energy, M Dance, L Tempo
        r7 = ctrl.Rule(self.valence_in['high'] & self.arousal_in['low'],
                       (self.valence_out['high'], self.energy_out['low'], self.dance_out['medium'], self.tempo_out['low']))
        
        # R8: High Valence + Med Arousal (Happy/Chilled) -> H Valence, M Energy, H Dance, M Tempo
        r8 = ctrl.Rule(self.valence_in['high'] & self.arousal_in['medium'],
                       (self.valence_out['high'], self.energy_out['medium'], self.dance_out['high'], self.tempo_out['medium']))
        
        # R9: High Valence + High Arousal (Excited/Joyful) -> H Valence, H Energy, H Dance, H Tempo
        r9 = ctrl.Rule(self.valence_in['high'] & self.arousal_in['high'],
                       (self.valence_out['high'], self.energy_out['high'], self.dance_out['high'], self.tempo_out['high']))
        
        return [r1, r2, r3, r4, r5, r6, r7, r8, r9]

    def evaluate(self, valence_val, arousal_val):
        """
        Executes the fuzzy inference engine for given inputs.
        """
        # Ensure inputs are constrained to [0, 10]
        valence_val = float(np.clip(valence_val, 0.0, 10.0))
        arousal_val = float(np.clip(arousal_val, 0.0, 10.0))

        # Set input values in the simulator
        self.simulator.input['valence_in'] = valence_val
        self.simulator.input['arousal_in'] = arousal_val
        
        # Perform defuzzification
        self.simulator.compute()
        
        # Return target audio features
        return {
            'valence': float(self.simulator.output['valence_out']),
            'energy': float(self.simulator.output['energy_out']),
            'danceability': float(self.simulator.output['dance_out']),
            'tempo': float(self.simulator.output['tempo_out'])
        }

    def get_all_plots_base64(self, val_val=None, aro_val=None, outputs=None):
        """
        Generates a 2x3 grid of matplotlib plots visualizing inputs and outputs,
        returning it as a base64 encoded PNG string.
        """
        fig, axes = plt.subplots(2, 3, figsize=(14, 8))
        fig.patch.set_facecolor('#111827')  # Premium dark background (tailwind-like gray-900)

        # General styling
        text_color = '#f3f4f6'  # gray-100
        grid_color = '#374151'  # gray-700
        colors = ['#38bdf8', '#fbbf24', '#34d399']  # cyan-400, amber-400, emerald-400
        
        # 1. Valence Input
        ax = axes[0, 0]
        ax.set_facecolor('#1f2937')  # gray-800
        for i, label in enumerate(['low', 'medium', 'high']):
            ax.plot(self.valence_in.universe, self.valence_in[label].mf, label=label, linewidth=2.5, color=colors[i])
        ax.set_title('Valence Input (Mood)', color=text_color, fontsize=12, pad=10, weight='bold')
        ax.set_xlabel('Sad → Happy (0-10)', color=text_color)
        ax.set_ylabel('Membership Degree', color=text_color)
        ax.tick_params(colors=text_color)
        ax.legend(facecolor='#111827', edgecolor='#374151', labelcolor=text_color)
        ax.grid(True, linestyle='--', color=grid_color, alpha=0.5)
        if val_val is not None:
            ax.axvline(x=val_val, color='#ef4444', linestyle='--', linewidth=2.5, label=f'Current: {val_val:.1f}')
            ax.legend(facecolor='#111827', edgecolor='#374151', labelcolor=text_color)

        # 2. Arousal Input
        ax = axes[0, 1]
        ax.set_facecolor('#1f2937')
        for i, label in enumerate(['low', 'medium', 'high']):
            ax.plot(self.arousal_in.universe, self.arousal_in[label].mf, label=label, linewidth=2.5, color=colors[i])
        ax.set_title('Arousal Input (Energy)', color=text_color, fontsize=12, pad=10, weight='bold')
        ax.set_xlabel('Calm → Excited (0-10)', color=text_color)
        ax.set_ylabel('Membership Degree', color=text_color)
        ax.tick_params(colors=text_color)
        ax.legend(facecolor='#111827', edgecolor='#374151', labelcolor=text_color)
        ax.grid(True, linestyle='--', color=grid_color, alpha=0.5)
        if aro_val is not None:
            ax.axvline(x=aro_val, color='#ef4444', linestyle='--', linewidth=2.5, label=f'Current: {aro_val:.1f}')
            ax.legend(facecolor='#111827', edgecolor='#374151', labelcolor=text_color)

        # Helper to plot outputs
        def plot_output(ax, var, title, label_x, target_val=None):
            ax.set_facecolor('#1f2937')
            for i, label in enumerate(['low', 'medium', 'high']):
                ax.plot(var.universe, var[label].mf, label=label, linewidth=2.5, color=colors[i])
            ax.set_title(title, color=text_color, fontsize=12, pad=10, weight='bold')
            ax.set_xlabel(label_x, color=text_color)
            ax.set_ylabel('Membership Degree', color=text_color)
            ax.tick_params(colors=text_color)
            ax.legend(facecolor='#111827', edgecolor='#374151', labelcolor=text_color)
            ax.grid(True, linestyle='--', color=grid_color, alpha=0.5)
            if target_val is not None:
                ax.axvline(x=target_val, color='#10b981', linestyle='--', linewidth=2.5, label=f'Target: {target_val:.2f}')
                ax.legend(facecolor='#111827', edgecolor='#374151', labelcolor=text_color)

        # 3. Target Valence (Row 1, Col 0 in output terms -> axes[1,0])
        plot_output(axes[1, 0], self.valence_out, 'Target Track Valence (Output)', 'Valence (0.0 - 1.0)', outputs['valence'] if outputs else None)

        # 4. Target Energy
        plot_output(axes[1, 1], self.energy_out, 'Target Track Energy (Output)', 'Energy (0.0 - 1.0)', outputs['energy'] if outputs else None)

        # 5. Target Danceability
        plot_output(axes[0, 2], self.dance_out, 'Target Track Danceability (Output)', 'Danceability (0.0 - 1.0)', outputs['danceability'] if outputs else None)
        
        # 6. Target Tempo
        plot_output(axes[1, 2], self.tempo_out, 'Target Track Tempo (Output)', 'Normalized Tempo (0.0 - 1.0)', outputs['tempo'] if outputs else None)

        plt.suptitle("Fuzzy Logic Inference System (FIS) State Visualization", color=text_color, fontsize=16, weight='bold', y=0.98)
        plt.tight_layout()
        
        # Save plot to base64 buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        return img_str
