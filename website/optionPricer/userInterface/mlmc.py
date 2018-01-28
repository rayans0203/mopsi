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

from sklearn.linear_model import Ridge
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline

class MC_simulation():
    def __init__(self,S):
        self.S=S
    def __call__(self,pricer):
        self.S=pricer.S0*np.exp((pricer.rate-0.5*pricer.vol**2)*pricer.maturity+pricer.vol*np.sqrt(pricer.maturity)*np.random.normal(0,1))
        return self.S

class M1LMC_simulation():
    def __init__(self,S):
        self.S=S
    def __call__(self,pricer,n,schema):
        dt=pricer.maturity/n
        W=build_BM(n,np.sqrt(dt))
        self.S=self.S0
        for j in range(n):
            self.S=pricer.euler(self.S,dt,W[j+1]-W[j])
        return self.S

######### UTILS ##############

def build_BM(n,sqrt_dt):
    W=np.zeros(n+1)
    W_ind=np.random.normal(0,sqrt_dt,n)
    for k in range(n):
        W[k+1]=W[k]+W_ind[k]
    return W

def build_BM_corr(sqrt_dt,rho,W):
    "returns a brownian motion with correlation 'rho' to input: W"
    n=W.shape[0]-1
    W_rho=np.zeros(n+1)
    W_independant=build_BM(n,sqrt_dt)
    W_ind_acc=W_independant[1:]-W_independant[:n]
    for k in range(n):
        W_rho[k+1]=W_rho[k]+rho*(W[k+1]-W[k])+np.sqrt(1-rho**2)*W_ind_acc[k]
    return W_rho   

def build_Cox_Ross(W,rho,kappa,theta,xi,dt,pricer):
    W_rho=build_BM_corr(np.sqrt(dt),rho,W)
    n=W.shape[0]-1
    W_rho_acc=W_rho[1:]-W_rho[:n]
    v=np.ones(n)*pricer.v0
    for k in range(n-1):
        v[k+1]=abs(v[k]+kappa*(theta-v[k])*dt+xi*np.sqrt(v[k])*W_rho_acc[k])
    return v

######### OptionPricer class ##########

class optionPricer():
    def __init__(self,S0,K,sigma,T,model,option_type,order="call",r=np.log(1.1),**kwargs):
        self.order=order
        self.S0=S0
        self.strike=K
        self.rate=r
        self.vol=sigma
        self.maturity=T
        self.model=model
        self.option_type=option_type
        if model=="Heston":
            self.kappa=kwargs["kappa"]
            self.theta=kwargs["theta"]
            self.xi=kwargs["xi"]
            self.rho=kwargs["rho"]
            self.v0=kwargs["v0"]
    def BlackScholes(self):
        d1=(np.log(self.S0/self.strike)+(self.rate+0.5*self.vol**2)*self.maturity)/(self.vol*np.sqrt(self.maturity))
        d2=d1-self.vol*np.sqrt(self.maturity)
        if self.order=="call":
            return self.S0*ss.norm.cdf(d1)-self.strike*np.exp(-self.rate*self.maturity)*ss.norm.cdf(d2)
        if self.order=="put":
            return self.strike*np.exp(-self.rate*self.maturity)*ss.norm.cdf(-d2)-self.S0*ss.norm.cdf(-d1)
    def euler(self,S,dt,W,*v):
        """ pour l instant, on ne considère que des options européennes """
        if self.model=="BS":
            return S*(1+self.rate*dt+self.vol*W)
        elif self.model=="Heston":
            return S*(1+self.rate*dt+np.sqrt(v[0])*W)
    def payoff(self,S):
        """ S est un numpy.array """
        if self.order=="call":
            return max(S-self.strike,0)
        elif self.order=="put":
            return max(self.strike-S,0)
        else:
            raise TypeError("Unvalid 'order' attribute. Must be either 'call' or 'put'.")
    def mc_explicit(self,N,pool):
        # on garde les possibilités de paralléliser ou non pour les comparer
        if pool==None:
            S=np.zeros(N)
            W=np.random.normal(0,np.sqrt(self.maturity),N)
            for _ in range(N):
                S[_]=self.S0*np.exp((self.rate-0.5*self.vol**2)*self.maturity+self.vol*W[_])
        else:
            future_res=[pool.apply_async(MC_simulation(0),(self,)) for _ in range(N)]
            S=np.array([f.get() for f in future_res])
            return np.exp(-self.rate*self.maturity)*np.mean(list(map(lambda x: self.payoff(x),S)))
    def calcul_BS(self,t,W):
        return(self.S0*np.exp((self.rate-0.5*self.vol**2)*t+self.vol*np.sqrt(t)*W))
    def mc(self,n,N,pool=None):
        if pool==None:
            dt=self.maturity/n
            Payoff=0
            for j in range(N):
                S=self.S0
                W=build_BM(n,np.sqrt(dt))
                W_ind=np.random.normal(0,np.sqrt(dt),n)
                if self.model=="Heston":
                    v=build_Cox_Ross(W,self.rho,self.kappa,self.theta,self.xi,dt,self)
                    for k in range(n):
                        S=self.euler(S,dt,W_ind[k],v[k])
                else:
                    if self.option_type=="E":
                        for k in range(n):
                            S=self.euler(S,dt,W_ind[k])
                    elif self.option_type=="A":
                        S=0
                        for k in range(n):
                            S+=(dt/(2*self.maturity))*(self.calcul_BS(k*dt,W[k])+self.calcul_BS((k+1)*dt,W[k+1]))
                    else:
                        raise AttributeError("'option_type' attribute must be either 'E' (european) or 'A' (asian).")
                Payoff+=self.payoff(S)
            return np.exp(-self.rate*self.maturity)*Payoff/N

        else:
            future_res=[pool.apply_async(M1LMC_simulation(s),(self,n)) for _ in range(N)]
            S=np.array([f.get() for f in future_res])
            return np.exp(-self.rate*self.maturity)*np.mean(list(map(lambda x: self.payoff(x),S)))
    def mlmc(self,n,m):
        L=int(np.log(n)/np.log(m))
        # l=0
        if self.option_type=="E":
            N0=int((m-1)*self.maturity*(n**2)*L)
        elif self.option_type=="A":
            N0=int((m**2-1)*(n**2)*(1-1/np.sqrt(n))/(np.sqrt(m-1)))
        S_N0=self.S0
        W_N0=np.random.normal(0,np.sqrt(self.maturity),N0)
        Payoff=0
        if self.model=="Heston":
            for j in range(N0):
                S_N0=self.euler(self.S0,self.maturity,W_N0[j],self.v0)
                Payoff+=self.payoff(S_N0)
        else:
            if self.option_type=="E":
                for j in range(N0):
                    S_N0=self.euler(self.S0,self.maturity,W_N0[j])
                    Payoff+=self.payoff(S_N0)
            elif self.option_type=="A":
                for j in range(N0):
                    S_N0=0
                    S_N0+=(1/2)*(self.S0+self.calcul_BS(self.maturity,W_N0[j]))
                    Payoff+=self.payoff(S_N0)     
        Payoff/=N0

        # for l>1
        # inverser le role de n et L, c est n qui donne L
        for l in range(1,L):
            #choix de Nl
            # déterminons la variance de Pl-Pl-1 puis choix de Nl
            Nl=0
            if self.option_type=="E":
                Nl=int(N0/(m**l))
            elif self.option_type=="A":
                Nl=int(N0/(m**(3*l/2)))
            else:
                raise AttributeError("'option_type' attribute must be either 'E' (european) or 'A' (asian).")

            for j in range(Nl):
                payoff_j=0
                
                S_thin=self.S0
                S_coarse=self.S0
                # on génère les deux mouvements browniens
                dt_thin=self.maturity/(m**l)
                W_thin=build_BM(m**l,np.sqrt(dt_thin))
                W_coarse=np.zeros(m**(l-1)+1)

                for i in range(m**(l-1)):
                    W_coarse[i+1]=W_thin[(i+1)*m]
                dt_coarse=self.maturity/(m**(l-1))
                if self.model=="Heston":
                    v_thin=build_Cox_Ross(W_thin,self.rho,self.kappa,self.theta,self.xi,dt_thin,self)
                    v_coarse=build_Cox_Ross(W_coarse,self.rho,self.kappa,self.theta,self.xi,dt_coarse,self)
                    for i in range(m**l):
                        S_thin=self.euler(S_thin,dt_thin,np.random.normal(0,np.sqrt(dt_thin)),v_thin[i])
                        if i%m==0:
                            S_coarse=self.euler(S_coarse,dt_coarse,np.random.normal(0,np.sqrt(dt_coarse)),v_coarse[i//m])
                    payoff_j+=self.payoff(S_thin)-self.payoff(S_coarse)
                elif self.model=="BS":
                    if self.option_type=="E":
                        for i in range(m**l):
                            S_thin=self.euler(S_thin,dt_thin,np.random.normal(0,np.sqrt(dt_thin)))
                            if i%m==0:
                                S_coarse=self.euler(S_coarse,dt_coarse,np.random.normal(0,np.sqrt(dt_coarse)))
                    elif self.option_type=="A":
                        S_thin=0
                        S_coarse=0
                        for i in range(m**l):
                            S_thin+=(dt_thin/(2*self.maturity))*(self.calcul_BS(i*dt_thin,W_thin[i])+self.calcul_BS((i+1)*dt_thin,W_thin[i+1]))
                            if i%m==0:
                                S_coarse+=(dt_coarse/(2*self.maturity))*(self.calcul_BS((i//m)*dt_coarse,W_coarse[i//m])+self.calcul_BS((i//m+1)*dt_coarse,W_coarse[(i+1)//m]))
                    else:
                        raise AttributeError("'option_type' attribute must be either 'E' (european) or 'A' (asian).")
                                
                    payoff_j+=self.payoff(S_thin)-self.payoff(S_coarse)
                Payoff+=payoff_j/Nl
        return np.exp(-self.rate*self.maturity)*Payoff
    def price(self,order,method="mc_e",pool=None,m=5,N=10**3,n=50,alpha=0.05):
        self.order=order
        if method=="bs":
            start=time()
            payoff=self.BlackScholes()
            return payoff,time()-start
        elif method=="mc_e":
            start=time()
            payoff=self.mc_explicit(N,pool)
            return payoff,time()-start
        elif method=="mc":
            start=time()
            payoff=self.mc(n,N,pool)
            return payoff,time()-start
        elif method=="mlmc":
            start=time()
            payoff=self.mlmc(n,m)
            return payoff,time()-start

    def confidence_interval(self,alpha,payoffs):
        n=payoffs.shape[0]
        V=payoffs.std()**2
        mu=payoffs.mean()
        if self.order=="call":
            return [mu-ss.norm.cdf(1-alpha/2)*np.sqrt(V/n),
                    mu+ss.norm.cdf(1-alpha/2)*np.sqrt(V/n)]
        elif self.order=="put":
            return [mu-ss.norm.cdf(1-alpha/2)*np.sqrt(V/n),
                    mu+ss.norm.cdf(1-alpha/2)*np.sqrt(V/n)]

if __name__=="__main__":
    o=optionPricer(100,100,0.2,3,"BS","A",kappa=3,rho=0,xi=0.2,theta=.9,v0=0.1)
    #print("reference price: {}".format(o.price("call",'bs')))
    print("MC euler price: {}".format(o.price("call","mc")))
    print('MLMC price with Heston model: {}'.format(o.price("call","mlmc")))

