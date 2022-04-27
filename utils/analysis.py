import csv
import os
import glob
from structs import  config
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline

class Analyse:

    def __init__(self, dir_path):
        self.current_dir = os.getcwd()
        self.location = dir_path


    def read_data_to_array(self, market_type, param):
        if market_type == 'random':
            regret_player_base = 'regret_p_market_size_'
            regret_arm_base = 'regret_a_market_size_'
            stability_base = 'stability_market_size_'
        else:
            regret_player_base = 'regret_p_beta_'
            regret_arm_base = 'regret_a_beta_'
            stability_base = 'stability_beta_'

        # Load all the runs into a dictg
        p_reg = {}
        a_reg = {}
        a_stab = {}

        for run_number in range(config.number_of_runs):
            print(f"N={param}, run number = {run_number}")
            file_p_regret = glob.glob(regret_player_base + str(param) + '_run_' + str(run_number) + '.csv')[0]
            file_a_regret = glob.glob(regret_arm_base + str(param) + '_run_' + str(run_number) + '.csv')[0]
            file_stability = glob.glob(stability_base + str(param) + '_run_' + str(run_number) + '.csv')[0]

            with open(file_p_regret) as file:
                reg_p = np.loadtxt(file, delimiter=',')

            with open(file_a_regret) as file:
                reg_a = np.loadtxt(file, delimiter=',')

            with open(file_stability) as file:
                stab = np.loadtxt(file, delimiter=',')

            p_reg[run_number] = reg_p
            a_reg[run_number] = reg_a
            a_stab[run_number] = stab

        return p_reg, a_reg, a_stab

    def change_array_to_logs(self, market_type, param, player_regrets, arm_regrets, stabilities):

        # Arrays to store average regret and stability for plotting purposes
        average_player_regret_to_return = []
        average_arm_regret_to_return = []
        average_stability_to_return = []


        if market_type == 'random':
            regret_file_player = open(config.random_loc + "N=" + str(param) + "_player_regret.csv", "w",  newline="")  # Open regret csv
            regret_file_arm = open(config.random_loc + "N=" + str(param) + "_arm_regret.csv", "w", newline="")
            stability_file = open(config.random_loc + "N=" + str(param) + "_stability.csv", "w", newline="")  # Open stability csv
        else:
            regret_file_player = open(config.het_loc + "b=" + str(param) + "_player_regret.csv", "w", newline="")  # Open regret csv
            regret_file_arm = open(config.het_loc + "b=" + str(param) + "_arm_regret.csv", "w", newline="")
            stability_file = open(config.het_loc + "b=" + str(param) + "_stability.csv", "w", newline="")  # Open stability csv


        # Need to log all of this into a master CSV
        writer_r_player = csv.writer(regret_file_player)  # Create CSV writer for player regret
        writer_r_arm = csv.writer(regret_file_arm)
        writer_s = csv.writer(stability_file)  # Create CSV writer for player stability

        # Create Headers for regret and stability master CSV
        r_head_player = ['Time Step']
        r_head_arm = ['Time Step']
        s_head = ['Time Step']
        for temp in range(config.number_of_runs):
            r_head_player.append("Run " + str(temp))
            r_head_arm.append("Run " + str(temp))
            s_head.append("Run " + str(temp))
        r_head_player.append("Average Regret")
        r_head_arm.append("Average Regret")
        s_head.append("Average Stability")

        writer_r_player.writerow(r_head_player)  # Write header of regret file
        writer_r_arm.writerow(r_head_arm)
        writer_s.writerow(s_head)  # Write header of stability file


        for t in range(config.horizon):
            l_r_p = 0.0
            l_r_a = 0.0
            l_s = 0.0

            row_r_p = [t]
            row_r_a = [t]
            row_s = [t]

            for run_number in range(config.number_of_runs):
                row_r_p.append(player_regrets[run_number][t])
                row_r_a.append(arm_regrets[run_number][t])
                row_s.append(stabilities[run_number][t])
                l_r_p += player_regrets[run_number][t]
                l_r_a += arm_regrets[run_number][t]
                l_s += stabilities[run_number][t]

            avg_regret_player = l_r_p / config.number_of_runs
            avg_regret_arm = l_r_a / config.number_of_runs
            avg_stab = (l_s / config.number_of_runs) * 100
            row_r_p.append(avg_regret_player)
            row_r_a.append(avg_regret_arm)
            row_s.append(avg_stab)
            average_player_regret_to_return.append(avg_regret_player)
            average_arm_regret_to_return.append(avg_regret_arm)
            average_stability_to_return.append(avg_stab)

            writer_r_player.writerow(row_r_p)
            writer_r_arm.writerow(row_r_a)
            writer_s.writerow(row_s)

            row_r_p = []
            row_r_a = []
            row_s = []
        regret_file_player.close()
        regret_file_arm.close()
        stability_file.close()
        return average_player_regret_to_return, average_arm_regret_to_return, average_stability_to_return

    # Delete all temporary files
    def delete_files(self):
        allfiles = glob.glob("*.csv")
        for file in allfiles:
            os.remove(file)

    def make_graph(self, market_type):
        # Change the location to the place of temp files
        os.chdir(self.location)

        # Prepare the X-Axis
        x_axis = np.zeros(config.horizon)
        for i in range(config.horizon): x_axis[i] = i
        x_new = np.linspace(x_axis.min(), x_axis.max(), 300)

        m_regrets_p = {}
        m_regrets_a = {}
        m_stability = {}

        if market_type == 'random':
            iterate_over = config.market_sizes
            l = "N="
        else:
            iterate_over = config.beta_vals
            l = "b="

        for param in iterate_over:
            print("Reading in available data...")
            player_regret, arm_regret, stability = self.read_data_to_array(market_type, param)
            rl_p, rl_a, sl = self.change_array_to_logs(market_type, param, player_regret, arm_regret, stability)
            m_regrets_p[param] = rl_p
            m_regrets_a[param] = rl_a
            m_stability[param] = sl
            print("Dpne.")


        # MAKE REGRET PLOT
        legend = []
        for r in m_regrets_p.keys():
            gfg = make_interp_spline(x_axis, m_regrets_p[r], k=3)
            y_new = gfg(x_new)
            plt.plot(x_new, y_new, linewidth=0.7)
            #plt.plot(x_axis, m_regrets_p[r], linewidth=0.7)
            legend.append(l + str(r))
        plt.legend(legend)

        if market_type == 'random':
            title = 'Maximum Average Player Regret (Random Prefs)'
            txt = f'Regret Calculated over {config.number_of_runs} runs'
            filename = 'regret_random_pref_player.png'
        else:
            title = 'Maximum Average Player Regret (Coorelated Prefs)'
            txt = f'Regret Calculated over {config.number_of_runs} runs. Higher beta implies more correlation'
            filename = 'regret_beta_player.png'

        plt.title(title)
        plt.figtext(0.5, 0.001, txt, wrap=True, horizontalalignment='center', fontsize=10)
        plt.savefig(config.loc + filename)  # First save then show
        plt.show()
        plt.close()


        # MAKE STABILITY PLOT
        legend = []
        for s in m_stability.keys():
            gfg = make_interp_spline(x_axis, m_stability[s], k=3)
            y_new = gfg(x_new)
            plt.plot(x_new, y_new, linewidth=0.7)
            #plt.plot(x_axis, m_stability[r], linewidth=0.7)
            legend.append(l + str(s))
        plt.legend(legend)

        if market_type == 'random':
            title = 'Average Stability (Random Prefs)'
            txt = f'Stability Calculated over {config.number_of_runs} runs'
            filename = 'stability_random_pref_arm.png'
        else:
            title = 'Average Stability (Coorelated Prefs)'
            txt = f'Stability Calculated over {config.number_of_runs} runs. Higher beta implies more correlation'
            filename = 'stability_beta_arm.png'

        plt.title(title)
        plt.figtext(0.5, 0.01, txt, wrap=True, horizontalalignment='center', fontsize=10)
        plt.savefig(config.loc + filename)  # First save then show
        plt.show()
        plt.close()


        # MAKE ARM REGRET PLOT IF NEEDED
        # Plot arm regrets if we want them
        if config.analyse_arm_regrets:
            legend = []
            for r in m_regrets_a.keys():
                gfg = make_interp_spline(x_axis, m_regrets_a[r], k=3)
                y_new = gfg(x_new)
                plt.plot(x_new, y_new, linewidth=0.7)
                #plt.plot(x_axis, m_regrets_a[r], linewidth=0.7)
                legend.append(l + str(r))
            plt.legend(legend)

            if market_type == 'random':
                title = 'Maximum Average Arm Regret (Random Prefs)'
                txt = f'Regret Calculated over {config.number_of_runs} runs'
                filename = 'regret_random_pref_arm.png'
            else:
                title = 'Maximum Average Arm Regret (Coorelated Prefs)'
                txt = f'Regret Calculated over {config.number_of_runs} runs. Higher beta implies more correlation'
                filename = 'regret_beta_arm.png'

            plt.title(title)
            plt.figtext(0.5, 0.001, txt, wrap=True, horizontalalignment='center', fontsize=10)
            plt.savefig(config.loc + filename)  # First save then show
            plt.show()
            plt.close()
        os.chdir(self.current_dir)

    def analyse(self):
        print("Making Graphs")
        if config.run_random:
            self.make_graph('random')
        if config.run_varied:
            self.make_graph('varied')

        if config.delete_temp_files:
            os.chdir(self.location)
            self.delete_files()

        # Change location back to the working directory
        os.chdir(self.current_dir)
