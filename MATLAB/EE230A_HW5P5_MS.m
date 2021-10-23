clc
clear
close all

Nd = linspace(1e20,1e23,1000);
Nc = 2.8e25; % unit 1/m^3

coeff = 2*11.7*8.854e-12/(1.6e-19); % 2*epsilon_Si/q

W1 = sqrt(coeff.*(1./Nd).*(0.5-0.026.*log(Nc./Nd)));
W2 = sqrt(coeff.*(1./Nd).*(0.6-0.026.*log(Nc./Nd)));
W3 = sqrt(coeff.*(1./Nd).*(0.7-0.026.*log(Nc./Nd)));

set(gca, 'XScale', 'log')
figure(1);
hold on
semilogx(Nd/1e6,W1)
semilogx(Nd/1e6,W2)
semilogx(Nd/1e6,W3)
ylabel('W_{dep}(m)')
xlabel('N_d(cm^{-3})')
title('Depletion width vs Doping Concentration')
legend('\Phi=0.5','\Phi=0.6','\Phi=0.7')
