%% carrier profile - exact
clc
clear
close all

m0 = 9.1e-21; % unit kg
mn = m0*0.26;
mp = m0*0.39;

EG=1.12; % unit eV
EV=0;
EC=EV+EG;

k = 8.617e-5; % unit eV/K
T = 300; % unit K
h = 4.1357e-15; % unit eV*s
kT = k*T;

convfact = 1.56e22; % to get the correct unit

EF_MINUS_EC = 3; % unit eV/kT=unitless

% calculation 
E = linspace(-1,EC+1,200);
n = 8*pi*sqrt(2)*(mn/h^2)^(3/2)*(((E-EC)).^0.5)./(1+exp((E-EC)/kT)*exp(-EF_MINUS_EC));
p = 8*pi*sqrt(2)*(mp/h^2)^(3/2)*(((EV-E)).^0.5)./(1+exp((EV-E)/kT)*exp(EF_MINUS_EC)*exp(EG/kT));

n = n*convfact;
p = p*convfact;
% plot
figure(1)
hold on
plot(n,E)
plot(p,E)
legend('n','p')
ylabel('E(eV)')
xlabel('n(eV^{-1}*cm^{-3}))')
title('Energy vs Carrier Density')

hold off

figure(2)
hold on
plot(log10(real(n)),E)
plot(log10(real(p)),E)
%plot(linspace(0,max(log10(real(n))),2),EC)
%plot(linspace(0,max(log10(real(p))),2),EV)
legend('n','p')
ylabel('E(eV)')
xlabel('log_{10}(n)(eV^{-1}*cm^{-3}))')
title('Energy vs log Carrier Density')
hold off


%% problem ii
clc
clear
close all

m0 = 9.1e-21; % unit kg
mn = m0*0.26;
mp = m0*0.39;

EG=1.12; % unit eV
EV=0;
EC=EV+EG;

k = 8.617e-5; % unit eV/K
T = 300; % unit K
h = 4.1357e-15; % unit eV*s
kT = k*T;

convfact = 1.56e22; % to get the correct unit

EF_MINUS_EC = -(EG/kT+3); % unit eV/kT=unitless

% calculation 
E = linspace(-1,EC+1,200);
n = 8*pi*sqrt(2)*(mn/h^2)^(3/2)*(((E-EC)).^0.5)./(1+exp((E-EC)/kT)*exp(-EF_MINUS_EC));
p = 8*pi*sqrt(2)*(mp/h^2)^(3/2)*(((EV-E)).^0.5)./(1+exp((EV-E)/kT)*exp(EF_MINUS_EC)*exp(EG/kT));

n = n*convfact;
p = p*convfact;
% plot
figure(3)
hold on
plot(n,E)
plot(p,E)
legend('n','p')
ylabel('E(eV)')
xlabel('n(eV^{-1}*cm^{-3}))')
title('Energy vs Carrier Density')

hold off

figure(4)
hold on
plot(log10(real(n)),E)
plot(log10(real(p)),E)
legend('n','p')
ylabel('E(eV)')
xlabel('log_{10}(n)(eV^{-1}*cm^{-3}))')
title('Energy vs log Carrier Density')
hold off

figure(5)
plot(E,1./(1+exp((E-EC)/kT)*exp(-EF_MINUS_EC)));