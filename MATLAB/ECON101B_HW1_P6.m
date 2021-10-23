%% ECON 101B 1.3 

clc 
clear
close all


c = linspace(0.001,200,100);
sigma = 0.99;

u1 = (c.^(1-sigma)-1)/(1-sigma);

figure(1)
plot(c,u1);
xlabel('c')
ylabel('u')
title(strcat('u(c) when \sigma=',num2str(sigma)))

% derivative
dudc1 = c.^(-sigma);
figure(2)
plot(c,dudc1);
xlabel('c')
ylabel('u')
title(strcat('du/dc when \sigma=',num2str(sigma)))



%% natural log

clc 
clear



c = linspace(0.001,200,100);

u2 = log(c);

figure(3)
plot(c,u2);
xlabel('c')
ylabel('u')
title('u(c)=ln(c)');

% derivative
dudc2 = 1./c;
figure(4)
plot(c,dudc2);
xlabel('c')
ylabel('u')
title('du/dc');