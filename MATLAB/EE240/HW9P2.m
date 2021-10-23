%%
close all
clear
clc
a0 = 1e4;
p1 = -1e6*2*pi;


figure(2)
    p2 = -560000*1e6*2*pi;
    k = a0;
    z = [];
    p = [p1,p2]
    [b,a] = zp2tf(z,p,k)
    openloop = tf([b],[a/(p1*p2)])
    closedloop = feedback(openloop,1)

    step(closedloop)
    legend(strcat('f_p2 = ',num2str(-p2/1e6/2/pi),'MHz'))
    figure()
    margin(openloop)    

%%
close all
clc
figure(3)
datacursormode on
wp2 = linspace(1e9,1e11,800);
tmax = double(zeros(1,800));
xx = 0.001;
for i = 1:length(wp2)
    p2 = -wp2(i);
    k = 2997;
    z = [];
    p = [p1,p2];
    [b,a] = zp2tf(z,p,k);
    openloop = tf([b],[a/(p1*p2)]);
    closedloop = feedback(openloop,0.5);
    [Y, T] = step(closedloop,180e-9);
    for j = 1:length(T)-1
        if((Y(j)<= 1-xx && Y(j+1) >1-xx) || (Y(j)>= 1+xx && Y(j+1) <1+xx))
            tmax(i) = T(j);
        end
    end
    if(tmax(i) == 0)
        i
        tmax(i)
        step(closedloop)
         getchar
    end
   
    %tmax(i)
    %step(closedloop);
    %getchar
    %legendInfo{i} = [strcat('f_p2 = ',num2str(-p2/1e6/2/pi),'MHz')];
    %margin(closedloop)
    %figure(4)
    %step(closedloop);
end  
semilogx(-wp2./p1,tmax)
title('t_{settling} vs {\omega}_{p2}/{\omega}_{p1} ')
xlabel('{{\omega}_{p2}}/{{\omega}_{p1}}')
ylabel('t(s)')
display('hi')
p2 = -wp2(find(tmax==min(tmax)));
if(length(p2)>1)
    p2 = p2(1)
end
    k = 2997;
    z = [];
    p = [p1,p2];
    [b,a] = zp2tf(z,p,k);
    openloop = tf([b],[a/(p1*p2)]);
    closedloop = feedback(openloop,1);
    figure()
margin(openloop)
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