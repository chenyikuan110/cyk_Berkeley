clc
close all 
clear all
N = 500;
alpha = linspace(0,2,N);
ones = linspace(1,2,N);

D = 1;
Y2=1;
Y3=Y2*(1+0.1);

r1=0.05;
r2=r1*(1-0.5);
beta = 0.9;

B1 = D ./(((1+r1)*alpha + (1+r1)*(1+r2)*(1-alpha)));

B2 = D ./ ((1+r2)*ones);

figure(1)
hold on
plot(alpha,B1)
plot(alpha,B2)
hold off
legend('B1','B2')
xlabel('alpha')
title(strcat('r_t=',num2str(r1),',r_{t+1}=',num2str(r2)))

C1 = B1;
C2 = Y2 + B2 - (1+r1).*alpha.*B1;
C3 = Y3 - (1+r1).*(1+r2).*(1-alpha).*B1 - (1+r2).*B2;

i = find((C3>0));
ii = i(1);


figure(2)
hold on
plot(alpha(ii:N),C1(ii:N))
plot(alpha(ii:N),C2(ii:N))
plot(alpha(ii:N),C3(ii:N))
hold off
legend('Cy','Cm','Co')
xlabel('alpha')
title(strcat('r_t=',num2str(r1),',r_{t+1}=',num2str(r2)))

U = log(C1) + beta*(log(C2)) + beta^2*(log(C3));

figure(3)
plot(alpha(ii:N),U(ii:N))
legend('Util PV')
xlabel('alpha')
title(strcat('r_t=',num2str(r1),',r_{t+1}=',num2str(r2),',\beta=',num2str(beta)))