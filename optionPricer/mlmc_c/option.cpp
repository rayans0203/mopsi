#include "option.h"

Option::Option(const double& K_,const double& T_,
               const double& S0_, Model* model_,
               Payoff* payoff_){
    payoff=payoff_;
    K=K_;
    T=T_;
    S0=S0_;
    model=model_;
}

Option::~Option(){
    delete payoff;
    delete model;
}

EuropeanOption::EuropeanOption(const double& K_,const double& T_,
                               const double& S0_, Model* model_,
                               Payoff* payoff_): Option(K_,T_,S0_,model_,payoff_){}

EuropeanOption::~EuropeanOption(){
    delete payoff;
    delete model;
}

double EuropeanOption::BlackScholes(const string& order) const{
    double d1=(log(S0/K) + (model->rate()+0.5*model->volatility()*model->volatility())*T)/(model->volatility()*sqrt(T));
    double d2=d1-model->volatility()*sqrt(T);
    if (order=="call") return S0*normalCFD(d1)-exp(-model->rate()*T)*K*normalCFD(d2);
    else if (order=="put") return K*exp(-model->rate()*T)*normalCFD(-d2)-S0*normalCFD(-d1);
    else throw std::domain_error("Order must be either 'call' or 'put'");
}

double EuropeanOption::MC_explicit(const int& N_samples) const{
    std::random_device rd;
    std::mt19937 gen(rd());
    std::normal_distribution<double> distribution(0.0,sqrt(T));
    double payoff_price=0;

    for (int i=0; i < N_samples;i++){
        payoff_price+=payoff->operator ()(S0*exp((model->rate()-0.5*model->volatility()*model->volatility())*T+model->volatility()*distribution(gen)));
    }
    return exp(-model->rate()*T)*(payoff_price/N_samples);
}

double EuropeanOption::MC(const int& N_samples, const int& n_euler) const{
    double payoff_price=0;
    double dt=T/n_euler;
    for (int j = 0; j < N_samples;j++){
        double S=S0;
        model->euler_MC(S,n_euler,dt);
        payoff_price+=payoff->operator ()(S);
    }
    return exp(-model->rate()*T)*(payoff_price/N_samples);
}

double EuropeanOption::MLMC(const int& n_euler, const int& m_levels) const{
    int L=int(log(n_euler)/log(m_levels));
    int N0=int((m_levels-1)*T*n_euler*n_euler*L);

    double payoff_price=0;
    for (int i =0; i <N0;++i){
        double S=S0;
        model->euler_MC(S,1,T);
        payoff_price+=payoff->operator ()(S);
    }
    payoff_price/=N0;

    for (int level=1; level < L; level++){
        int nl=pow(m_levels,level);
        int Nl=int(N0/nl);
        double dt_thin=T/nl;
        double dt_coarse=m_levels*dt_thin;
        for (int j = 0; j < Nl; j++){
            double S_thin=S0;
            double S_coarse=S0;
            model->euler_MLMC(S_thin,S_coarse,dt_thin,dt_coarse,nl,m_levels);
            payoff_price+=(payoff->operator ()(S_thin)-payoff->operator ()(S_coarse))/Nl;
        }
    }
    return exp(-model->rate()*T)*payoff_price;
}

AsianOption::AsianOption(const double& K_,const double& T_,
                         const double& S0_, Model* model_,
                         Payoff* payoff_): Option(K_,T_,S0_,model_,payoff_){}

AsianOption::~AsianOption(){
    delete payoff;
    delete model;
}

double AsianOption::MC(const int& N_samples, const int& n_euler) const{
    double payoff_price=0;
    double dt=T/n_euler;
    for (int j = 0; j < N_samples;j++){
        double I=0;
        model->riemann_MC(I,n_euler,dt);
        //cout << S0*I/T << endl;
        payoff_price+=payoff->operator ()(S0*I/T);
    }
    return exp(-model->rate()*T)*(payoff_price/N_samples);
}

double AsianOption::MLMC(const int& n_euler, const int& m_levels) const{
    int L=int(log(n_euler)/log(m_levels));
    int N0=int((m_levels-1)*T*n_euler*n_euler*L);

    double payoff_price=0;
    for (int i =0; i <N0;++i){
        double I=0;
        model->riemann_MC(I,1,T);
        payoff_price+=payoff->operator ()(S0*I/T);
    }
    payoff_price/=N0;
    for (int level=1; level < L; level++){
        int nl=pow(m_levels,level);
        int Nl=int(N0/nl);
        double dt_thin=T/nl;
        double dt_coarse=m_levels*dt_thin;
        for (int j = 0; j < Nl; j++){
            double I_thin=0;
            double I_coarse=0;
            model->riemann_MLMC(I_thin,I_coarse,dt_thin,dt_coarse,nl,m_levels);
            payoff_price+=(payoff->operator ()(S0*I_thin/T)-payoff->operator ()(S0*I_coarse/T))/Nl;
        }
    }
    return exp(-model->rate()*T)*payoff_price;
}

