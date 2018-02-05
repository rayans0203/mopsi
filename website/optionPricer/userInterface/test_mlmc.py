from django.test import TestCase
from . import mlmc
import numpy as np

class MLMCTestCase(TestCase):
	def setUp(self):
    	# INPUTS
	    order="call"    # call, put
	    S0=100
	    strike=100
	    rate=np.log(1.1)
	    vol=0.2
	    maturity=3
	    N=1000  # nb d 'échantillons pour  MonteCarlo classique avec schema numérique
	    n=50    # nb de pas de disrétisation pour schéma numérique 
	    m=2     # détermine le nombre de niveau par L=log(n)/log(m)
	    model="BS"  # BS: Black-Scholes, Heston: Heston
	    sch="euler" # euler, milstein
	    option_type="A" # E: european, A: asian

	    self.o=mlmc.optionPricer(S0,strike,vol,maturity,model,option_type,sch,r=rate,kappa=3,rho=0,xi=0.2,theta=.9,v0=0.1)

	def test_price_positive_BS(self):
		for i in range(20):
			order=np.random.choice(["call","put"])
			S0=np.random.random()*100
			K=np.random.random()*100
			rate=np.random.random()*0.2
			vol=np.random.random()*.5
			maturity=np.random.random()*3
			N=1000
			n=50
			m=2
			schema=np.random.choice(["euler"])
			option_type=np.random.choice(["E","A"])
			method=np.random.choice(["mlmc","mc"])
			o=mlmc.optionPricer(S0,K,vol,maturity,"BS",option_type,schema,r=rate)

			args=(order,S0,K,rate,vol,maturity,schema,option_type,method)

			price=o.price(order,method,m,N,n)[0]

			# voir les arguments passés au cas où..
			print(args)
			print(price)
			self.assertTrue(price>=0)

	def test_price_positive_Heston(self):
		for i in range(20):
			order=np.random.choice(["call","put"])
			S0=np.random.random()*100
			K=np.random.random()*100
			rate=np.random.random()*0.2
			vol=np.random.random()*.5
			maturity=np.random.random()*3
			N=1000
			n=50
			m=2
			schema=np.random.choice(["euler"])
			option_type=np.random.choice(["E"])
			method=np.random.choice(["mlmc","mc"])
			o=mlmc.optionPricer(S0,K,vol,maturity,"Heston",option_type,schema,r=rate,kappa=3,rho=0,xi=0.2,theta=.9,v0=0.1)

			args=(order,S0,K,rate,vol,maturity,schema,option_type,method)

			price=o.price(order,method,m,N,n)[0]

			# voir les arguments passés au cas où..
			print(args)
			print(price)
			self.assertTrue(price>=0)