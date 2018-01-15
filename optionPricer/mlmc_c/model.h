#ifndef MODEL_H
#define MODEL_H

#include <cmath>
#include "utils.h"

class Model{
protected:
    double r;
public:
    Model(const double& r_){r=r_;}
    virtual ~Model(){}

    virtual double rate() const=0;
    virtual double volatility() const=0;
    virtual void euler_MC(double& S, const int& n_euler, const double& dt) const =0;
    virtual void euler_MLMC(double& S_thin, double& S_coarse,
                            const double& dt_thin, const double& dt_coarse,
                            const int& n_euler, const int& m_levels) const=0;
    virtual void riemann_MC(double& I,const int& n_euler, const double& dt)const=0;
    virtual void riemann_MLMC(double& I_thin, double& I_coarse,
                    const double& dt_thin, const double& dt_coarse,
                    const int& n_euler, const int& m_levels)const=0;
};

class BlackScholes: public Model{
    double vol;
public:
    BlackScholes(const double& r_, const double& vol_): Model(r_) {vol=vol_;}
    ~BlackScholes(){}

    double rate()const{return r;}
    double volatility()const{return vol;}
    void euler_MC(double& S,const int& n_euler, const double& dt) const;
    void euler_MLMC(double& S_thin, double& S_coarse,
                    const double& dt_thin, const double& dt_coarse,
                    const int& n_euler, const int& m_levels) const;
    void riemann_MC(double& I,const int& n_euler, const double& dt)const;
    void riemann_MLMC(double& I_thin, double& I_coarse,
                    const double& dt_thin, const double& dt_coarse,
                    const int& n_euler, const int& m_levels)const;
};

class Heston: public Model{
    double kappa;
    double theta;
    double rho;
    double xi;
    double v0;
public:
    Heston(const double& r_, const double& kappa_,
           const double& theta_, const double& xi_,
           const double& rho_, const double& v0_): Model(r_){kappa=kappa_;theta=theta_;xi=xi_;rho=rho_;v0=v0_;}
    ~Heston(){}

    double rate()const{return r;}
    double volatility()const{return 0;}

    vector<double> build_Cox_Ross(const vector<double>& W,const double& sqrt_dt) const;
    void euler_MC(double& S,const int& n_euler, const double& dt) const;
    void euler_MLMC(double& S_thin, double& S_coarse,
                    const double& dt_thin, const double& dt_coarse,
                    const int& n_euler, const int& m_levels) const;
    void riemann_MC(double& I,const int& n_euler, const double& dt)const{I=-1;}
    void riemann_MLMC(double& I_thin, double& I_coarse,
                    const double& dt_thin, const double& dt_coarse,
                    const int& n_euler, const int& m_levels)const{I_thin=-1;I_coarse=-1;}
};



#endif // MODEL_H
