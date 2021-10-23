%%
close all
clear
clc
a0 = 20;
p1 = -10e6*2*pi;
p2 = -40e6*2*pi;
k = a0;
z = [];
p = [p1,p2]
[b,a] = zp2tf(z,p,k)
gm=10e-3;
ro=3e3;
Cgs=200e-15;
CL=0.03e-12;

numerator = 0.5*(gm*ro)^2;

%openloop = tf([b],[a/(p1*p2)])
openloop = tf(numerator,[ro^2*CL*Cgs/2,(ro*Cgs+ro*gm*ro*CL/2),1]);
figure(3)

    closedloop = feedback(openloop,1)
    margin(closedloop)
%%
hold on
for fb = [0,0.5,1]
    closedloop = feedback(openloop,fb)
    % 
    % figure(1)
    % bode(openloop,closedloop)
    % legend show
    % figure(2)
    % margin(closedloop)
    % legend show
    bode(closedloop)
%      a = a0/(1+fb*a0)
%      [Y,T,X] = step(closedloop,100e-9);
%      plot(T,Y/a)
     legend('f = 0','f = f_{crit}','f = 1')
     %pzmap(closedloop)
end
hold off
title('Bode plot for different f_{feedback}')
% title('Normalized step response for different f_{feedback}')