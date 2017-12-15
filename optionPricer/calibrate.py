from mlmc import optionPricer
import numpy as np
import scipy.stats as ss

o=optionPricer(100,100,0.25,1,r=0.05)

############# CONSTANTES NUMÉRIQUES ################

n_steps=20
n_min=30
n_max=90
n_a=2
n_b=5000
m=7
eps=1e-3

########## PAR RECUIT SIMULÉ #############

def simulated_annealing(n,m,n_steps=5):
    t=0
    for _ in range(n_steps):
        t+=o.price(method='mlmc',n=n,m=m)[1]
    t/=n_steps
    T0=np.sqrt(n)
    T=T0
    a=2e-1
    k=1
    T_min=1e-1
    N=1000
    best_N=N
    time_best_N=0
    time_N=0
    for _ in range(n_steps):
        time_N+=o.price(N=best_N,method="m1lmc")[1]
    time_N/=n_steps
    old_cost=(t-time_N)**2
    count=0
    while T>T_min:
        if time_N>t:
            N=int(best_N*0.95)
        elif time_N<t:
            N=int(best_N*1.05)
        time_N=0
        for _ in range(n_steps):
            time_N+=o.price(method="m1lmc",N=N)[1]
        time_N/=n_steps
        new_cost=(t-time_N)**2
        if new_cost<old_cost or ss.bernoulli(np.exp((old_cost-new_cost)/T))==1:
            old_cost=new_cost
            best_N=N
            count=0
        else:
            count+=1
        if count>1000:
            break
        T=T*(1+a*k)/(1+a*(k+1))
        k+=1
    return best_N


######### rechercche locale #########

def loc_search(n,eps,m,n_steps):
    time_n=0
    N=1000
    for _ in range(n_steps):
        time_n+=o.price('mlmc',n=n,m=m)[1]
    time_n/=n_steps
    time_N=0
    for _ in range(n_steps):
        time_N+=o.price("m1lmc",N=N,n=n)[1]
    time_N/=n_steps
    while abs(time_n-time_N)/time_n > eps:
        if time_N>time_n:
            N=int(N*0.97)
        else:
            N=int(N*1.03)

        time_N=0
        for _ in range(n_steps):
            time_N+=o.price("m1lmc",N=N,n=n)[1]
        time_N/=n_steps
        print("current N : ",N)
    return N

####### par dichotomie ##########

def dikotomy(n,eps,m,n_steps,n_a,n_b):
    time_n=0
    N=int((n_a+n_b)/2)
    N_old=N
    for _ in range(n_steps):
        time_n+=o.price('mlmc',n=n,m=m)[1]
    time_n/=n_steps
    time_N=0
    for _ in range(n_steps):
        time_N+=o.price("m1lmc",N=N,n=n)[1]
    time_N/=n_steps
    while abs(time_n-time_N)/time_n > eps:
        if time_N>time_n:
            n_a=N
        else:
            n_b=N

        time_N=0
        if N==N_old:
            break
        N_old=N
        for _ in range(n_steps):
            time_N+=o.price("m1lmc",N=N,n=n)[1]
        time_N/=n_steps
        print("current N : ",N)
    return N

########## COMPARAISON DES MÉTHODES #############
mlmc_time=[]
mc_ee_sa_time=[]
mc_dich_time=[]


for n in range(n_min,n_max,10):
    print((n-n_min)*100/(n_min-n_max)," %")

    mlmc_t=0
    mc_sa_t=0
    mc_dich_t=0
    mc_locsearch_t=0
    for _ in range(n_steps):
        print('    ',_*100/n_steps," %")
        mlmc_t+=o.price(method="mlmc",n=n)[1]
        mc_sa_t+=o.price(method="m1lmc",N=simulated_annealing(n,m))[1]
        mc_dich_t+=o.price(method="m1lmc",N=dikotomy(n,eps,m,n_steps,n_a,n_b))[1]
        mc_locsearch_t+=o.price(method="m1lmc",N=loc_search(n,eps,m,n_steps))[1]

    mlmc_t/=n_steps
    mc_sa_t/=n_steps
    mc_dich_t/=n_steps
    mlmc_time.append(mlmc_t)
    mc_ee_sa_time.append(mc_sa_t)
    mc_dich_time.append(mc_dich_t)

######## Affichage des différentes méthodes de comparaison ##########

n_s=list(range(n_min,n_max,10))

plt.plot(n_s,mlmc_time,label="MLMC",marker="s")
plt.plot(n_s,mc_sa_time,label="EE-SA",marker="o")
plt.plot(n_s,mc_dich_time,label="EE-DICH",marker="p")
plt.plot(n_s,mc_dich_time,label="EE-LS",marker="h")
plt.ylabel("Temps mis par la simulation avec $N_*$ échantillons")
plt.xlabel("$n$ utilisé pour le pas de discrétisation du schéma numérique de MLMC")
plt.legend(loc=2)
plt.show()