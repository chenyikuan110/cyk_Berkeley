clc
close all
clear all
L = 1; %meter
c = 3e8;
period = L/c*2;
t = linspace(-period*0.1,period*1.1,200);
V = zeros(size(t));
Z_L = 100;
Z_0 = 50; % Ohms

gamma_L = (Z_L-Z_0)/(Z_L+Z_0);

k = 0;
for i=1:length(t)-1
   display(i)
    if(t(i)*c < 2*k*L && t(i+1)*c >= k*2*L)
       V(i) = 1*gamma_L^(k);
       k = k+1;
    end
    
end

stem(t,V)
title(strcat('V(z=0,t) for load termination = ',num2str(Z_L),'{\Omega}',',{\Gamma}_{L} = ',num2str(gamma_L)))
ylabel('V/V_{in}')
xlabel('t(s)')'

%% Smith chart
close all
clc
z = 0;
gamma = z2gamma(z);
figure
smithchart(gamma)
title({'One-port S-parameter for open',' ',' '})


