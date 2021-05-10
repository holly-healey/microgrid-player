# python 3
# this class combines all basic features of a generic player
import numpy as np
import pandas

scenario_data = pandas.read_csv(ev_scenarios.csv)

class Player:

	def __init__(self):
		# some player might not have parameters
		self.parameters = 0
		self.horizon = 48
		self.nb_slow = 2
		self.nb_fast = 2

	def set_scenario(self, scenario_data):
		self.data = scenario_data
		arr_dep = list(scenario_data.values())[:self.nb_slow+self.nb_fast]
		self.depart = {"slow": [d[1] for d in arr_dep[:self.nb_slow]], "fast": [d[1] for d in arr_dep[self.nb_slow:self.nb_fast+self.nb_slow]]}
		self.arrival = {"slow": [d[0] for d in arr_dep[:self.nb_slow]], "fast": [d[0] for d in arr_dep[self.nb_slow:self.nb_fast+self.nb_slow]]}

	def set_prices(self, prices):
		self.prices = prices

	def compute_all_load(self):
		load = np.zeros(self.horizon)
		for time in range(self.horizon):
			load[time] = self.compute_load(time)
		return load

	def take_decision(self, time):

		# Sorting time by price (lowest to highest)
		sorted_time_by_price = np.zeros(self.horizon)
		s=np.copy(self.prices)
		for i in range(self.horizon):
			max=0
			indice=0
			for j in range(self.horizon):
				if s[j]>=max:
					max=self.prices[j]
					indice=j
			sorted_time_by_price[self_horizon-i-1]=indice
			s[indice]=-1



		for k in range(self.nb_slow):
			charge_restante=10
			i=0
			while(charge_restante>0):
				if sorted_time_by_price[i]<self.depart[k] and load[sorted_time_by_price[i]]<40:
					load[sorted_time_by_price[i]] = min(min(charge_restante,3),40-load[sorted_time_by_price[i]])
					charge_restante = charge_restante-min(min(charge_restante,3),40-load[sorted_time_by_price[i]])
				i+=1

		for k in range(self.nb_fast):
			charge_restante=10
			i=0
			while(charge_restante>0):
				if sorted_time_by_price[i]<self.depart[self.nb_slow + k] and load[sorted_time_by_price[i]]<40:
					load[sorted_time_by_price[i]] = min(min(charge_restante,10),40-load[sorted_time_by_price[i]])
					charge_restante = charge_restante-min(min(charge_restante,10),40-load[sorted_time_by_price[i]])
				i+=1

		return 0

	def compute_load(self, time):
		load = self.take_decision(time)
		# do stuff ?
		return load

	def reset(self):
		# reset all observed data
		pass