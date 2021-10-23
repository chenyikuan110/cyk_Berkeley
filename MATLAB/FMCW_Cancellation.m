clear all
clc
f_start = 1.7;
f_del = 2;
t_up = 5;
f_nyq = 2*(f_start+f_del);

t = linspace(0,2*t_up,1000);
V_in = zeros(size(t));

for i=1:floor(length(t)/2)
    V_in(i) = sin((f_start+f_del/t_up*t(i))*2*pi*t(i)); 
end
for i=floor(length(t)/2)+1:length(t)
    V_in(i) = sin((f_start+f_del-f_del/t_up*t((i)-t_up))*2*pi*t(i)); 
end
figure(1)
plot(t,V_in);

%spectrogram(V_in)