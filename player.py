# python 3
# this class combines all basic features of a generic player
import numpy as np
import pandas

class Player:

	def __init__(self):
		# some player might not have parameters
		self.parameters = 0
		self.horizon = 48
		self.nb_slow = 2
		self.nb_fast = 2

	def set_scenario(self, scenario_data):
		self.data = scenario_data
		# pb pour créer cette liste
		arr_dep = list(scenario_data.to_numpy())[:self.nb_slow+self.nb_fast]
		print(arr_dep)
		self.depart = {"slow": [d[1] for d in arr_dep[:self.nb_slow]], "fast": [d[1] for d in arr_dep[self.nb_slow:self.nb_fast+self.nb_slow]]}
		self.arrival = {"slow": [d[0] for d in arr_dep[:self.nb_slow]], "fast": [d[0] for d in arr_dep[self.nb_slow:self.nb_fast+self.nb_slow]]}

	def set_prices(self, prices):
		self.prices = prices

	def compute_all_load(self):
		load = np.zeros(self.horizon)
		load = self.take_decision(0) # on n'utilise pas l'argument time
		#for time in range(self.horizon):
		#	load[time] = self.compute_load(time)
		return load

	def take_decision(self, time):

		# Sorting time index by price (lowest to highest)
		sorted_time_by_price = np.zeros(self.horizon)
		s = np.copy(self.prices)
		for i in range(self.horizon):
			maxi = 0
			indice = 0
			for j in range(self.horizon):
				if s[j] >= maxi:
					maxi = self.prices[j]
					indice = j
			sorted_time_by_price[self.horizon-i-1] = indice
			s[indice] = -1


		############## V1G CASE (no reinjection)

		for k in range(self.nb_slow):
			charge_restante = 10
			i = 0
			while charge_restante > 0:
				if sorted_time_by_price[i] < self.depart[k] and load[sorted_time_by_price[i]] < 40:
					load[sorted_time_by_price[i]] += 0.95 * min(min(charge_restante, 3), 40-load[sorted_time_by_price[i]])
					charge_restante -= 0.95 * min(min(charge_restante, 3), 40-load[sorted_time_by_price[i]])
				i += 1

		for k in range(self.nb_fast):
			charge_restante = 10
			i = 0
			while charge_restante > 0:
				if sorted_time_by_price[i] < self.depart[self.nb_slow + k] and load[sorted_time_by_price[i]] < 40:
					load[sorted_time_by_price[i]] += 0.95 * min(min(charge_restante, 10), 40-load[sorted_time_by_price[i]])
					charge_restante -= 0.95 * min(min(charge_restante, 10), 40-load[sorted_time_by_price[i]])
				i += 1
		##################

		return load

	def compute_load(self, time):
		load = self.take_decision(time)
		# do stuff ?
		return load

	def reset(self):
		# reset all observed data
		pass

scenario_data = pandas.read_csv("ev_scenarios.csv")
prices = np.random.rand(48)


P = Player()
P.__init__()
P.set_scenario(scenario_data)

P.set_prices(prices)
load = P.compute_all_load()
