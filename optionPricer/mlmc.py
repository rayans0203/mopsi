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

# from sklearn.linear_model import Ridge
# from sklearn.preprocessing import PolynomialFeatures
# from sklearn.pipeline import make_pipeline

class MC_simulation():
    def __init__(self,S):
        self.S=S
    def __call__(self,pricer):
        self.S=pricer.S0*np.exp((pricer.rate-0.5*pricer.vol**2)*pricer.maturity+pricer.vol*np.sqrt(pricer.maturity)*np.random.normal(0,1))
        return self.S

class M1LMC_simulation():
    def __init__(self,S):
        self.S=S
    def __call__(self,pricer,N_step,schema):
        dt=pricer.maturity/N_step
        W=build_BM(N_step,np.sqrt(dt))
        if schema=="euler":
            for j in range(N_step):
                self.S=pricer.euler(self.S,dt,W[j])
        elif schema=="milstein":
            for j in range(N_step):
                self.S=pricer.milstein(self.S,dt,W[j])
        return self.S

def build_BM(n,sig):
    W=np.zeros(n)
    W[0]=np.random.normal(0,sig**2)
    for k in range(1,n):
        W[k]=W[k-1]+np.random.normal(0,sig**2)
    return W

class optionPricer():
    def __init__(self,S0,K,sigma,T,r=0.05,order="call"):
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
    def euler(self,S,dt,W):
        return S*(1+self.rate*dt+self.vol*W)
    def milstein(self,S,dt,W):
        return S*(1+self.rate*dt+self.vol*W+0.5*(self.vol**2)*(W**2-dt))
    def mc(self,N,pool):
        # on garde les possibilités de paralléliser ou non pour les comparer
        if pool==None:
            S=[]
            W=np.random.normal(0,1,N)
            for _ in range(N):
                S.append(self.S0*np.exp((self.rate-0.5*self.vol**2)*self.maturity+self.vol*np.sqrt(self.maturity)*W[_]))
        else:
            future_res=[pool.apply_async(MC_simulation(0),(self,)) for _ in range(N)]
            S=[f.get() for f in future_res]
        return S
    def m1lmc(self,N_samples,N_step,pool,schema="euler"):
        s=self.S0
        if pool==None:
            S=np.ones(N_samples)*s
            dt=self.maturity/N_step
            for j in range(N_samples):
                W=build_BM(N_step,np.sqrt(dt))
                if schema=="euler":
                    for _ in range(N_step):
                        S[j]=self.euler(S[j],dt,W[_])
                elif schema=="milstein":
                    for _ in range(N_step):
                        S[j]=self.milstein(S[j],dt,W[_])
        else:
            future_res=[pool.apply_async(M1LMC_simulation(s),(self,N_step,schema)) for _ in range(N_samples)]
            S=[f.get() for f in future_res]
        return S
    def mlmc(self,n,m=7,schema="euler"):
        L=int(np.log(n)/np.log(m))
        S=np.zeros(L)
        # l=0
        Payoff=0
        N0=int((m-1)*self.maturity*(n**2)*np.log(n)/np.log(m))
        if self.order=="call":
            for _ in range(N0):
                Payoff+=max(self.S0*(1+self.rate*self.maturity+self.vol*np.random.normal(0,self.maturity))-self.strike,0)
        elif self.order=="put":
            for _ in range(N0):
                Payoff+=max(self.strike-self.S0*(1+self.rate*self.maturity+self.vol*np.random.normal(0,self.maturity)),0)
        Payoff/=N0
        # for l>1
        # inverser le role de n et L, c est n qui donne L
        for l in range(1,L):
            
            #choix de Nl
            # déterminons la variance de Pl-Pl-1 puis choix de Nl
            Nl=int(N0/(m**l))

            P_thin=np.zeros(Nl)
            P_coarse=np.zeros(Nl)

            for j in range(Nl):
                # on génère les deux mouvements browniens
                dt_thin=self.maturity/(m**l)
                W_thin=build_BM(m**l,np.sqrt(dt_thin))
                S_thin=self.S0
                S_coarse=self.S0
                dt_coarse=self.maturity/(m**(l-1))
                if schema=="euler":
                    for i in range(1,m**l):
                        S_thin=self.euler(S_thin,dt_thin,W_thin[i]-W_thin[i-1])
                    for i in range(m**(l-1)):
                        S_coarse=self.euler(S_coarse,dt_coarse,W_thin[(i+1)*m-1]-W_thin[i*m])
                elif schema=="milstein":
                    for i in range(1,m**l):
                        S_thin=self.milstein(S_thin,dt_thin,W_thin[i]-W_thin[i-1])
                    for i in range(m**(l-1)):
                        S_coarse=self.milstein(S_coarse,dt_coarse,W_thin[(i+1)*m-1]-W_thin[i*m])
                if self.order=="call":
                    P_thin[j]=max(S_thin-self.strike,0)
                    P_coarse[j]=max(S_coarse-self.strike,0)
                elif self.order=="put":
                    P_thin[j]=max(self.strike-S_thin,0)
                    P_coarse[j]=max(self.strike-S_coarse,0)

            Payoff+= (P_thin-P_coarse).mean()
        return np.exp(-self.rate*self.maturity)*Payoff
    def price(self,method="mc",pool=None,m=7,N=10**4,n=10**2,alpha=5,schema="euler"):
        CI=[]
        if method!='mlmc':
            if method=="bs":
                return self.BlackScholes()
            elif method=="mc":    
                start=time()
                S=self.mc(N,pool)
            elif method=="m1lmc":
                start=time()
                S=self.m1lmc(N,n,pool)

            if self.order=="call":
                payoffs=list(map(lambda x:np.exp(-self.rate*self.maturity)*max(x-self.strike,0),S))
                payoff=np.mean(payoffs)
                CI=self.confidence_interval(alpha,payoffs)
            elif self.order=="put":
                payoffs=list(map(lambda x:np.exp(-self.rate*self.maturity)*max(x-self.strike,0),S))
                payoff=np.mean(payoffs)
                CI=self.confidence_interval(alpha,payoffs)
            else:
                raise ValueError("'order' muste be either 'call' or 'put'")      

            end=time()
            return (payoff,end-start,CI)

        elif method=="mlmc":
            start=time()
            payoff=self.mlmc(n,m,schema)
            end=time()
            return (payoff,end-start,CI)

    def confidence_interval(self,alpha,payoff):
        n=len(payoff)
        V=np.std(payoff)**2
        mu=np.mean(payoff)
        if self.order=="call":
            print(mu,ss.norm.cdf(1-alpha/2)*np.sqrt(V/n))
            return [mu-ss.norm.cdf(1-alpha/2)*np.sqrt(V/n),
                    mu+ss.norm.cdf(1-alpha/2)*np.sqrt(V/n)]
        elif self.order=="put":
            return [mu-ss.norm.cdf(1-alpha/2)*np.sqrt(V/n),
                    mu+ss.norm.cdf(1-alpha/2)*np.sqrt(V/n)]


o=optionPricer(100,100,0.25,1,r=0.05)
print(o.price())

# # Déterminer la relation entre n de MLMC et N de MC pour même temps de calcul
# # les "n" pour MLMC
# X=np.array(range(10,50))
# times=[]
# for x in X:
#     payoff,t=o.price(n=x,method="mlmc")
#     times.append(t)
# # stocke les "N(n)" tels que MC(N(n)) prenne le même temps que MLMC(n)
# print("checkpoint 1")
# y=[]
# N_interval=list(range(300,2*10**4))
# for t in times:
#     time_N=10**7
#     N_t=0
#     count=0
#     for N in N_interval:
#         payoff,tt=o.price(N=N,method="mc")
#         if (tt-t)**2<(time_N-t)**2:
#             time_N=tt
#             N_t=N
#             count=0
#         else:
#             count+=1
#         if count>10000:
#             break
#     y.append(N_t)
# print('checkpoint 2')
# for degree in [4,5]:
#     print(degree)
#     model=make_pipeline(PolynomialFeatures(degree),Ridge())
#     model.fit(X.reshape(-1,1),y)

# y_predict=model.predict(X)
# from tempfile import TemporaryFile
# outfile=TemporaryFile()

# np.save(outfile,model)
# plt.plot(X,y,marker='o',label='actual best fit')
# plt.plot(X,y_predict,marker='>',color='r',label='model prediction')
# plt.xlabel("Number n of samples used for Euler schematization")
# plt.ylabel('N(n) of MC simulations')
# plt.show()

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

def mse(ref,pricer,simulations,pool,method="mc",max_iter=5):
    err=0
    times=[]
    for _ in range(max_iter):
        print('{}% '.format(100*_/max_iter))
        omc,t=pricer.price(method,pool,N=simulations)
        err+=(omc-ref)**2
        times.append(t)
    return err/max_iter,np.mean(times)

obs=o.price(method="bs")
a=np.array([10,10**2,2*10**2,5*10**2,10**3,2*10**3,5*10**3,10**4])
# pool=mp.Pool(4)
# outputs_m1lmc=list(map(lambda x: mse(obs,o,x,pool,method="m1lmc"),a))
# MSE_m1lmc=[outputs_m1lmc[k][0] for k in range(len(outputs_m1lmc))]
# TIMES_m1lmc=[outputs_m1lmc[k][1] for k in range(len(outputs_m1lmc))]

# to show the benefits of parallelization
# outputs_m1lmc_unthreaded=list(map(lambda x: mse(obs,o,x,None,method="m1lmc"),a))
# MSE_m1lmc_unthreaded=[outputs_m1lmc_unthreaded[k][0] for k in range(len(outputs_m1lmc_unthreaded))]
# TIMES_m1lmc_unthreaded=[outputs_m1lmc_unthreaded[k][1] for k in range(len(outputs_m1lmc_unthreaded))]

# outputs_mlmc=list(map(lambda x: mse(obs,o,x,pool,method="mlmc"),a))
# MSE_mlmc=[outputs_mlmc[k][0] for k in range(len(outputs_mlmc))]
# TIMES_mlmc=[outputs_mlmc[k][1] for k in range(len(outputs_mlmc))]

# plt.loglog(np.log(a),MSE_mc,marker='<')
# plt.loglog(np.log(a),MSE_mlmc)
# plt.grid(True)
# plt.xlabel("log of the number of samples for MC simulations")
# plt.ylabel("log of the MSE")

# from tempfile import TemporaryFile
# outfile=TemporaryFile()

# np.save(outfile,(TIMES_m1lmc,TIMES_m1lmc_unthreaded))

# plt.plot(np.log10(a),np.log10(TIMES_m1lmc),marker='o',label="With parallelization")
# plt.plot(np.log10(a),np.log10(TIMES_m1lmc_unthreaded),marker='<',color='r',label="No parallelization")
# plt.xlabel("$log_{10}$ of the number of samples for MC simulations \n with Euler schematization")
# plt.ylabel("$log_{10}$ of the computation time")
# plt.legend(loc=2)
# plt.tight_layout()
# plt.show()
