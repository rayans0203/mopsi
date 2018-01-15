#include "model.h"

void BlackScholes::euler_MC(double &S, const int &n_euler, const double &dt) const{
    std::random_device rd;
    std::mt19937 gen(rd());
    std::normal_distribution<double> distribution(0.0,1.0);
    for (int i = 0; i < n_euler;i++) S=S*(1+r*dt+vol*(distribution(gen)*sqrt(dt)));
}

void BlackScholes::euler_MLMC(double& S_thin, double& S_coarse,
                              const double& dt_thin, const double& dt_coarse,
                              const int& n_euler, const int& m_levels) const{
    std::random_device rd;
    std::mt19937 gen(rd());
    std::normal_distribution<double> distribution(0.0,1.0);
    for (int i=0; i < n_euler;i++){
        S_thin=S_thin*(1+r*dt_thin+vol*(distribution(gen)*sqrt(dt_thin)));
        if (i%m_levels==0) S_coarse=S_coarse*(1+r*dt_coarse+vol*(distribution(gen)*sqrt(dt_coarse)));
    }
}

void BlackScholes::riemann_MC(double &I, const int &n_euler, const double &dt) const{
    vector<double> W=build_BM(n_euler,sqrt(dt));
    std::random_device rd;
    std::mt19937 gen(rd());
    std::normal_distribution<double> distribution(0.0,1.0);
    for (int i = 0; i < n_euler;i++) I+=(dt/2)*(exp((r-0.5*vol*vol)*i*dt+vol*sqrt(i*dt)*distribution(gen))
                                                    +exp((r-0.5*vol*vol)*(i+1)*dt+vol*sqrt((i+1)*dt)*distribution(gen)));
}

void BlackScholes::riemann_MLMC(double& I_thin, double& I_coarse,
                                const double& dt_thin, const double& dt_coarse,
                                const int& n_euler, const int& m_levels) const{
    std::random_device rd;
    std::mt19937 gen(rd());
    std::normal_distribution<double> distribution(0.0,1.0);
    for (int i=0; i < n_euler;i++){
        I_thin+=(dt_thin/2)*(exp((r-0.5*vol*vol)*i*dt_thin+vol*sqrt(i*dt_thin)*distribution(gen))
                                 +exp((r-0.5*vol*vol)*(i+1)*dt_thin+vol*sqrt((i+1)*dt_thin)*distribution(gen)));
        if (i%m_levels==0) I_coarse+=(dt_coarse/2)*(exp((r-0.5*vol*vol)*i*dt_coarse+vol*sqrt(i*dt_coarse)*distribution(gen))
                                                        +exp((r-0.5*vol*vol)*(i+1)*dt_coarse+vol*sqrt((i+1)*dt_coarse)*distribution(gen)));
    }
}

vector<double> Heston::build_Cox_Ross(const vector<double>& W,const double& sqrt_dt) const{
    vector<double> W_corr=build_BM_corr(W,sqrt_dt,rho);
    int n_euler=W.size()-1;
    vector<double> volatility;
    volatility.push_back(v0);
    for (int k=0; k < n_euler-1;k++){
        double vol=volatility.at(volatility.size()-1);
        volatility.push_back(abs(vol+kappa*(theta-vol)*sqrt_dt*sqrt_dt+xi*sqrt(vol)*(W_corr.at(k+1)-W_corr.at(k))));
    }
    return volatility;
}

void Heston::euler_MC(double &S, const int &n_euler, const double &dt) const{
    vector<double> W=build_BM(n_euler,sqrt(dt));
    vector<double> volatility=this->build_Cox_Ross(W,sqrt(dt));
    for (int i = 0; i < n_euler;i++) S=S*(1+r*dt+volatility.at(i)*(W.at(i+1)-W.at(i)));
}

void Heston::euler_MLMC(double& S_thin, double& S_coarse,
                        const double& dt_thin, const double& dt_coarse,
                        const int& n_euler, const int& m_levels) const{
    vector<double> W_thin=build_BM(n_euler,sqrt(dt_thin));
    vector<double> W_coarse;
    W_coarse.push_back(0);
    for (int i=0; i < int(n_euler/m_levels);i++) W_coarse.push_back(W_thin.at((i+1)*m_levels));

    vector<double> volatility_thin=this->build_Cox_Ross(W_thin,sqrt(dt_thin));
    vector<double> volatility_coarse=this->build_Cox_Ross(W_coarse,sqrt(dt_coarse));

    for (int i=0; i < n_euler;i++){
        S_thin=S_thin*(1+r*dt_thin+volatility_thin.at(i)*(W_thin.at(i+1)-W_thin.at(i)));
        if (i%m_levels==0) S_coarse=S_coarse*(1+r*dt_coarse+volatility_coarse.at(i/m_levels)*(W_coarse.at(i/m_levels+1)-W_coarse.at(i/m_levels)));
    }
}
