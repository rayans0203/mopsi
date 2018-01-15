#include "option.h"

int main(){

    const double K=100;
    const double S0=100;
    const double r=log(1.1);
    const double T=3;
    const double vol=0.2;
    const double kappa=3.0;
    const double rho=0;
    const double xi=0.2;
    const double theta=0.9;
    const double v0=0.1;

    const int N_samples=10000;
    const int n_euler=100;
    const int m_levels=2;

    Payoff* payoff= new PayoffCall(K);
    //Model* model= new BlackScholes(r,vol);
    Model* model= new Heston(r,kappa,theta,xi,rho,v0);
    EuropeanOption* o= new EuropeanOption(K,T,S0,model,payoff);

    //cout << o->BlackScholes("call") << endl;
    //cout << o->MC_explicit(N_samples)<< endl;

    // asian option: reference price: 11.8424
    cout << o->MC(N_samples,n_euler) << endl;
    cout << o->MLMC(n_euler,m_levels) << endl;
    return 0;
}
