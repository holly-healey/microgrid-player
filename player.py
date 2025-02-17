# python 3
# this class combines all basic features of a generic player
import numpy as np
import pandas


class Battery:

	def __init__(self):
		self.max_charge_slow = 3
		self.max_charge_fast = 22
		self.max_battery = 40
		self.horizon = 48
		self.nb_slow = 2
		self.nb_fast = 2
		self.charge = np.zeros((self.nb_slow + self.nb_fast, self.horizon))


class Player:

	def __init__(self):
		# some player might not have parameters
		self.parameters = 0
		self.horizon = 48
		self.nb_slow = 2
		self.nb_fast = 2
		self.max_charge_slow = 3
		self.max_charge_fast = 22
		self.max_battery = 40

	def set_scenario(self, scenario_data):
		self.data = scenario_data
		# pb pour créer cette liste
		ev_id = np.array(scenario_data["ev_id"])[:self.nb_slow+self.nb_fast]
		dep = np.array(scenario_data["time_slot_dep"])[:self.nb_slow+self.nb_fast]
		arr = np.array(scenario_data["time_slot_arr"])[:self.nb_slow+self.nb_fast]
		self.depart = {"slow": [d for d in dep[:self.nb_slow]], "fast": [d for d in dep[self.nb_slow:self.nb_fast+self.nb_slow]]}
		self.arrival = {"slow": [d for d in arr[:self.nb_slow]], "fast": [d for d in arr[self.nb_slow:self.nb_fast+self.nb_slow]]}

	def set_prices(self, prices):
		self.prices = prices

	def compute_all_load(self):
		load = np.zeros(self.horizon)
		load = self.take_decision(0) # on n'utilise pas l'argument time
		#for time in range(self.horizon):
		#	load[time] = self.compute_load(time)
		return load

	def take_decision(self, time):
		B = Battery()
		B.__init__()

		load = np.zeros(self.horizon)
		# Sorting time index by price (lowest to highest)
		sorted_time_by_price = np.zeros(self.horizon, dtype=int)
		s = np.copy(self.prices)
		for i in range(self.horizon):
			maxi = 0
			indice = 0
			for j in range(self.horizon):
				if s[j] >= maxi:
					maxi = self.prices[j]
					indice = j
			sorted_time_by_price[self.horizon-i-1] = int(indice)
			s[indice] = -1

		print(sorted_time_by_price)


		############## V1G CASE (no reinjection)
		for k in range(self.nb_slow):
			charge_restante = 10
			i = 0
			while charge_restante > 0 and i < 48 :
				if sorted_time_by_price[i] < self.depart["slow"][k] and load[sorted_time_by_price[i]] < 40:
					load[sorted_time_by_price[i]] += 0.95 * min(min(charge_restante, 3), 40-load[sorted_time_by_price[i]])
					charge_restante -= 0.95 * min(min(charge_restante, 3), 40-load[sorted_time_by_price[i]])
					B.charge[k, sorted_time_by_price[i]] += 0.95 * min(min(charge_restante, 3), 40-load[sorted_time_by_price[i]])
				i += 1

		for k in range(self.nb_fast):
			charge_restante = 10
			i = 0
			while charge_restante > 0 and i < 48 :
				if sorted_time_by_price[i] < self.depart["fast"][k] and load[sorted_time_by_price[i]] < 40:
					load[sorted_time_by_price[i]] += 0.95 * min(min(charge_restante, 10), 40-load[sorted_time_by_price[i]])
					charge_restante -= 0.95 * min(min(charge_restante, 10), 40-load[sorted_time_by_price[i]])
					B.charge[self.nb_slow + k, sorted_time_by_price[i]] += 0.95 * min(min(charge_restante, 3), 40-load[sorted_time_by_price[i]])
				i += 1
		##################
		'''
		############## V2G CASE (reinjection)
		charge_state = np.zeros((self.nb_slow + self.nb_fast, self.horizon+1))
		# derniere colonne : somme des charges utiles pour le véhicule
		a = np.zeros((self.nb_fast, self.horizon))
		# a suit l'évolution du stock de batterie des véhicules rapides
		i = 0
		while i <self.horizon:
			for r in range(self.nb_fast):
				for l in range(self.nb_slow):
					#charge véhicules lents
					if charge_state[l][-1] < 10 and charge_state[l][i] < 3 and sorted_time_by_price[i] < self.depart["slow"][l] and load[sorted_time_by_price[i]] < 40:
						load[sorted_time_by_price[i]] += 0.95 * min(min(10-charge_state[l][-1], 3 - charge_state[l][i]), 40 - load[sorted_time_by_price[i]])
						charge_state[l][-1] += load[sorted_time_by_price[i]]
						charge_state[l][i] += load[sorted_time_by_price[i]]

					#charge véhicules rapides
					if charge_state[self.nb_slow+r][i] < self.max_charge_fast and charge_state[self.nb_slow + r][-1] < 10 and a[r][i] < self.max_battery and sorted_time_by_price[i] < self.depart["fast"][r] and load[sorted_time_by_price[i]]<40:
						load[sorted_time_by_price[i]] += 0.95 * min(
							min(10 - charge_state[self.nb_slow+r][-1], 10 - charge_state[self.nb_slow+r, -1]), 40 - load[sorted_time_by_price[i]])
						charge_state[self.nb_slow+r][-1] += load[sorted_time_by_price[i]]
						charge_state[self.nb_slow + r][i] += load[sorted_time_by_price[i]]
						a[r,i] += load[sorted_time_by_price[i]]

					# charge véhicules rapides pour les lents
					if i < self.horizon:
						for t in range(i+1,self.depart["fast"][r]):
							if self.depart["slow"][l]-1 <= self.depart["fast"][r] and a[r][i] < self.max_battery and charge_state[l][-1] < 10 and sorted_time_by_price[i] < self.depart["slow"][l] and sorted_time_by_price[i] < self.depart["fast"][r] and load[sorted_time_by_price[i]]<40 and a[r][i]<40 :
								load[sorted_time_by_price[i]] += 0.95 * min(min(10-charge_state[l][-1], 22-charge_state[self.nb_slow+r][-1]), min(40 - load[sorted_time_by_price[i]], 40 - a[r][i]))
								charge_state[self.nb_slow+r][i] += load[sorted_time_by_price[i]]
								a[r][i] += load[sorted_time_by_price[i]]
								charge_state[l][-1] += 0.95 * load[sorted_time_by_price[i]]
								a[r][t] -= load[sorted_time_by_price[i]]
			i += 1

		'''
		return load

	def compute_load(self, time):
		load = self.take_decision(time)
		# do stuff ?
		return load

	def reset(self):
		# reset all observed data
		pass



if __name__ == '__main__':
	scenario_data = pandas.read_csv("ev_scenarios.csv", sep=";", decimal=".")
	prices = np.random.rand(48)

	P = Player()
	P.set_scenario(scenario_data)
	P.set_prices(prices)
	load = P.compute_load(0)

	print(load)