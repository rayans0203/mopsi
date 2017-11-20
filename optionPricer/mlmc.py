# -*- coding: utf-8 -*-
"""
Created on Wed Nov 15 09:34:45 2017

@author: rayan
"""

import numpy as np
import scipy.stats as ss
from time import time
from matplotlib import pyplot as plt
import multiprocessing as mp

class MC_simulation():
    def __init__(self,S):
        self.S=S
    def __call__(self,pricer,W):
        self.S=pricer.S0*np.exp((pricer.rate-0.5*pricer.vol**2)*pricer.maturity+pricer.vol*np.sqrt(pricer.maturity)*W)
        return self.S

class M1LMC_simulation():
    def __init__(self,S):
        self.S=S
    def __call__(self,pricer,N_step,schema):
        W=np.random.normal(0,1,N_step)
        if schema=="euler":
            dt=pricer.maturity/N_step
            for j in range(N_step):
                self.S=self.S*(1+pricer.rate*dt+pricer.vol*np.sqrt(dt)*W[j])
        return self.S

class optionPricer():
    def __init__(self,S0,K,sigma,T,r=0.01,order="call"):
        self.order=order
        self.S0=S0
        self.strike=K
        self.rate=r
        self.vol=sigma
        self.maturity=T
    def BlackScholes(self):
        d1=(np.log(self.S0/self.strike)+(self.rate+(self.vol**2)/2)*self.maturity)/(self.vol*np.sqrt(self.maturity))
        d2=d1-self.vol*np.sqrt(self.maturity)
        if self.order=="call":
            return (self.S0*ss.norm.cdf(d1)-self.strike*np.exp(-self.rate*self.maturity)*ss.norm.cdf(d2))
        if self.order=="put":
           return self.strike*np.exp(-self.rate*self.maturity)*ss.norm.cdf(-d2(self.S0,self.strike,self.rate,self.vol,self.maturity))-self.S0*ss.norm.cdf(-d1(self.S0,self.strike,self.rate,self.vol,self.maturity))
    def mc(self,N,W=None):
        if W==None:
            W=np.random.normal(0,1,N)
        pool=mp.Pool(4)
        future_res=[pool.apply_async(MC_simulation(0),(self,W[_],)) for _ in range(N)]
        S=[f.get() for f in future_res]
        return S
    def m1lmc(self,N_samples,N_step,schema="euler"):
        s=self.S0
        pool=mp.Pool(4)
        future_res=[pool.apply_async(M1LMC_simulation(s),(self,N_step,schema)) for _ in range(N_samples)]
        S=[f.get() for f in future_res]
        return S
    def mlmc(self,L,N=10**4,m=2,schema="euler"):
        """ for now, we suppose L fixed, then we will implement a version
        in which we increment L until the mse is greater than a given accuracy"""
        S=np.zeros(L)
        # l=0
        Payoff=0
        if self.order=="call":
            for _ in range(N):
                Payoff+=max(self.S0*(1+self.rate*self.maturity+self.vol*np.sqrt(self.maturity)*np.random.normal(0,1))-self.strike,0)
        elif self.order=="put":
            for _ in range(N):
                Payoff+=max(self.strike-self.S0*(1+self.rate*self.maturity+self.vol*np.sqrt(self.maturity)*np.random.normal(0,1)),0)
        Payoff/=N
        # for l>1
        for l in range(1,L):
            
            #choix de Nl
            # déterminons la variance de Pl-Pl-1 puis choix de Nl
            Nl=N

            P_thin=np.zeros(Nl)
            P_coarse=np.zeros(Nl)

            if schema=="euler":
                for j in range(Nl):
                    # on génère les deux mouvements browniens
                    W_thin=np.random.normal(0,1,m**l)
                    W_coarse=np.array([np.sum(W_thin[k*m:(k+1)*m]) for k in range(m**(l-1))])
            
                    S_thin=self.S0
                    dt_thin=self.maturity/(m**l)
                    for i in range(1,m**l):
                        S_thin=S_thin*(1+self.rate*dt_thin+self.vol*np.sqrt(dt_thin)*W_thin[i])
                    S_coarse=self.S0
                    dt_coarse=self.maturity/(m**(l-1))
                    for i in range(m**(l-1)):
                        S_coarse=S_coarse*(1+self.rate*dt_coarse+self.vol*np.sqrt(dt_coarse)*W_coarse[i])

                    if self.order=="call":
                        P_thin[j]=max(S_thin-self.strike,0)
                        P_coarse[j]=max(S_coarse-self.strike,0)
            print(Payoff)
            print((P_thin-P_coarse).mean())
            Payoff+= (P_thin-P_coarse).mean()
        return Payoff
    def price(self,method="mc",N=10**4,N0=10**2):
        if method=="bs":
            return self.BlackScholes()
        elif method=="mc":    
            start=time()
            S=self.mc(N)
        elif method=="m1lmc":
            start=time()
            S=self.m1lmc(N,N0)

        if self.order=="call":
            payoff=list(map(lambda x:max(x-self.strike,0),S))
            end=time()
            return (np.mean(payoff),end-start)
        elif self.order=="put":
            payoff=list(map(lambda x:max(self.strike-x,0),S))
            end=time()
            return (np.mean(payoff),end-start)
        else:
            raise ValueError("'order' muste be either 'call' or 'put'")

o=optionPricer(100,100,0.25,1,r=0.05)
obs=o.price(method="bs")
(om1mc,t)=o.price(method="mc")

print("BS: {} $ vs 1-MLMC: {} $".format(obs,om1mc))
print("time: {}".format(t))

# class MSE_computation():
#     def __init__(self):
#         self.err=0
#         self.times=[]
#     def __call__(self,ref,pricer,simulations,method):
#         omc,t=pricer.price(method,N=simulations)
#         self.err+=(omc-ref)**2
#         self.times.append(t)
#         return self.err,self.times

# def mse(ref,pricer,simulations,method="mc",max_iter=100):
#     pool=mp.Pool(4)
#     future_res=[pool.apply_async(MSE_computation(),(ref,pricer,simulations,method)) for _ in range(max_iter)]
#     data=[f.get() for f in future_res]
#     err=np.sum([data[k][0] for k in range(len(data))])
#     times=[data[k][1] for k in range(len(data))]
#     return err/max_iter,np.mean(times)

# def mse(ref,pricer,simulations,method="mc",max_iter=100):
#     err=0
#     times=[]
#     for _ in range(max_iter):
#         omc,t=pricer.price(method,N=simulations)
#         err+=(omc-ref)**2
#         times.append(t)
#     return err/max_iter,np.mean(times)

# a=np.array([10**2,5*10**2,10**3])
# outputs=list(map(lambda x: mse(obs,o,x,method="mc"),a))
# MSE=[outputs[k][0] for k in range(len(outputs))]
# TIMES=[outputs[k][1] for k in range(len(outputs))]

# plt.subplot(211)
# plt.title('Classic Monte-Carlo simulations with \n Black-Scholes formula as reference')
# plt.loglog(np.log(a),MSE,marker='<')
# plt.grid(True)
# plt.xlabel("log of the number of samples for MC simulations")
# plt.ylabel("log of the MSE")

# plt.subplot(212)
# plt.loglog(np.log(a),TIMES,marker='o')
# plt.grid(True)
# plt.xlabel("log of the number of samples for MC simulations")
# plt.ylabel("log of the computation time")
# plt.tight_layout()
# plt.show()
