%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%               successive approximation adc                 %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
clear 
close all
clc

%function [adcout]=SAR_conventional(nbit)
% some design parameters
Vsupply = 1.2;
Vref = 1.2;
nbit = 12;
fsample = 25e6;  %25MHz
fin = fsample/2/50.5;  %3.125MHz
fsar = fsample * nbit; %300MHz
sample_num_per_cycle = fsample/fin;
sample_num = ceil(sample_num_per_cycle*8);
LSB= 2*Vref / 2^nbit;
Vcm = Vref / 2;
Input_power = 0; % dBFS
Input_coeff = 10^(Input_power/20);
%time_array = [(1/fsar):(1/fsar):sample_num*(1/fsar)];

C_array=[];
for r=1:nbit-1
    C_array=[C_array,2^(nbit-r-1)];
end
C_array = [C_array, 1];
%positive end & negative end 
Cp = C_array; 
Cn = C_array;
Cgd = 0.1e-15;
Cpar_p = 0;  % To be determiend
Cpar_n = Cpar_p;
Cp = Cp + Cpar_p;
Cn = Cn + Cpar_n;
Cp_tot = sum(Cp);
Cn_tot = sum(Cn);

%% Power calculation
% Assume the output comparator is a StrongArm Latch
% http://www.seas.ucla.edu/brweb/papers/Journals/BR_Magzine4.pdf
%
% We calculate the gm based on our settling requirement
%
Cpp = 40e-15; % tbd
Vthn = 0.5; % tbd
T_settle = 1/fsar/2;
I_tail = 2*Cpp*Vthn/T_settle; % Unit:Amp
Temp = 298; % Kelvin
gamma = 1;
% From offset 
% Voffset less than 0.5 LSB
Voffset_max = Vref/(2^nbit)/2
% Voffset = deltaCp/Cpp*I_tail/2/gm
deltaCp = Cpp*0.05; % tbd
gm_min = deltaCp/Cpp*I_tail/2/Voffset_max;
kT = 4.11e-21;

% input referred noise 
%
% vn^2 = (2*kT/Cpp+2*(4*kT*gamma*gm/Cpp^2*T_settle))/Av^2 
%
% Av=gm*Vthn/(I_tail/2)
%
% ==> vn^2 = (2*kT/Cpp+2*(4*kT*gamma*gm/Cpp^2*T_settle))/(gm*Vthn/(I_tail/2))^2
%
% Our goal is to let vn less than quantization noise, so set 2*vn^2 to be 
% equal to quantization noise * 1/4 (2*vn^2 because we're differential)
% 1/4 not 1/2 because we also have kT/Ctot noise on the DAC 
%
% 2*vn^2 = 1/2*((1.2^2/2)/10^((12*6.02+1.67)/10))
%
%
vnsquare_max = 1/2*((Vref^2/2)/10^((nbit*6.02+1.67)/10))/4;
Av_min = gm_min*Vthn/(I_tail/2);

gm_sweep = linspace(gm_min,gm_min*400,100);
vnsq_sweep = (2*kT/Cpp+2*(4*kT*gamma.*gm_sweep/Cpp^2*T_settle))./((gm_sweep*Vthn/(I_tail/2)).^2);

figure(3)
hold on
plot(gm_sweep,vnsq_sweep,'b');
plot(gm_sweep,vnsquare_max*ones(length(gm_sweep)),'c');
hold off

% choose the gm, get Av and actual Voffset
gm = gm_sweep(find(vnsq_sweep < vnsquare_max ,1 ));
Av = gm*Vthn/(I_tail/2);
Voffset = deltaCp/Cpp*I_tail/2/gm;
vn_stdev = sqrt((2*kT/Cpp+2*(4*kT*gamma*gm/Cpp^2*T_settle))/((gm*Vthn/(I_tail/2))^2));

% assume C_load is a FO1 inverter
C_load = 1e-15; % tbd
Cp_tot_real = kT/vnsquare_max;
Cn_tot_real = Cp_tot_real;

Cp_real = Cp * Cp_tot_real/Cp_tot;
Cn_real = Cn * Cn_tot_real/Cn_tot;

kick_back = (Cgd)/(Cp_tot_real);

Power_latch = fsar*(2*Cpp+C_load)*Vsupply^2;
Power_DAC = fsar*(Cn_tot_real+Cp_tot_real)*Vsupply^2; % unit is Watt
Power_tot = Power_latch + Power_DAC

%% Run ADC
output = [];
vp = [];
vn = [];
Vin = 0;
history = 0;

for t = linspace(0,(sample_num-1)/fsample,sample_num)
    Vin = Input_coeff*Vref*sin(2*pi*fin*t);
    % sampling input
    out = zeros(1, nbit);
    top = ones(nbit, 1);
    bottom = ones(nbit, 1);
    Vinp = Vcm + 0.5*Vin;
    Vinn = Vcm - 0.5*Vin;
    
    %first bit
    Vxp = Vinp;
    Vxn = Vinn;

    if Vxp > Vxn
        top(1) = 0;
        out(1) = 1;
    else
        bottom(1) = 0;
        out(1) = 0;
    end
    % SAR logic
    for i=2:nbit
        % input referred noise additive
        vnp = randn()*vn_stdev + history*kick_back*Vref;
        vnn = randn()*vn_stdev - history*kick_back*Vref;
        Vxp = (Cp_real * top * Vref - Vref * Cp_tot_real + Vinp * Cp_tot_real) / Cp_tot_real + vnp;
        Vxn = (Cn_real * bottom * Vref - Vref * Cn_tot_real + Vinn * Cn_tot_real) / Cn_tot_real +vnn;

        if (Vxp+Voffset) > Vxn
            out(i) = 1;
            history = 1;
            top(i) = 0;
        else
            out(i) = 0;
            history = -1;
            bottom(i) = 0;
        end
    end
    output = [output;out];
    
end

% convert to decimal
output_dec = [];
for i=1:sample_num
    row = output(i,:);
    val = 0;
    for j=1:nbit
        val = val * 2 + row(j);
    end
    val = (val * 2 * Vref / 2^nbit) - Vref;
    output_dec = [output_dec, val];
end



% x = Input_coeff*Vref*sin(2*pi*fin*t);
t = linspace(0,(sample_num-1)/fsample,sample_num);
t2 = t*fsample;

Y = output_dec(int32(t2+1));


up_sample_ratio = 1;
f_resample = fsample*up_sample_ratio;

Y_HOLD = zeros(1,length(Y)*up_sample_ratio);
Y_upsampled = upsample(Y,up_sample_ratio);

for j = 1:up_sample_ratio
    Y_HOLD = Y_HOLD + Y_upsampled;
    Y_upsampled = circshift(Y_upsampled,1);
end
t_up = linspace(0,(sample_num-1)/fsample,sample_num*up_sample_ratio);
x_up = Input_coeff*Vref*sin(2*pi*fin*t_up);

% plot
figure(1);

hold on
%plot (t2, output_dec(int32(t2+1)));
plot(t_up, x_up,'MarkerFaceColor',[0,0.4470,0.7410])
stairs(t_up, Y_HOLD,'MarkerFaceColor',[0.8500,0.3250,0.0980])
hold off
legend('Input','ADC')
title('Time Domain Input and Output')
xlabel('t/sec')

% ------------------------- end of time domain plot -----------------
% spectrum


% frequency axis
w = linspace(0,length(Y_HOLD)-1,length(Y_HOLD));
omega = w/length(Y_HOLD)*2*pi;
freq = omega/(2*pi)*f_resample;

y_fft = fft(Y_HOLD);
y_fft_norm_mag = abs(y_fft)/max(abs(y_fft));

XX = fft(x_up);
XX_norm_mag = abs(XX)/max(abs(XX));

figure(2)
hold on
plot(freq(1:length(Y_HOLD)/2),mag2db(XX_norm_mag(1:length(Y_HOLD)/2)),...
    'MarkerFaceColor',[0,0.4470,0.7410])
plot(freq(1:length(Y_HOLD)/2),mag2db(y_fft_norm_mag(1:length(Y_HOLD)/2)),...
    'MarkerFaceColor',[0.8500,0.3250,0.0980])
legend('Input','ADC')
hold off
%plot(freq,y_fft_norm_mag)
title('Spectrum of the sampled data')
xlabel('MHz')
ylabel('dBFS')

Y_SNR = snr(Y_HOLD)


