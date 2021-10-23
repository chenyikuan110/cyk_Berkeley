%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                 Successive Approximation ADC         
%          
%                 Chuyao Cheng and Yikuan Chen
%                           Nov 2019
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
clear 
close all
clc

%function [adcout]=SAR_conventional(nbit)
% some design parameters
Vsupply = 1.2;
Vref = 1.2;
nbit = 13;
fsample = 25e6;  %25MHz
NN = 4;
fin = fsample/2/NN;  %3.125MHz


sample_num_per_cycle = fsample/fin;
sample_num = ceil(sample_num_per_cycle*8192/NN);
Input_power = -0; % dBFS


% initialize ADC
import my_sar_adc
my_ADC = my_sar_adc(Vsupply, Vref,nbit,fsample)

Zc = 1/(2*pi*fin*my_ADC.Cp_tot_real);
filter = Zc/abs(my_ADC.Ron+Zc);
Input_coeff = 10^(Input_power/20)*filter;


% run ADC
t = linspace(0,(sample_num-1)/fsample,sample_num);
x = Input_coeff*Vref*cos(2*pi*fin*t);

%t = linspace(0,(2^nbit*50)-1,2^nbit*50);
%x = Vref*linspace(-2^(nbit-1),2^(nbit-1)-1,2^(nbit)*50)/(2^nbit/2);
%Vref*(t/(2^nbit))-Vref;

%stairs(t,x)

Y = my_ADC.run_adc(t,x);

% YH = histogram(Y,(2^nbit));
% plot(YH.Values(1:2^nbit-1)/50-1)
% title('DNL plot using Histogram Method')
% xlabel('output code')
% ylabel('DNL (LSB)')
% ylim([-1 1])
% xlim([0 2^nbit])

% plot result
% up sample > 1 if you want to see the harmonics of the staircase waveform
up_sample_ratio = 1;
f_resample = fsample*up_sample_ratio;

Y_HOLD = zeros(1,length(Y)*up_sample_ratio);
Y_upsampled = upsample(Y,up_sample_ratio);

for j = 1:up_sample_ratio
    Y_HOLD = Y_HOLD + Y_upsampled;
    Y_upsampled = circshift(Y_upsampled,1);
end

t_up = t;
x_up = x;

% ------------------ Below is for plotting ------------------- %

% plot - Time Domain
figure(2);
hold on
plot(t_up, x_up,'MarkerFaceColor',[0,0.4470,0.7410])
stairs(t_up, Y_HOLD,'MarkerFaceColor',[0.8500,0.3250,0.0980])
hold off
legend('Input','ADC')
title('Time Domain Input and Output')
xlabel('t(s)')
ylabel('signal(V)')

% plot - spectrum
% frequency axis
w = linspace(0,length(Y_HOLD)-1,length(Y_HOLD));
omega = w/length(Y_HOLD)*2*pi;
freq = omega/(2*pi)*f_resample;

% output
y_fft = fft(Y_HOLD);
y_fft_norm_mag = abs(y_fft)/sample_num*2;

% input
XX = fft(x_up);
XX_norm_mag = abs(XX)/sample_num*2;

figure(3)
hold on
plot(freq(1:floor(length(Y_HOLD)/2)+1),mag2db(XX_norm_mag(1:floor(length(Y_HOLD)/2)+1)),...
    'MarkerFaceColor',[0,0.4470,0.7410])
plot(freq(1:floor(length(Y_HOLD)/2)+1),mag2db(y_fft_norm_mag(1:floor(length(Y_HOLD)/2)+1)),...
    'MarkerFaceColor',[0.8500,0.3250,0.0980])
legend('Input','ADC')

hold off
%plot(freq,y_fft_norm_mag)
title('Spectrum of the sampled data')
xlabel('MHz')
ylabel('dBFS')

peak_freq = find(y_fft_norm_mag==max(y_fft_norm_mag),1);

P_Noise = sum(y_fft_norm_mag(2:peak_freq-1).^2) ...
    + sum(y_fft_norm_mag(peak_freq+1:floor(length(y_fft)/2)).^2);

%P_spike = (max(max(y_fft_norm_mag(2:peak_freq-1)),...
%    max(y_fft_norm_mag(peak_freq+1:floor(length(y_fft)/2)))));

P_signal = y_fft_norm_mag(peak_freq)^2;
Y_SNR = 10*log10(y_fft_norm_mag(peak_freq)^2/P_Noise);
%Y_SFDR = 10*log10(y_fft_norm_mag(peak_freq)^2/P_spike);
Y_SNR = snr(Y_HOLD)
Y_SFDR = sfdr(Y_HOLD)
Total_power = my_ADC.Power_tot;
