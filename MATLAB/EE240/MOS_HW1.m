close all
clc

vgs = [0.8,1,1.5,2];
vds = linspace(0.1,5,50);
ids = zeros(length(vgs),length(vds));

vth = 0.7;
k_prime = 100E-6; % A/V
W = 10; %um
L = 1; %um
k = k_prime*W/L;
lambda = 0.04; %V^-1

figure(1)
hold on
for i = 1:length(vds)
    for j = 1:length(vgs)
        if(vgs(j)<vth)
            ids(i,j) = 0;
        elseif(vds(i)<vgs(j)-vth)
            % triode
            ids(i,j) = k*(vgs(j)-vth-vds(i)/2)*vds(i)*(1+lambda*vds(i));
        else
            % saturation
            ids(i,j) = k/2*(vgs(j)-vth)^2*(1+lambda*vds(i)); 
        end
    end
end


plot(vds,ids(:,:))
title('Ids vs Vgs')
xlabel('Vgs(V)')
ylabel('Ids(A)')
legend(strcat('Vgs(V)=',num2str(vgs(1))),strcat('Vgs(V)=',num2str(vgs(2))),...
    strcat('Vgs(V)=',num2str(vgs(3))),strcat('Vgs(V)=',num2str(vgs(4))));

for i = 1:length(vds)
    for j = 1:length(vgs)
        if(vgs(j)<vth)
            ids(i,j) = 0;
        elseif(vds(i)<vgs(j)-vth)
            % triode
            ids(i,j) = k*(vgs(j)-vth-vds(i)/2)*vds(i)*(1+lambda*vds(i));
        else
            % saturation
            ids(i,j) = k/2*(vgs(j)-vth)^2*(1+lambda*vds(i)); 
        end
        % boundary marks
        if(abs(vgs(j) - vth) < 1E-5 || abs(vds(i) - (vgs(j) - vth)) < 1E-5)
            scatter(vds(i),ids(i,j));
        end
    end
end