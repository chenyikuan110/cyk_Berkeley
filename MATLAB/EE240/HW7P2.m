close all
clear
clc
tau = 1e-6;
a0 = 1e6;
i = 1;
for f = [1,0.1,0.01,0.001]
    openloop = tf([a0],[tau,(1+f*a0)]);
    figure(i)
    i = i+1;
    bode(openloop)
    title(['Bode Plot for f=',num2str(f)])
end

%%
close all
clear
clc
a0 = 10000;
Cf = 0.05e-6;
Rf = 200;
wp1 = 10;
openloop = tf([10000*Cf*Rf,10000],[Cf*Rf/wp1,(Cf*Rf+1/wp1),10001]);
[Gm,Pm,Wcg,Wcp] = margin(openloop)

figure(1)
margin(openloop)
figure(2)
pzmap(openloop)

%%
close all
clear
clc
a0 = 10000;
p1 = -1e3*2*pi;
p2 = -54181697;
p3 = -200e6*2*pi
k = a0;
z = [-p2];
p = [p1,p2,p3]
[b,a] = zp2tf(z,p,k)

openloop = tf([b],[a/(-p1*p2*p3)])
closedloop = feedback(openloop,0.5)

figure(1)
bode(openloop,closedloop)
legend show
figure(2)
margin(closedloop)
legend show
figure(3)
pzmap(openloop)