%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                 Successive Approximation ADC                
%                            
%                 Chuyao Cheng and Yikuan Chen
%                           Nov 2019
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% SAR ADC model
classdef my_sar_adc
    properties
        % System Spec
        Vsupply;
        Vref;
        nbit;
        fsample;  %25MHz
        fsar; %300MHz
        LSB;
        Vcm;
        
        % sampling switch
        Ron = 711;
        
        % DAC Array
        Cp;
        Cn;
        Cgd;
        Cpar_p;  % To be determiend
        Cpar_n;
        Cp_tot;
        Cn_tot;
        Cp_tot_real;
        Cn_tot_real;
        Cp_real;
        Cn_real;
        I_tail;
        gm;
        Power_DAC;
              
        % Latch
        Av;
        Cpp;
        Vthn;
        C_load;
        Voffset;
        vn_stdev;
        kick_back;
        Power_latch;
        
        Power_tot;
    end
    
    methods
        function obj = my_sar_adc(Vsup, Vr,nb,fs)
            
            if(nargin ~= 4)
                display('Incorrect number of argument! Will use default values.')
                obj.Vsupply = 1.2;
                obj.Vref = 1.2;
                obj.nbit = 12;
                obj.fsample = 25e6;  %25MHz              
            else
                obj.Vsupply = Vsup;
                obj.Vref = Vr;
                obj.nbit = nb;
                obj.fsample = fs;  %25MHz  
            end
            
            obj.Cgd = 0.1e-15;
            obj.Cpar_p = 2.39e-15;  % To be determiend
            obj.Cpar_n = obj.Cpar_p;            
            obj.LSB= 2*obj.Vref / 2^obj.nbit;
            obj.Vcm = obj.Vref / 2;
            obj.fsar = obj.fsample * obj.nbit; %300MHz
            obj.Cpp = 40e-15;
            obj.Vthn = 0.5;
            obj.C_load = 1e-15;
            
            obj.Cp=zeros(1,obj.nbit);
            obj.Cn=zeros(1,obj.nbit);
            for i=1:obj.nbit-1
                obj.Cp(i)=2^(obj.nbit-i-1);
                obj.Cn(i)=2^(obj.nbit-i-1);
            end
            obj.Cp(obj.nbit) = 1;
            obj.Cn(obj.nbit) = 1;
            obj.Cp_tot = sum(obj.Cp) + obj.Cpar_p;
            obj.Cn_tot = sum(obj.Cn) + obj.Cpar_n;
            
            % capacitances and power
            [gm,Av,I_tail,Cp_tot_real,Voffset,vn_stdev] = set_nonidealities(obj);
            
            obj.gm = gm;
            obj.Av = Av;
            obj.I_tail = I_tail;
            obj.Voffset = Voffset;
            obj.vn_stdev = vn_stdev;
            obj.Cp_tot_real = Cp_tot_real;
            obj.Cn_tot_real = obj.Cp_tot_real;
            
            obj.Cp_real = obj.Cp * obj.Cp_tot_real/obj.Cp_tot;
            obj.Cn_real = obj.Cn * obj.Cn_tot_real/obj.Cn_tot;

            obj.kick_back = (obj.Cgd)/(obj.Cp_tot_real);

            obj.Power_latch = obj.fsar*(2*obj.Cpp+obj.C_load)*obj.Vsupply^2;
            obj.Power_DAC = obj.fsar*(obj.Cn_tot_real+obj.Cp_tot_real)*obj.Vsupply^2; % unit is Watt
            obj.Power_tot = obj.Power_latch + obj.Power_DAC;

            
        end
        
        function [gm,Av,I_tail,Cp_tot_real,Voffset,vn_stdev] = set_nonidealities(obj)
            T_settle = 1/obj.fsar/2;
            I_tail = 2*obj.Cpp*obj.Vthn/T_settle; % Unit:Amp
            gamma = 0.78;
            % From offset - Voffset less than 0.5 LSB
            Voffset_max = obj.Vref/(2^obj.nbit)/2;
            
            % Using Voffset = deltaCp/Cpp*I_tail/2/gm
            deltaCp = obj.Cpp*0.05; % tbd
            gm_min = deltaCp/obj.Cpp*I_tail/2/Voffset_max;
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
            vnsquare_max = 1/2*((obj.Vref^2/2)/10^((obj.nbit*6.02+1.67)/10))/4;
            display(vnsquare_max)
            Av_min = gm_min*obj.Vthn/(I_tail/2);

            gm_sweep = linspace(gm_min,gm_min*40,500);
            vnsq_sweep = (2*kT/obj.Cpp+2*(4*kT*gamma.*gm_sweep/obj.Cpp^2*T_settle))...
                ./((gm_sweep*obj.Vthn/(I_tail/2)).^2);

            figure(1)
            hold on
            plot(gm_sweep,vnsq_sweep,'b');
            plot(gm_sweep,vnsquare_max*ones(length(gm_sweep)),'c');
            hold off
            xlabel('gm({\Omega}^{-1})')
            ylabel('Input referred v_n^2 (V^2)')
            title('Sweeping Results of Input Referred Noise')

            % choose the gm, get Av and actual Voffset
            gm = gm_sweep(find(vnsq_sweep < vnsquare_max ,1 ));

            Av = gm*obj.Vthn/(I_tail/2);
            % verify that the settling has no problem for LSB input
            tau_u = obj.Cpp/gm;
            max_tau_u = T_settle/log(2^obj.nbit);
            
            if(tau_u <= max_tau_u)
                disp('Settling satisfied');
            else
                disp('Cannot satisfy settling, need larger gm')
                gm = obj.Cpp/max_tau_u;            
            end
            
            Voffset = deltaCp/obj.Cpp*I_tail/2/gm;
            vn_stdev = sqrt((2*kT/obj.Cpp+2*(4*kT*gamma*gm/obj.Cpp^2*T_settle))...
                /((gm*obj.Vthn/(I_tail/2))^2));
            display(gm)
            display(vn_stdev)
            Cp_tot_real = kT/vn_stdev^2;
            if(Cp_tot_real/(2^obj.nbit/2) < 2e-15)
                Cp_tot_real = 2^obj.nbit/2*2e-15;
            end
            % assume C_load is a FO1 inverter
            assert((Av >= Av_min));       
                  
        end
        
        function Y = run_adc(obj,t,x)
            kT = 4.11e-21;
           % Run ADC
            output = zeros(1,length(x));
            Vin = 0;
            history = 0;
            % iterate over all samples
            for j = 1:length(t)
                Vin = x(j);
                % sampling input
                out = zeros(1, obj.nbit);
                top = ones(obj.nbit, 1);
                bottom = ones(obj.nbit, 1);
                Vinp = obj.Vcm + 0.5*Vin;
                Vinn = obj.Vcm - 0.5*Vin;

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
                for i=2:obj.nbit
                    % input referred noise additive
                    vnp =randn()*kT/obj.Cp_tot_real + randn()*obj.vn_stdev + history*obj.kick_back*obj.Vref;
                    vnn =randn()*kT/obj.Cn_tot_real + randn()*obj.vn_stdev - history*obj.kick_back*obj.Vref;
                    Vxp = (obj.Cp_real * top * obj.Vref - obj.Vref * obj.Cp_tot_real ...
                        + Vinp * obj.Cp_tot_real) / obj.Cp_tot_real + vnp;
                    Vxn = (obj.Cn_real * bottom * obj.Vref - obj.Vref * obj.Cn_tot_real ...
                        + Vinn * obj.Cn_tot_real) / obj.Cn_tot_real +vnn;

                    if ((Vxp+obj.Voffset) >= Vxn)
                        out(i) = 1;
                        history = 1;
                        top(i) = 0;
                    elseif ((Vxp+obj.Voffset) < Vxn)
                        out(i) = 0;
                        history = -1;
                        bottom(i) = 0;
                    else
                        if(rand()>0.5)  
                            out(i) = 1;
                            history = 1;
                            top(i) = 0;       
                        else
                            out(i) = 0;
                            history = -1;
                            bottom(i) = 0;
                        end
                    end
                end
                val = 0;
                
                % convert from binary to decimal
                for i=1:obj.nbit
                    val = val * 2 + out(i);
                end
                val = (val * 2 * obj.Vref / 2^obj.nbit) - obj.Vref;                
                output(j) = val;

            end
            
            % x = Input_coeff*Vref*sin(2*pi*fin*t);
            t2 = t*obj.fsample;

            Y = output(int32(t2+1));
  

        end
        
    end
end

