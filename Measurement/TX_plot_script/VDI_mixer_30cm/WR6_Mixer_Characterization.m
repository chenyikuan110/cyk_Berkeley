% close all; clear all; clc;

debug=1;


d=0.3;
freq_min=110;
freq_max=170;

my_dir="C:\Users\Hesham\Desktop\My Drive\My Work\Berkeley\Group\measured_data\Charm\2024_7\";
my_subdir="VDI_mixer_30cm\";

% lo_freq=[130 135 140];
lo_freq=[130 135 140];
lo_freq=[135];
freq_rec_power=[];
rec_power=[];
fig_legend=[];


for index=lo_freq
        file=sprintf('%s%sRX_IF_LI_%d.csv',my_dir,my_subdir,index);
        tmp_lo=table2array(readtable(file))';
        file=sprintf('%s%sRX_IF_HI_%d.csv',my_dir,my_subdir,index);
        tmp_hi=table2array(readtable(file))';

        freq_rec_power=[freq_rec_power ; ([-1*flip(tmp_lo(1,1:1:end)) tmp_hi(1,1:1:end)]+index)];
        rec_power=[rec_power ; [flip(tmp_lo(2,1:1:end)) tmp_hi(2,1:1:end)]];
end

file=sprintf('%s%sextender_power.xlsx',my_dir,my_subdir);
tmp=table2array(readtable(file))';
freq_ref_power_course=tmp(1,:);
ref_power_course = tmp(2,:);

file=sprintf('%s%sOE_gain.csv',my_dir,my_subdir);
tmp=table2array(readtable(file))';
freq_oe_gain=tmp(1,:);
oe_gain_smooth = tmp(2,:);
oe_gain_actual = tmp(3,:);

file=sprintf('%s%shorn_gain.csv',my_dir,my_subdir);
tmp=table2array(readtable(file))';
freq_horn_gain=tmp(1,:);
horn_gain_smooth = tmp(2,:);
horn_gain_actual = tmp(3,:);

figure(1);
hold on

figure(2);
hold on

figure(3);
hold on

for index=1:length(lo_freq)

    freq = max(freq_min,freq_rec_power(index,1)):0.25:min(freq_max,freq_rec_power(index,end));

    fspl = -20*log10(d*freq*10*4*pi/3);
    ref_power = interp1(freq_ref_power_course,ref_power_course,freq,'makima');
    oe_gain = interp1(freq_oe_gain,oe_gain_actual,freq,'makima');
    horn_gain = interp1(freq_horn_gain,horn_gain_actual,freq,'makima');
    rec_power_interp = interp1(freq_rec_power(index,:),rec_power(index,:),freq,'makima');

    rec_gain = rec_power_interp-(ref_power+oe_gain);
    rec_gain = movmean(rec_gain,3);
    figure(1)
    plot(freq,rec_gain)

    rec_gain = rec_power_interp-(ref_power+oe_gain+fspl);
    rec_gain = movmean(rec_gain,3);
    figure(2)
    plot(freq,rec_gain)

    rec_gain = rec_power_interp-(ref_power+oe_gain+horn_gain+fspl);
    rec_gain = movmean(rec_gain,3);
    figure(3)
    plot(freq,rec_gain)

    fig_legend=[fig_legend; sprintf('LO=%dGHz',lo_freq(index))];
end


figure(1);
xlabel('Freq [GHz]');
ylabel('Conversion Gain [dB]');
pbaspect([2 2 1])
grid on
xlim([110 160]);
ylim([-70 -50]);
xticks(110:10:160);
% yticks(0:4:20);
legend(fig_legend,'fontsize',12,'location','southwest');
title('Ref. 1: 30cm Range');

figure(2);
xlabel('Freq [GHz]');
ylabel('Conversion Gain [dB]');
pbaspect([2 2 1])
grid on
xlim([110 160]);
ylim([-5 15]);
xticks(110:10:160);
% yticks(0:4:20);
legend(fig_legend,'fontsize',12,'location','southwest');
title('Ref. 2: Antenna Input');

figure(3);
xlabel('Freq [GHz]');
ylabel('Conversion Gain [dB]');
pbaspect([2 2 1])
grid on
xlim([110 160]);
ylim([-25 -5]);
xticks(110:10:160);
% yticks(0:4:20);
legend(fig_legend,'fontsize',12,'location','southwest');
title('Ref. 3: Mixer Input');

clc;
