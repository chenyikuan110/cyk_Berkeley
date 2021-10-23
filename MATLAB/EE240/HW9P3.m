%%
close all
clear
clc
gm2=0.1e-3*2/0.25;
gm6 = sqrt(2)*gm2;

C = 500e-15;
R_TAIL1 = 100e3;
R_TAIL2 = 11.3e6;

figure(3)
hold on
%openloop = tf([b],[a/(p1*p2)])
openloop = tf([80*C*R_TAIL1,80*(2*gm2*R_TAIL1)],[C*R_TAIL1,1]);
    closedloop = feedback(openloop,0)
    [mag,phase,w] = bode(closedloop,{1,1e11})
openloop = tf([80*C*R_TAIL2,80*(2*gm2*R_TAIL2)],[C*R_TAIL2,1]);
    closedloop = feedback(openloop,0)
    [mag,phase,w] = bode(closedloop,{1,1e11})
    semilogx(w,mag2db(mag(1,:)),w,mag2db(mag(1,:)))
    
    
    title('CMRR')
    ylabel('CMRR (dB)')
    xlabel('\omega (rad/s)')