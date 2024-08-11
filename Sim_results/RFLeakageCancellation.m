clear all
close all
clc

% multi-path on/off
Multipath = 0

IQ_mismatch_on = 1; % set to 0 to turnoff IQ amplitude mismatch
noise_on = 1; % set to 0 to turn off thermal noise
averaging = 1; % if average is turned on, the frequency detection will be smoothed

num_averaging = 3; % using neigboring plus_minus num_average indexes

avg_window = triang(2*num_averaging+1);
avg_window = avg_window/sum(avg_window);

fRF = 135e9;
fBW = 10e9;
Tchirp = 100e-6;
K = fBW/Tchirp;

fRBW = 1/Tchirp;
dRBW = fRBW/fBW*3e8*Tchirp;
fsampling = fRBW * 1000;
N = floor(fsampling/fRBW);

PTX_dBm = 10;
Isolation = 30; %dB
Isolation_1 = 30; %dB

t = linspace(0,Tchirp*(1-1/N),N); % simulate one chirp
window = hamming(length(t));
window = window*length(window)/sum(window);

fig_count = 1;

f_range = 1/2 * 10e3;
% num_points = 3;
leak_dist = 1.7e-3+rand()*0.6e-3;
leak_dist_1 = 3e-2+rand()*0.1e-3; % second jammer

tau_leak = leak_dist/3e8;
tau_leak_1 = leak_dist_1/3e8;

tau_LORX  = (500e-6*rand())/3e8; % relative delay from LO splitter to RX mixer-input, make it a bit random

delay_step = 1.53e-12;
tau_tunable_array = 0e-12:delay_step:120e-12;
del_0 = zeros(1,length(tau_tunable_array));
del_2 = del_0;
yfft_1 = del_2; % bin[1] bookkeeping

curr_max_del_0 = 0;
curr_max_del_2 = 0;
curr_max_tau = 0;
curr_tau = tau_tunable_array(1);

DC_offset = randn()*0.001;

Phi_0 = 2*pi*rand(); % LO start at a random phase at t=0
Phi_1 = 0*2*pi*rand()/360/2; % keep the phase mismatch in the LO splitter less than 0.5 deg


sharpness_change = 0;

A0 = db2mag(PTX_dBm-Isolation)*sqrt(2); % sqrt(2) as the crest factor of sine
A1 = db2mag(PTX_dBm-Isolation_1)*sqrt(2);

IQ_mismatch = 1*db2mag(-0.5*IQ_mismatch_on);
IQ_phase_err = 1*pi/180; % phase error in IQ hybrid

SNRdB = 114; % relative to 0dBm full-scale; for 1000pts
sigma = noise_on*10^(SNRdB/10); %SNR to linear scale
N0 = 1/sigma;
Noise_i = sqrt(N0/2)*randn(size(t)); %computed noise
Noise_q = sqrt(N0/2)*randn(size(t)); %computed noise

LO = cos((2*pi*(fRF+K/2.* (t-tau_LORX) ).* (t-tau_LORX) + Phi_0 + Phi_1)) ...
    + 1i * sin((2*pi*(fRF+K/2.* (t-tau_LORX) ).* (t-tau_LORX) + Phi_0 + Phi_1 + IQ_phase_err));

for tau = tau_tunable_array

    f_beat = K*(tau_leak+tau);
    % RF down-conversion
    leakage_controlled_i = 1*A0*cos(   2*pi*(fRF+K/2.*(t-(tau_leak+tau))).*(t-(tau_leak+tau)) + Phi_0) + Noise_i;
    leakage_controlled_q = 1*A0*(IQ_mismatch)*sin(   2*pi*(fRF+K/2.*(t-(tau_leak+tau))).*(t-(tau_leak+tau)) + Phi_0) + Noise_q;

    if(Multipath == 1)
        f_beat_1 = K*(tau_leak_1+tau);
        leakage_controlled_i = leakage_controlled_i + A1*cos( ...
            2*pi*(fRF+K/2.*(t-(tau_leak_1+tau))).*(t-(tau_leak_1+tau)) + Phi_0);
        leakage_controlled_q = leakage_controlled_q + A1*sin( ...
            2*pi*(fRF+K/2.*(t-(tau_leak_1+tau))).*(t-(tau_leak_1+tau)) + Phi_0);
    end
    y = leakage_controlled_i .* real(LO) + leakage_controlled_q.*imag(LO) + DC_offset;

    % windowing
    % y = y.*window'; % cannot window it, weird

    yfft = fft(y)/length(y);
    yfft_db = mag2db(abs(yfft));


    yfft_1(fig_count)= yfft_db(2);
    del_0(fig_count) = yfft_db(2) - yfft_db(1);
    del_2(fig_count) = yfft_db(2) - yfft_db(3);
    if(averaging == 0)
        if(del_0(fig_count) > curr_max_del_0)
            curr_max_del_0 = del_0(fig_count);

        end
        if(del_2(fig_count) > curr_max_del_2)
            curr_max_del_2 = del_2(fig_count);
            curr_max_tau = tau;
        end

        if(del_0(fig_count) < curr_max_del_0 || del_2(fig_count) < curr_max_del_2)
            %fig_count
            % calculate the change of sharpness
            sharpness_change = curr_max_del_0-del_0(fig_count)+curr_max_del_2-del_2(fig_count);
            if(sharpness_change > 300)
                %curr_tau
                break;
            end
        end
    end

    curr_tau = tau;

    fig_count = fig_count +1;
end

if(averaging == 1)
    curr_max_del_0 = 0;
    curr_max_del_2 = 0;
    del_0_avg = del_0;
    del_2_avg = del_2; % copy
    for fig_count = 1+num_averaging: length(tau_tunable_array)-num_averaging
%         del_0_avg(fig_count) = sum(del_0(fig_count-num_averaging:fig_count+num_averaging))/(2*num_averaging+1);
%         del_2_avg(fig_count) = sum(del_2(fig_count-num_averaging:fig_count+num_averaging))/(2*num_averaging+1);
        del_0_avg(fig_count) = del_0(fig_count-num_averaging:fig_count+num_averaging) * avg_window;
        del_2_avg(fig_count) = del_2(fig_count-num_averaging:fig_count+num_averaging) * avg_window;

        if(del_0_avg(fig_count) > curr_max_del_0)
            curr_max_del_0 = del_0_avg(fig_count);
            curr_max_tau = tau_tunable_array(fig_count);
        end
        if(del_2_avg(fig_count) > curr_max_del_2)
            curr_max_del_2 = del_2_avg(fig_count);
%             curr_max_tau = tau_tunable_array(fig_count);
        end

        if(del_0_avg(fig_count) < curr_max_del_0 || del_2_avg(fig_count) < curr_max_del_2)
            %fig_count
            % calculate the change of sharpness
            sharpness_change = curr_max_del_0-del_0_avg(fig_count)+curr_max_del_2-del_2_avg(fig_count);
            if(sharpness_change > 300)
                %curr_tau
                break;
            end
        end
    end
    del_0 = del_0_avg;
    del_2 = del_2_avg; % replace
end

% actual phase of the leakage at RX mixer RF port - this is black-boxed to
% the system, the minus sign is because Rx lags behind LO by the tau
% leak_phase = rem(2*pi*(fRF+K/2*(-tau_leak-curr_max_tau))*(-tau_leak-curr_max_tau), 2*pi);
leak_phase = rem(2*pi*(tau_leak+curr_max_tau-tau_LORX)*(fRF-K/2*(tau_leak+curr_max_tau-tau_LORX)), 2*pi);
if(leak_phase < 0)
    leak_phase = leak_phase + 2*pi;
end


figure(fig_count)

leak_dist_det = (fRBW/K - curr_max_tau) * 3e8;

hold on
plot(tau_tunable_array,del_0);
plot(tau_tunable_array,del_2);

axis([tau_tunable_array(1) tau_tunable_array(end), -5 50])
hold off
legend('P(1)-P(0)','P(1)-P(2)');
ylabel('dB');
xlabel('{\tau}_{tunable}');
title({'Sharpness of the peak with {\tau}_{tunable} sweep', ...
    strcat('leakage path set to ',32,num2str(leak_dist*1000),'mm'),...
    strcat('leakage path detected is',32,num2str(leak_dist_det*1000),'mm.'),...
    strcat('number of iterations',32,num2str(fig_count-1))});

figure(fig_count + 1)
plot(tau_tunable_array,yfft_1);
ylabel('dB');
xlabel('{\tau}_{tunable}');
title('bin[1] power');


% now calculate the amplitude and phase of the controlled leakage
leakage_controlled_i = 1*A0*cos(   2*pi*(fRF+K/2.*(t-(tau_leak+curr_max_tau)))...
    .*(t-(tau_leak+curr_max_tau)) + Phi_0) + Noise_i;
leakage_controlled_q = 1*A0*(IQ_mismatch)*sin(   2*pi*(fRF+K/2.*(t-(tau_leak+curr_max_tau)))...
    .*(t-(tau_leak+curr_max_tau)) + Phi_0) + Noise_q;

if(Multipath == 1)
    leakage_controlled_i = leakage_controlled_i + A1*cos( ...
        2*pi*(fRF+K/2.*(t-(tau_leak_1+curr_max_tau))).*(t-(tau_leak_1+curr_max_tau)) + Phi_0);
    leakage_controlled_q = leakage_controlled_q + A1*sin( ...
        2*pi*(fRF+K/2.*(t-(tau_leak_1+curr_max_tau))).*(t-(tau_leak_1+curr_max_tau)) + Phi_0);
end
% LO = exp(1i*(2*pi*(fRF+K/2.* t     ).* t      + Phi_1));

y = leakage_controlled_i .* real(LO) + leakage_controlled_q.*imag(LO) + DC_offset;

% windowing
y = y.*window'; % cannot window it, weird
yfft = fft(y)/length(y);

% parameter estimation
A0_hat = abs(yfft(2))*2; % first bin
Phi_hat_0 = phase(yfft(2));

% Phi_hat_0 = 2*pi*fRF/K*fRBW;




%%

% generate a signal with leakage plus target
dist_tar = 0.2; % meter, hand is this far away
tau_tar = dist_tar * 2 /3e8;

%Ptx = 17; % transmitted power in dBm
Ap  = 7.3e-7; % Rx antenna aperture, assuming 3dBi gain
RCS_dB = -40; % dBsm
RCS = 10^(RCS_dB/10);

% amp of received signal
A1_dB = PTX_dBm + 10*log10(2*Ap*RCS/(4*pi)^2/dist_tar^4);
A1 = db2mag(A1_dB)*sqrt(2);

% book keeping
% the pure/untuned leakage has an un-controlled delay
leakage_uncontrolled_i = 1*A0*cos(   2*pi*(fRF+K/2.*(t-tau_leak)).*(t-tau_leak) + Phi_0) + Noise_i;
leakage_uncontrolled_q = 1*A0*(IQ_mismatch)*sin(   2*pi*(fRF+K/2.*(t-tau_leak)).*(t-tau_leak) + Phi_0) + Noise_q;


if(Multipath == 1)
    leakage_uncontrolled_i = leakage_uncontrolled_i + A1*cos( ...
        2*pi*(fRF+K/2.*(t-(tau_leak_1))).*(t-(tau_leak_1)) + Phi_0);
    leakage_uncontrolled_q = leakage_uncontrolled_q + A1*sin( ...
        2*pi*(fRF+K/2.*(t-(tau_leak_1))).*(t-(tau_leak_1)) + Phi_0);
end

% purely target
tar_only_uncontrolled_i = 1*A1*cos(   2*pi*(fRF+K/2.*(t-tau_tar)) ...
                        .*(t-tau_tar) + Phi_0);
tar_only_uncontrolled_q = 1*A1*(IQ_mismatch)*sin(2*pi*(fRF+K/2.*(t-tau_tar)) ...
                        .*(t-tau_tar) + Phi_0);

tar_only_controlled_i = 1*A1*cos(   2*pi*(fRF+K/2.*(t-tau_tar-curr_max_tau)) ...
                        .*(t-tau_tar-curr_max_tau) + Phi_0);
tar_only_controlled_q = 1*A1*(IQ_mismatch)*sin(2*pi*(fRF+K/2.*(t-tau_tar-curr_max_tau)) ...
                        .*(t-tau_tar-curr_max_tau) + Phi_0);

% received signal if leakage is not tuned
Rx_i_uncontrolled = leakage_uncontrolled_i + tar_only_uncontrolled_i + Noise_i;
Rx_q_uncontrolled = leakage_uncontrolled_q + tar_only_uncontrolled_q + Noise_q;

% received signal if leakage is tuned
Rx_i_controlled = leakage_controlled_i + tar_only_controlled_i + Noise_i;
Rx_q_controlled = leakage_controlled_q + tar_only_controlled_q + Noise_q;

%%
Phi_tunable_array = Phi_hat_0-pi : 0.01 : Phi_hat_0+pi;
BB_del_0 = zeros(1,length(Phi_tunable_array));
BB_del_2 = BB_del_0;
BB_fft_1 = BB_del_2; % bin[1] bookkeeping

curr_min_BB_del_0 = 0;
curr_min_BB_del_2 = 0;
curr_min_BB_Phi= 0;
curr_BB_Phi = Phi_tunable_array(1);

plot_count = 1;

% for Phi_hat = Phi_hat_0 - 0.2 : 0.04 : Phi_hat_0 + 0.2
% Leakage freq is already determined in previous step, now sweep to find
% best initial phase for the cancellation signal
for Phi_hat = Phi_tunable_array

    DAC_IF = 1*A0_hat*exp(1i*(2*pi*fRBW.*t + Phi_hat));

    y_cancel = DAC_IF .* LO;

    out_i = Rx_i_controlled - real(y_cancel);
    out_q = Rx_q_controlled - imag(y_cancel);


    % dechirp
    BB_out = out_i .* real(LO) + out_q.*imag(LO) + DC_offset;
    % BB_out = out_i .* real(LO) + DC_offset;

    % windowing
    BB_out = BB_out.*window'; % window it

    BB_fft = fft(BB_out)/length(BB_out);
    BB_fft_db = mag2db(abs(BB_fft));


    BB_del_0(plot_count) = BB_fft_db(2);% - BB_fft_db(1);
    BB_del_2(plot_count) = BB_fft_db(2);% - BB_fft_db(3);
    BB_fft_1(plot_count)= BB_fft_db(2);

    string_phi = strcat("Phi: ",num2str(Phi_hat),", BB_del_0: ",num2str(BB_del_0(plot_count)));
    disp(string_phi)

    if(BB_del_0(plot_count) < curr_min_BB_del_0)
        curr_min_BB_del_0 = BB_del_0(plot_count);
        curr_min_BB_Phi = Phi_hat;
    end

    if(BB_del_0(plot_count) > curr_min_BB_del_0 || BB_del_2(plot_count) > curr_min_BB_del_2)
        %fig_count
        % calculate the change of sharpness
        sharpness_change = curr_min_BB_del_0-BB_del_0(plot_count)...
            +curr_min_BB_del_2-BB_del_2(plot_count);
        if(sharpness_change < -300)
            %curr_tau
            break;
        end
    end

    curr_BB_Phi = Phi_hat;

    plot_count = plot_count + 1;
end


leak_phase_det = rem(curr_min_BB_Phi,2*pi);
if(leak_phase_det < 0)
    leak_phase_det = leak_phase_det + 2*pi;
end
figure(plot_count)
hold on
plot(Phi_tunable_array,BB_del_0);
plot(Phi_tunable_array,BB_del_2);

axis([Phi_tunable_array(1) Phi_tunable_array(end), -50 50])
hold off
legend('P(1)-P(0)','P(1)-P(2)');
ylabel('dB');
xlabel('{\Phi}_{tunable} rad');
title({'Sharpness of the peak with phase sweep', ...
    strcat('leakage phase offset actually set to ',32,num2str(leak_phase),'rad'),...
    strcat('leakage phase offset detected is',32,num2str(leak_phase_det),'rad.'),...
    strcat('number of iterations',32,num2str(plot_count-1))});

figure(plot_count + 1)
plot(Phi_tunable_array,BB_fft_1);
ylabel('dB');
xlabel('{\Phi}_{tunable} rad');
title('bin[1] power');

% kill the dominant one and keep working on the second one
if(Multipath == 1)
    curr_max_tau_0 = curr_max_tau;
    curr_max_del_0 = 0;
    curr_max_del_2 = 0;
    fig_count = 1;
    for tau = tau_tunable_array

        % A_i*cos⁡( 2π(f_RF+K/2 t-Kτ_i)t-2π (f_RF-K/2 τ_i)τ_i+φ(t-τ_i ))

        f_DAC = fRBW - K*tau; % derivation in word
        Phi_DAC = Phi_hat_0 + 2*pi*(fRF-K/2*tau)*tau; % derivation in word
        DAC_IF = 1*A0_hat*exp(1i*(2*pi*f_DAC.*t + Phi_DAC));

        y_cancel = DAC_IF .* LO;
        leakage_controlled_i = leakage_controlled_i + A1*cos( ...
            2*pi*(fRF+K/2.*(t-(tau_leak_1+curr_max_tau+tau))).*(t-(tau_leak_1+curr_max_tau+tau)) + Phi_0);
        leakage_controlled_q = leakage_controlled_q + A1*sin( ...
            2*pi*(fRF+K/2.*(t-(tau_leak_1+curr_max_tau+tau))).*(t-(tau_leak_1+curr_max_tau+tau)) + Phi_0);


        tar_only_controlled_i = 1*A1*cos(   2*pi*(fRF+K/2.*(t-tau_tar-curr_max_tau-tau)) ...
                        .*(t-tau_tar-curr_max_tau-tau) + Phi_0);
        tar_only_controlled_q = 1*A1*(IQ_mismatch)*sin(2*pi*(fRF+K/2.*(t-tau_tar-curr_max_tau-tau)) ...
                                .*(t-tau_tar-curr_max_tau-tau) + Phi_0);
        Rx_i_controlled = leakage_controlled_i + tar_only_controlled_i + Noise_i;
        Rx_q_controlled = leakage_controlled_q + tar_only_controlled_q + Noise_q;
        out_i = Rx_i_controlled - real(y_cancel);
        out_q = Rx_q_controlled - imag(y_cancel);
    %     out_i = 1*A0*cos(   2*pi*(fRF+K/2.*(t-tau_leak-curr_max_tau))...
    %     .*(t-tau_leak-curr_max_tau) + Phi_0 + Phi_hat) + Noise_i;
    %     out_q = 1*A0*(IQ_mismatch)*sin(   2*pi*(fRF+K/2.*(t-tau_leak-curr_max_tau))...
    %     .*(t-tau_leak-curr_max_tau) + Phi_0 + Phi_hat) + Noise_q;

        % dechirp
        BB_out = out_i .* real(LO) + out_q.*imag(LO) + DC_offset;

        % windowing
        % y = y.*window'; % cannot window it, weird
        yfft = fft(BB_out)/length(BB_out);
        yfft_db = mag2db(abs(yfft));


        yfft_1(fig_count)= yfft_db(3);
        del_0(fig_count) = yfft_db(3) - yfft_db(2);
        del_2(fig_count) = yfft_db(3) - yfft_db(4);

        if(del_0(fig_count) > curr_max_del_0)
            curr_max_del_0 = del_0(fig_count);

        end
        if(del_2(fig_count) > curr_max_del_2)
            curr_max_del_2 = del_2(fig_count);
            curr_max_tau_0 = tau;
        end

        if(del_0(fig_count) < curr_max_del_0 || del_2(fig_count) < curr_max_del_2)
            %fig_count
            % calculate the change of sharpness
            sharpness_change = curr_max_del_0-del_0(fig_count)+curr_max_del_2-del_2(fig_count);
            if(sharpness_change > 300)
                %curr_tau
                break;
            end
        end

        fig_count = fig_count + 1;

    end

    figure()

    leak_dist_det = (fRBW/K - curr_max_tau_0) * 3e8;

    hold on
    plot(tau_tunable_array,del_0);
    plot(tau_tunable_array,del_2);

    axis([tau_tunable_array(1) tau_tunable_array(end), -5 50])
    hold off
    legend('P(1)-P(0)','P(1)-P(2)');
    ylabel('dB');
    xlabel('{\tau}_{tunable}');
    title({'Sharpness of the peak with {\tau}_{tunable} sweep', ...
        strcat('leakage path set to ',32,num2str((leak_dist_1)*1000),'mm'),...
        strcat('leakage path detected is',32,num2str((dRBW+leak_dist_det)*1000),'mm.'),...
        strcat('number of iterations',32,num2str(fig_count-1))});

    figure(fig_count + 1)
    plot(tau_tunable_array,yfft_1);
    ylabel('dB');
    xlabel('{\tau}_{tunable}');
    title('bin[2] power');

    % now calculate the amplitude and phase of the controlled leakage
    f_DAC = fRBW - K*curr_max_tau_0; % derivation in word
    Phi_DAC = Phi_hat_0 + 2*pi*(fRF-K/2*curr_max_tau_0)*curr_max_tau_0; % derivation in word
    DAC_IF = 1*A0_hat*exp(1i*(2*pi*f_DAC.*t + Phi_DAC));

    y_cancel = DAC_IF .* LO;

    leakage_controlled_i = leakage_controlled_i + A1*cos( ...
        2*pi*(fRF+K/2.*(t-(tau_leak_1+curr_max_tau+curr_max_tau_0))).*(t-(tau_leak_1+curr_max_tau+curr_max_tau_0)) + Phi_0);
    leakage_controlled_q = leakage_controlled_q + A1*sin( ...
        2*pi*(fRF+K/2.*(t-(tau_leak_1+curr_max_tau+curr_max_tau_0))).*(t-(tau_leak_1+curr_max_tau+curr_max_tau_0)) + Phi_0);


    tar_only_controlled_i = 1*A1*cos(   2*pi*(fRF+K/2.*(t-tau_tar-curr_max_tau-curr_max_tau_0)) ...
                    .*(t-tau_tar-curr_max_tau-curr_max_tau_0) + Phi_0);
    tar_only_controlled_q = 1*A1*(IQ_mismatch)*sin(2*pi*(fRF+K/2.*(t-tau_tar-curr_max_tau-curr_max_tau_0)) ...
                            .*(t-tau_tar-curr_max_tau-curr_max_tau_0) + Phi_0);
    Rx_i_controlled = leakage_controlled_i + tar_only_controlled_i + Noise_i;
    Rx_q_controlled = leakage_controlled_q + tar_only_controlled_q + Noise_q;

    out_i = Rx_i_controlled - real(y_cancel);
    out_q = Rx_q_controlled - imag(y_cancel);
    %     out_i = 1*A0*cos(   2*pi*(fRF+K/2.*(t-tau_leak-curr_max_tau))...
    %     .*(t-tau_leak-curr_max_tau) + Phi_0 + Phi_hat) + Noise_i;
    %     out_q = 1*A0*(IQ_mismatch)*sin(   2*pi*(fRF+K/2.*(t-tau_leak-curr_max_tau))...
    %     .*(t-tau_leak-curr_max_tau) + Phi_0 + Phi_hat) + Noise_q;

    % dechirp
    BB_out = out_i .* real(LO) + out_q.*imag(LO) + DC_offset;
    % windowing
    y = BB_out.*window'; % cannot window it, weird
    yfft = fft(y)/length(y);

    % parameter estimation
    A1_hat = abs(yfft(3))*2; % second bin
    Phi_hat_1 = phase(yfft(3));

end

% generate cancellation signal
if(Multipath == 0)
    DAC_IF = 1*A0_hat*exp(1i*(2*pi*fRBW.*t + curr_min_BB_Phi));
else
    DAC_IF = 1*A0_hat*exp(1i*(2*pi*fRBW.*t + curr_min_BB_Phi)) ...
        + 1*A1_hat*exp(1i*(2*pi*(fRBW*2).*t + Phi_hat_1));
end
y_cancel = DAC_IF .* LO;

% cancellation amplitude error
amp_err = db2mag(-1);
out_i = Rx_i_controlled - amp_err*real(y_cancel);
out_q = Rx_q_controlled - amp_err*imag(y_cancel);

BB_before_controlled = real(Rx_i_controlled .* real(LO) + Rx_q_controlled.*imag(LO) + DC_offset);
BB_out = real(out_i .* real(LO) + out_q.*imag(LO) + DC_offset);

% plot the raw result
BB_raw_out = real(Rx_i_uncontrolled .* real(LO) + Rx_q_uncontrolled .* imag(LO));

% plot the leakage only
BB_leakage_out = real(leakage_uncontrolled_i .* real(LO) + leakage_uncontrolled_q .* imag(LO));

% plot shifted leakage
BB_leakage_controlled = real(leakage_controlled_i.* real(LO) + leakage_controlled_q.*imag(LO) + DC_offset);

% plot the target only
BB_target_out = real(tar_only_uncontrolled_i .* real(LO) + tar_only_uncontrolled_q .* imag(LO));

% windowing
BB_out_windowed = BB_out.*window'; % window it
BB_before_controlled_windowed = BB_before_controlled .* window';
BB_raw_out_windowed = BB_raw_out .* window';
BB_leakage_out_windowed = BB_leakage_out .* window';
BB_target_out_windowed = BB_target_out .* window';

BB_fft = fft(BB_out_windowed)/length(BB_out_windowed);
BB_fft_db = mag2db(abs(BB_fft));

BB_before_controlled_fft_db = mag2db(abs(fft(BB_before_controlled_windowed)/length(BB_before_controlled_windowed)));
BB_raw_fft_db = mag2db(abs(fft(BB_raw_out_windowed)/length(BB_raw_out_windowed)));
BB_leakage_out_db = mag2db(abs(fft(BB_leakage_out_windowed)/length(BB_leakage_out_windowed)));
BB_target_out_db = mag2db(abs(fft(BB_target_out_windowed)/length(BB_target_out_windowed)));


%%
figure(plot_count+2)
% plot(t,real(BB_out));
% axis([t(1) t(end), -2 2])
% ylabel('Magnitude');
% xlabel('t(s)')

% correct for the additional distance added, unit mm
correction_dist = curr_max_tau * 3e11 / 2;

hold on
% raw
stem((0:1:floor(length(BB_raw_fft_db)/2)-1)*fRBW*3e11/K/2,...
    BB_raw_fft_db(1: floor(length(BB_raw_fft_db)/2)),'Marker','square','BaseValue',-130,'LineWidth',2);

% canceled
stem((0:1:floor(length(BB_fft_db)/2)-1)*fRBW*3e11/K/2-correction_dist,...
    BB_fft_db(1: floor(length(BB_fft_db)/2)),'Marker','*','BaseValue',-130,'LineWidth',2);

% just leakage
plot((0:1:floor(length(BB_leakage_out_db)/2)-1)*fRBW*3e11/K/2,...
    BB_leakage_out_db(1: floor(length(BB_leakage_out_db)/2)),'LineWidth',2);

% just target
plot((0:1:floor(length(BB_leakage_out_db)/2)-1)*fRBW*3e11/K/2,...
    BB_target_out_db(1: floor(length(BB_target_out_db)/2)),'LineWidth',2);

hold off

for i = 0:floor(100)
    string_print = strcat(num2str(i*fRBW*3e11/K/2),...
        ',',num2str(BB_raw_fft_db(i+1)),...
        ',',num2str(BB_fft_db(i+1)),...
        ',',num2str(BB_leakage_out_db(i+1)),...
        ',',num2str(BB_target_out_db(i+1)));
    disp(string_print)
end

legend('before cancellation',"after cancellation","leakage-only","target-only");
axis([0 min((floor(length(BB_fft_db)/2)-1)*fRBW*3e11/K/2-correction_dist,1000) -140 0])
title(strcat("Target at ",num2str(dist_tar*100),"cm, Delay tuning step is ",num2str(delay_step*1e12)," ps"))
xlabel('Distance(mm)')
ylabel('dB');


% Real Time
figure(plot_count+3)
subplot(2,1,1)
hold on

% raw
plot(t, BB_raw_out,'LineWidth',2,'DisplayName','before cancellation');

% just leakage
plot(t, BB_leakage_out,'LineWidth',2,'DisplayName','leakage component');
hold off
legend
xlabel('Time(s)')
ylabel('Mag');
title(strcat("Signal without frequency offsetting"))

subplot(2,1,2)
hold on
yyaxis left
% shifted raw
plot(t, BB_before_controlled,'LineWidth',2,'DisplayName','shifted, before cancellation');

% shifted leakage
plot(t, BB_leakage_controlled,'LineWidth',2,'DisplayName','shifted, leakage component');

% DAC tone
plot(t, real(DAC_IF),'LineWidth',2,'DisplayName','DAC IF');

% cancelled
plot(t, BB_out,'LineWidth',2,'DisplayName','after cancellation');

% just target
yyaxis right
plot(t, BB_target_out,'LineWidth',2,'DisplayName','target-only');


hold off
% axis([0 max(t) -10 10])
legend
xlabel('Time(s)')
ylabel('Mag');
title(strcat("Signal with frequency offsetting"))


%  stem(0:1:100-1,BB_fft_db(1: 100),'BaseValue',-150);
%  ylabel('dB');
% title(strcat('{\Phi}_{hat} = ',num2str(curr_min_BB_Phi),'rad'));

%%
